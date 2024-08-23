from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QLabel, QSplitter, QTabWidget, QDialog, QDialogButtonBox, QToolBar, QAction, QSpinBox
)
from PyQt5.QtGui import QColor, QIcon, QTextCursor, QFont, QFontDatabase, QTextCharFormat, QPainter, QSyntaxHighlighter
from PyQt5.QtCore import Qt, pyqtSlot, Q_ARG, QMetaObject, pyqtSignal, QTimer, QSize
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis, QLineSeries
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from bs4 import BeautifulSoup

class Theme:
    DARK = {
        'bg': '#1a1a1a',
        'text': '#e0e0e0',
        'button': '#2c2c2c',
        'button_hover': '#3d3d3d',
        'input': '#1f1f1f',
        'border': '#555555',
        'scroll_bg': '#2c2c2c',
        'scroll_handle': '#555555'
    }

class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.formatter = HtmlFormatter()

    def highlightBlock(self, text):
        highlighted = highlight(text, PythonLexer(), self.formatter)
        soup = BeautifulSoup(highlighted, 'html.parser')

        format_dict = {
            'k': QColor('#c678dd'),  # Keyword
            's': QColor('#98c379'),  # String
            'c': QColor('#5c6370'),  # Comment
            'n': QColor('#e5c07b'),  # Name
            'o': QColor('#d19a66'),  # Operator
            'p': QColor('#abb2bf'),  # Punctuation
        }

        self.setFormat(0, len(text), QTextCharFormat())  # Reset format

        pos = 0
        for tag in soup.find_all(['span']):
            class_name = tag.get('class', [None])[0]
            if class_name in format_dict:
                color = format_dict[class_name]
                char_format = QTextCharFormat()
                char_format.setForeground(color)
                start = text.find(tag.get_text(), pos)
                end = start + len(tag.get_text())
                self.setFormat(start, end - start, char_format)
                pos = end

class Role:
    ROLES = [
        "General Assistant",
        "Technical Expert",
        "Creative Thinker",
        "Data Analyst",
        "Healthcare Advisor",
        "Educational Tutor",
        "Scientific Researcher",
        "Project Manager",
        "Philosopher",
        "Debater"
    ]

class CollaborationSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Collaboration Settings")
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.rounds_label = QLabel("Number of Interaction Rounds (0 for infinite):")
        self.rounds_input = QSpinBox()
        self.rounds_input.setRange(0, 10000)
        layout.addWidget(self.rounds_label)
        layout.addWidget(self.rounds_input)

        self.max_tokens_label = QLabel("Max Tokens per Response:")
        self.max_tokens_input = QLineEdit()
        self.max_tokens_input.setText("1000")
        layout.addWidget(self.max_tokens_label)
        layout.addWidget(self.max_tokens_input)

        self.temperature_label = QLabel("Temperature (0.0 - 1.0):")
        self.temperature_input = QLineEdit()
        self.temperature_input.setText("0.7")
        layout.addWidget(self.temperature_label)
        layout.addWidget(self.temperature_input)

        self.model1_role_label = QLabel("Role for Model 1:")
        self.model1_role_dropdown = ModernComboBox()
        self.model1_role_dropdown.addItems(Role.ROLES)
        layout.addWidget(self.model1_role_label)
        layout.addWidget(self.model1_role_dropdown)

        self.model2_role_label = QLabel("Role for Model 2:")
        self.model2_role_dropdown = ModernComboBox()
        self.model2_role_dropdown.addItems(Role.ROLES)
        layout.addWidget(self.model2_role_label)
        layout.addWidget(self.model2_role_dropdown)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_settings(self):
        return {
            "rounds": int(self.rounds_input.value()),
            "max_tokens": int(self.max_tokens_input.text()),
            "temperature": float(self.temperature_input.text()),
            "model1_role": self.model1_role_dropdown.currentText(),
            "model2_role": self.model2_role_dropdown.currentText()
        }

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Roboto", 10))
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2c2c2c;
                color: #e0e0e0;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #5a5a5a;
            }
        """)

class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Roboto", 10))
        self.setStyleSheet("""
            QComboBox {
                background-color: #2c2c2c;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                padding: 5px;
                border-radius: 5px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #3d3d3d;
                border-left-style: solid;
            }
            QComboBox QAbstractItemView {
                background-color: #2c2c2c;
                color: #e0e0e0;
                selection-background-color: #3d3d3d;
            }
        """)

class ControlPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        self.mode_tabs = QTabWidget()
        self.mode_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background: #1a1a1a;
            }
            QTabBar::tab {
                background: #2c2c2c;
                color: #e0e0e0;
                padding: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3d3d3d;
            }
        """)
        layout.addWidget(self.mode_tabs)

        self.init_single_model_tab()
        self.init_collab_tab()

        self.visualization = VisualizationWidget()
        layout.addWidget(self.visualization)

        self.init_control_buttons(layout)

        self.mode_tabs.currentChanged.connect(self.toggle_mode)
        self.start_collab_button.clicked.connect(self.main_window.start_collaboration)
        self.stop_button.clicked.connect(self.main_window.stop_chat)
        self.clear_chat_button.clicked.connect(self.main_window.clear_chat)
        self.collab_settings_button.clicked.connect(self.main_window.show_collaboration_settings)

    def init_single_model_tab(self):
        single_model_widget = QWidget()
        single_model_layout = QVBoxLayout(single_model_widget)
        single_model_layout.addWidget(QLabel("Select Model:"))
        self.single_model_dropdown = ModernComboBox()
        single_model_layout.addWidget(self.single_model_dropdown)

        single_model_layout.addWidget(QLabel("Role for the model:"))
        self.role_dropdown = ModernComboBox()
        self.role_dropdown.addItems(Role.ROLES)
        single_model_layout.addWidget(self.role_dropdown)

        self.mode_tabs.addTab(single_model_widget, "Single Model")

    def init_collab_tab(self):
        collab_widget = QWidget()
        collab_layout = QVBoxLayout(collab_widget)

        collab_layout.addWidget(QLabel("Model 1:"))
        self.model1_dropdown = ModernComboBox()
        collab_layout.addWidget(self.model1_dropdown)

        collab_layout.addWidget(QLabel("Model 1 Role:"))
        self.model1_role_dropdown = ModernComboBox()
        self.model1_role_dropdown.addItems(Role.ROLES)
        collab_layout.addWidget(self.model1_role_dropdown)

        collab_layout.addWidget(QLabel("Model 2:"))
        self.model2_dropdown = ModernComboBox()
        collab_layout.addWidget(self.model2_dropdown)

        collab_layout.addWidget(QLabel("Model 2 Role:"))
        self.model2_role_dropdown = ModernComboBox()
        self.model2_role_dropdown.addItems(Role.ROLES)
        collab_layout.addWidget(self.model2_role_dropdown)

        self.start_collab_button = ModernButton("Start Collaboration")
        collab_layout.addWidget(self.start_collab_button)
        self.collab_settings_button = ModernButton("Collaboration Settings")
        collab_layout.addWidget(self.collab_settings_button)

        self.mode_tabs.addTab(collab_widget, "Collaboration")

    def init_control_buttons(self, layout):
        control_buttons_layout = QHBoxLayout()
        self.stop_button = ModernButton("Stop")
        self.clear_chat_button = ModernButton("Clear Chat")
        control_buttons_layout.addWidget(self.stop_button)
        control_buttons_layout.addWidget(self.clear_chat_button)
        layout.addLayout(control_buttons_layout)

    def toggle_mode(self, index):
        self.main_window.current_mode = "collaboration" if index == 1 else "single"

