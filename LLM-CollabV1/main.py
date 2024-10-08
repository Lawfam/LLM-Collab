import sys
import json
import threading
import time
import torch
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QMessageBox
from PyQt5.QtGui import QIcon, QFont, QFontDatabase
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QTimer, QSize
from ui import ChatBox, ControlPanel, CollaborationSettingsDialog, Theme
from models import ModelInteractions

class MainWindow(QMainWindow):
    update_chat_signal = pyqtSignal(str, bool)
    stream_update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced LLM Collaboration App")
        self.setGeometry(100, 100, 1200, 800)

        with open('config.json') as config_file:
            self.config = json.load(config_file)

        self.model_interactions = ModelInteractions(self.config)

        self.current_theme = Theme.DARK

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.chat_box = ChatBox(self)
        self.control_panel = ControlPanel(self)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.chat_box)
        splitter.addWidget(self.control_panel)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

        self.current_mode = "single"
        self.stop_event = threading.Event()
        self.collaboration_models = []
        self.conversation_history = []

        self.collab_settings = {
            "rounds": 0,
            "max_tokens": 1000,
            "temperature": 0.7,
            "model1_role": "General Assistant",
            "model2_role": "Technical Expert"
        }

        self.create_toolbar()
        self.apply_theme(self.current_theme)
        self.fetch_all_models()

        self.statusBar().showMessage("Ready")

        self.update_chat_signal.connect(self.chat_box.display_message)
        self.stream_update_signal.connect(self.chat_box.update_streaming_message)

    def create_toolbar(self):
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))

        start_action = toolbar.addAction(QIcon("icons/start.png"), "Start")
        start_action.triggered.connect(self.start_collaboration)

        stop_action = toolbar.addAction(QIcon("icons/stop.png"), "Stop")
        stop_action.triggered.connect(self.stop_chat)

        clear_action = toolbar.addAction(QIcon("icons/clear.png"), "Clear")
        clear_action.triggered.connect(self.clear_chat)

        settings_action = toolbar.addAction(QIcon("icons/settings.png"), "Settings")
        settings_action.triggered.connect(self.show_collaboration_settings)

    def apply_theme(self, theme):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {theme['bg']};
                color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['button']};
                color: {theme['text']};
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {theme['input']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                padding: 3px;
                border-radius: 3px;
            }}
            QScrollBar:vertical {{
                background: {theme['scroll_bg']};
                width: 12px;
                margin: 22px 0 22px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {theme['scroll_handle']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical {{
                background: {theme['scroll_bg']};
                height: 20px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}
            QScrollBar::sub-line:vertical {{
                background: {theme['scroll_bg']};
                height: 20px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}
        """)

    def fetch_all_models(self):
        try:
            groq_models = self.model_interactions.fetch_groq_models()
            ollama_models = self.model_interactions.fetch_ollama_models()
            anthropic_models = self.model_interactions.fetch_anthropic_models()
            openai_models = self.model_interactions.fetch_openai_models()
            gemini_models = self.model_interactions.fetch_gemini_models()
            perplexity_models = self.model_interactions.fetch_perplexity_models()
        except Exception as e:
            self.show_error_message(f"Error fetching models: {str(e)}")
            return

        combined_models = (
            ["Groq: " + model for model in groq_models] +
            ["Ollama: " + model for model in ollama_models] +
            ["Anthropic: " + model for model in anthropic_models] +
            ["OpenAI: " + model for model in openai_models] +
            ["Gemini: " + model for model in gemini_models] +
            ["Perplexity: " + model for model in perplexity_models]
        )

        self.control_panel.single_model_dropdown.addItems(combined_models)
        self.control_panel.model1_dropdown.addItems(combined_models)
        self.control_panel.model2_dropdown.addItems(combined_models)

        if combined_models:
            self.control_panel.single_model_dropdown.setCurrentIndex(0)
            self.control_panel.model1_dropdown.setCurrentIndex(0)
            self.control_panel.model2_dropdown.setCurrentIndex(1 if len(combined_models) > 1 else 0)

    @pyqtSlot()
    def handle_message(self, message):
        self.chat_box.display_message(f"You: {message}", is_user=True)

        if self.current_mode == "collaboration" and self.collaboration_models:
            threading.Thread(target=self.collaborative_interaction, args=(message,), daemon=True).start()
        else:
            selected_model = self.control_panel.single_model_dropdown.currentText()
            selected_role = self.control_panel.role_dropdown.currentText()
            threading.Thread(target=self.single_model_response, args=(selected_model, selected_role, message), daemon=True).start()

    def single_model_response(self, model, role, user_message):
        if not self.stop_event.is_set():
            role_prompt = {
                "General Assistant": "You are a helpful assistant. 😊",
                "Technical Expert": "You are an expert in technology. 🛠️",
                "Creative Thinker": "You are a creative thinker. ✍️",
                "Data Analyst": "You are a data analyst. 📊",
                "Healthcare Advisor": "You are a healthcare advisor. 🏥",
                "Educational Tutor": "You are an educational tutor. 📚",
                "Scientific Researcher": "You are a scientific researcher. 🧪",
                "Project Manager": "You are a project manager. 📋",
                "Philosopher": "You are a philosopher. 🤔",
                "Debater": "You are a skilled debater. 💬"
            }.get(role, "You are a general assistant. 😊")

            full_prompt = f"{role_prompt}\n{user_message}"

            try:
                start_time = time.time()
                self.stream_update_signal.emit(f"\n{model}: ")
                for chunk in self.model_interactions.get_model_response_stream(model, full_prompt,
                                                   max_tokens=self.collab_settings["max_tokens"],
                                                   temperature=self.collab_settings["temperature"]):
                    if self.stop_event.is_set():
                        break
                    self.stream_update_signal.emit(chunk)
                end_time = time.time()
                response_time = end_time - start_time

                self.control_panel.visualization.update_chart({model: [response_time]})
            except Exception as e:
                self.show_error_message(f"Error getting model response: {str(e)}")

    @pyqtSlot()
    def start_collaboration(self):
        model1 = self.control_panel.model1_dropdown.currentText()
        model2 = self.control_panel.model2_dropdown.currentText()
        self.collaboration_models = [model1, model2]
        self.conversation_history = []

        system_prompt = "You are part of a collaborative AI system. Engage in a conversation, building upon each other's ideas."

        self.update_chat_signal.emit(f"Starting collaboration between models with prompt: {system_prompt}", False)
        threading.Thread(target=self.collaborative_interaction, args=(system_prompt,), daemon=True).start()

    def collaborative_interaction(self, system_prompt):
        model1_role = self.control_panel.model1_role_dropdown.currentText()
        model2_role = self.control_panel.model2_role_dropdown.currentText()

        self.conversation_history.append({"role": "system", "content": system_prompt})

        model1 = self.collaboration_models[0]
        model2 = self.collaboration_models[1]

        response_times = {model1: [], model2: []}
        rounds = self.collab_settings["rounds"]
        current_model = model1
        round_num = 0

        while rounds == 0 or round_num < rounds:
            if self.stop_event.is_set():
                break

            prompt = "\n".join([msg["content"] for msg in self.conversation_history])
            if current_model == model1:
                prompt = f"Role: {model1_role}. {prompt}"
            else:
                prompt = f"Role: {model2_role}. {prompt}"

            try:
                start_time = time.time()
                self.stream_update_signal.emit(f"\n{current_model}: ")
                full_response = ""
                for chunk in self.model_interactions.get_model_response_stream(current_model, prompt,
                                                   max_tokens=self.collab_settings["max_tokens"],
                                                   temperature=self.collab_settings["temperature"]):
                    if self.stop_event.is_set():
                        break
                    self.stream_update_signal.emit(chunk)
                    full_response += chunk
                end_time = time.time()
                response_time = end_time - start_time

                response_times[current_model].append(response_time)
                self.conversation_history.append({"role": "assistant", "content": full_response})

                current_model = model2 if current_model == model1 else model1
                round_num += 1
            except Exception as e:
                self.show_error_message(f"Error during collaborative interaction: {str(e)}")
                break

        self.control_panel.visualization.update_chart(response_times)

    @pyqtSlot()
    def stop_chat(self):
        self.stop_event.set()
        self.update_chat_signal.emit("Chat stopped by user.", False)
        QTimer.singleShot(2000, lambda: self.statusBar().showMessage("Idle"))

    @pyqtSlot()
    def clear_chat(self):
        self.chat_box.clear_chat()
        self.conversation_history = []

    def show_collaboration_settings(self):
        dialog = CollaborationSettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.collab_settings = dialog.get_settings()

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def show_error_message(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    font_id = QFontDatabase.addApplicationFont("path/to/Roboto-Regular.ttf")
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 10))
    else:
        print("Error loading Roboto font. Using system default.")

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())