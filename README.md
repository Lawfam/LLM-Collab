Multi-LLM API Integration Project - Version 1
This project integrates multiple LLM (Large Language Model) APIs, enabling dynamic switching between them for optimized task performance. It allows users to automate coding, research, predictions, and strategy generation by leveraging different LLMs such as Ollama, OpenAI, Anthropic, Groq, and Google Gemini.

Note: Perplexity is currently non-functional, and this is the first version of the project. We welcome contributions to add features and improve the codebase!

Features
Dynamic API Switching: Supports integration with multiple LLM APIs. You can switch between LLMs based on the specific task at hand.
Real-Time Data Visualization: Modern UI built with PyQt5 for displaying charts, progress bars, and other interactive elements.
Task Automation: Automates a wide range of tasks, from coding to scientific research and strategy generation.
Modular Design: Each component of the project is independent, ensuring easy addition of features or modification without breaking the entire system.
APIs Integrated
Ollama
OpenAI
Anthropic
Google Gemini
Groq
Perplexity is currently non-functional and under development.

Tech Stack
PyQt5: For building the user interface and real-time charts.
Torch: For AI model execution.
Requests: For API communication.
Logging: Managed by Loguru.
SimpleJson & JsonLib: For data handling.
Requirements
The project uses a set of Python libraries as listed in the requirements.txt file. You can install these dependencies using the following command:

bash
Copy code
pip install -r requirements.txt
The major libraries include:

PyQt5 (for UI)
Requests (for API communication)
Torch (for AI model execution)
Loguru (for logging)
Python-dotenv (for environment management)
Full list of dependencies can be found in the requirements.txt file.

Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/multi-llm-api-integration.git
Navigate to the project directory:

bash
Copy code
cd multi-llm-api-integration
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Set up your API keys and endpoints by creating a .env file in the root directory, with the following content:

bash
Copy code
API_KEYS={
    "groq": "<groq_api_key>",
    "anthropic": "<anthropic_api_key>",
    "openai": "<openai_api_key>",
    "gemini": "<gemini_api_key>",
    "ollama_ip": "ip-add:11434"
}

API_URLS={
    "groq_llm": "https://api.groq.com/openai/v1/chat/completions",
    "ollama_llm": "ip address:11434/api/generate",
    "openai_llm": "https://api.openai.com/v1/chat/completions",
    "gemini_llm": "https://generativelanguage.googleapis.com/v1/models"
}
Run the application:

bash
Copy code
python main.py
How to Contribute
Fork the repository.
Create a new branch for your feature (git checkout -b feature/feature-name).
Commit your changes (git commit -m 'Add some feature').
Push to the branch (git push origin feature/feature-name).
Open a pull request to discuss your changes.
Future Enhancements
Fixing Perplexity Integration: Resolve the issues with the Perplexity API.
Improving UI: Adding more visualization elements and customization options.
Additional Features: Automating new tasks like sentiment analysis, detailed data visualizations, and more.
Acknowledgements
This project is inspired by the need to leverage multiple AI models for various tasks, combining the strengths of each model.
Contributions are welcomed from developers, AI enthusiasts, and anyone looking to collaborate on multi-LLM projects.