class ChatBox(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.current_stream_message = ""

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Roboto", 11))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: none;
                padding: 10px;
            }
        """)
        self.highlighter = CodeHighlighter(self.chat_display.document())
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.setFont(QFont("Roboto", 11))
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color: #2c2c2c;
                color: #e0e0e0;
                border: 1px solid #3d3d3d;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        self.send_button = ModernButton("Send")
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.send_button.clicked.connect(self.send_message)
        self.chat_input.returnPressed.connect(self.send_message)

    def send_message(self):
        message = self.chat_input.text().strip()
        if message:
            self.main_window.handle_message(message)
            self.chat_input.clear()

    def display_message(self, message, is_user=False):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        format = QTextCharFormat()
        if is_user:
            format.setForeground(QColor("#4a9de7"))
            cursor.insertText("You: ", format)
        else:
            if ":" in message:
                model_name, content = message.split(":", 1)
                format.setForeground(QColor("#e67e22") if "Model 1:" in model_name else QColor("#e6e622"))
                cursor.insertText(f"{model_name}: ", format)
                format.setForeground(QColor("#e0e0e0"))
                cursor.insertText(content.strip(), format)
            else:
                format.setForeground(QColor("#e0e0e0"))
                cursor.insertText(message, format)
        cursor.insertText("\n\n", format)

        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def update_streaming_message(self, chunk):
        self.current_stream_message += chunk
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(chunk)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def clear_chat(self):
        self.chat_display.clear()
        self.current_stream_message = ""

class VisualizationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTheme(QChart.ChartThemeDark)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        layout.addWidget(self.chart_view)

    def update_chart(self, data):
        QMetaObject.invokeMethod(self, "update_chart_internal", Qt.QueuedConnection, Q_ARG(dict, data))

    @pyqtSlot(dict)
    def update_chart_internal(self, data):
        self.chart.removeAllSeries()
        for axis in self.chart.axes():
            self.chart.removeAxis(axis)

        bar_series = QBarSeries()
        line_series = {}

        for model, times in data.items():
            bar_set = QBarSet(model)
            bar_set.append(sum(times))
            bar_series.append(bar_set)

            line = QLineSeries()
            line.setName(f"{model} (per round)")
            for i, time in enumerate(times):
                line.append(i, time)
            line_series[model] = line

        self.chart.addSeries(bar_series)
        for line in line_series.values():
            self.chart.addSeries(line)

        axis_x = QBarCategoryAxis()
        axis_x.append(list(data.keys()))
        self.chart.addAxis(axis_x, Qt.AlignBottom)
        bar_series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTitleText("Response Time (s)")
        self.chart.addAxis(axis_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_y)

        for line in line_series.values():
            line.attachAxis(axis_x)
            line.attachAxis(axis_y)

        self.chart.setTitle("Model Response Times")
        self.chart_view.setChart(self.chart)