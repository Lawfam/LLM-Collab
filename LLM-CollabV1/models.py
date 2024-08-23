import requests
import json
import anthropic
import openai
import google.generativeai as genai
from google.auth import credentials
from google.oauth2 import service_account

class ModelInteractions:
    def __init__(self, config):
        self.config = config
        self.anthropic_client = anthropic.Client(api_key=config['API_KEYS']['anthropic'])
        if hasattr(openai, 'Client'):
            self.openai_client = openai.Client(api_key=config['API_KEYS']['openai'])
        else:
            openai.api_key = config['API_KEYS']['openai']
            self.openai_client = openai
        
        # Initialize Gemini client
        genai.configure(api_key=config['API_KEYS']['gemini'])
        self.gemini_client = genai

    def fetch_groq_models(self):
        response = requests.get(self.config['API_URLS']['groq_models'], headers=self.config['HEADERS']['groq'])
        response.raise_for_status()
        models_data = response.json()
        return [model.get("id", "Unknown") for model in models_data.get("data", [])]

    def fetch_ollama_models(self):
        response = requests.get(self.config['API_URLS']['ollama_models'])
        response.raise_for_status()
        data = response.json()
        return [model['name'] for model in data.get('models', [])]

    def fetch_anthropic_models(self):
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-3-5-sonnet-20240620",
            "claude-instant-1.2"
        ]

    def fetch_openai_models(self):
        if hasattr(self.openai_client, 'models'):
            models = self.openai_client.models.list()
            return [model.id for model in models.data if "gpt" in model.id.lower()]
        else:
            models = self.openai_client.Model.list()
            return [model.id for model in models['data'] if "gpt" in model.id.lower()]

    def fetch_gemini_models(self):
        return [model['id'] for model in self.config['GEMINI_MODELS']]

    def fetch_perplexity_models(self):
        # Perplexity API doesn't have a specific endpoint for listing models
        # We'll return a predefined list of supported models
        return [
            "sonar-small-online",
            "sonar-small-chat",
            "sonar-medium-online",
            "sonar-medium-chat",
            "codellama-34b-instruct",
            "mistral-7b-instruct",
            "llama-2-70b-chat",
            "mixtral-8x7b-instruct"
        ]

    def get_groq_response_stream(self, model, prompt, max_tokens, temperature):
        response = requests.post(
            self.config['API_URLS']['groq_llm'],
            headers=self.config['HEADERS']['groq'],
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True
            },
            stream=True
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8').split('data: ')[1])
                if 'choices' in data and len(data['choices']) > 0:
                    chunk = data['choices'][0]['delta'].get('content', '')
                    if chunk:
                        yield chunk

    def get_ollama_response_stream(self, model, prompt, max_tokens, temperature):
        response = requests.post(
            self.config['API_URLS']['ollama_llm'],
            json={
                'model': model,
                'prompt': prompt,
                'options': {
                    'num_predict': max_tokens,
                    'temperature': temperature
                },
                'stream': True
            },
            stream=True
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    json_line = json.loads(line)
                    if 'response' in json_line:
                        yield json_line['response']
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {line}")

    def get_anthropic_response_stream(self, model, prompt, max_tokens, temperature):
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in response:
            if chunk.type == 'text_delta':
                yield chunk.text

    def get_openai_response_stream(self, model, prompt, max_tokens, temperature):
        if hasattr(self.openai_client, 'chat'):
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        else:
            response = self.openai_client.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            for chunk in response:
                if chunk['choices'][0]['delta'].get('content'):
                    yield chunk['choices'][0]['delta']['content']

    def get_gemini_response_stream(self, model, prompt, max_tokens, temperature):
        gemini_model = self.gemini_client.GenerativeModel(model_name=model)
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            ),
            stream=True
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def get_perplexity_response_stream(self, model, prompt, max_tokens, temperature):
        headers = {
            "Authorization": f"Bearer {self.config['API_KEYS']['perplexity']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        response = requests.post(
            f"{self.config['API_URLS']['perplexity']}/chat/completions",
            headers=headers,
            json=data,
            stream=True
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8').split('data: ')[1])
                    if 'choices' in data and len(data['choices']) > 0:
                        chunk = data['choices'][0]['delta'].get('content', '')
                        if chunk:
                            yield chunk
                except json.JSONDecodeError:
                    continue

    def get_model_response_stream(self, model, prompt, max_tokens=1000, temperature=0.7):
        if model.startswith("Groq: "):
            yield from self.get_groq_response_stream(model.replace("Groq: ", ""), prompt, max_tokens, temperature)
        elif model.startswith("Ollama: "):
            yield from self.get_ollama_response_stream(model.replace("Ollama: ", ""), prompt, max_tokens, temperature)
        elif model.startswith("Anthropic: "):
            yield from self.get_anthropic_response_stream(model.replace("Anthropic: ", ""), prompt, max_tokens, temperature)
        elif model.startswith("OpenAI: "):
            yield from self.get_openai_response_stream(model.replace("OpenAI: ", ""), prompt, max_tokens, temperature)
        elif model.startswith("Gemini: "):
            yield from self.get_gemini_response_stream(model.replace("Gemini: ", ""), prompt, max_tokens, temperature)
        elif model.startswith("Perplexity: "):
            yield from self.get_perplexity_response_stream(model.replace("Perplexity: ", ""), prompt, max_tokens, temperature)
        else:
            yield "Invalid model selected."