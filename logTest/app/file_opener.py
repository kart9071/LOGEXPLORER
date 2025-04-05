from PyQt6.QtWidgets import (
    QWidget, QPushButton, QListWidget, QListWidgetItem,
    QVBoxLayout, QFileDialog, QHBoxLayout, QLineEdit, QLabel, QDialog
)
from PyQt6.QtCore import Qt
from app.kafka_consumer import KafkaLogConsumer
import ollama
from app.LogFileLoader import LogFileLoader

class FileOpenerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.consumer_thread = None
        self.log_file = None
        self.line_number = 1
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Kafka Log Explorer")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #2E3440;")

        self.open_button = QPushButton('Open', self)
        self.open_button.setStyleSheet("color: white; font-size:10px;")
        self.open_button.setFixedSize(50, 40)
        self.open_button.clicked.connect(self.open_file)

        self.button = QPushButton("Start", self)
        self.button.clicked.connect(self.start_listening)
        self.button.setStyleSheet("color: white; font-size: 10px;")
        self.button.setFixedSize(50, 40)

        self.show_full_button = QPushButton("→", self)
        self.show_full_button.setFixedSize(30, 30)
        self.show_full_button.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 14px;
                margin-left: 10px;
                padding: 0px;
            }
        """)
        self.show_full_button.clicked.connect(self.scroll_to_bottom)

        self.query_input = QLineEdit(self)
        self.query_input.setPlaceholderText("Ask about failures...")
        self.query_input.setStyleSheet("color: white; background-color: #333; font-size: 14px;")
        self.query_input.returnPressed.connect(self.handle_query)

        self.log_list = QListWidget(self)
        self.log_list.setStyleSheet("""
            QListWidget {
                background-color: #1E1E1E;
                border: none;
            }
        """)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.button)
        button_layout.addWidget(self.show_full_button)
        button_layout.addStretch()
        
        self.loading_label = QLabel("")
        self.loading_label.setStyleSheet("color: gray; font-size: 12px;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.log_list)
        main_layout.addWidget(self.query_input)
        main_layout.addWidget(self.loading_label)

        self.setLayout(main_layout)

    def scroll_to_bottom(self):
        self.log_list.scrollToBottom()

    def start_listening(self):
        if self.log_file:
            if not self.consumer_thread or not self.consumer_thread.isRunning():
                self.consumer_thread = KafkaLogConsumer(self.log_file)
                self.consumer_thread.log_signal.connect(self.append_log)
                self.consumer_thread.start()
            else:
                self.append_log("Kafka consumer is already running.")
        else:
            self.append_log("No file selected. Please open a file first.")

    def highlight_log(self, log):
        if "ERROR" in log or 'error' in log:
            return "#FF6B6B"
        elif "INFO" in log or 'info' in log:
            return "#5AC8FA"
        elif "WARNING" in log or 'WARN' in log or 'war' in log or 'warning' in log:
            return "#F4C542"
        else:
            return "#E0E0E0"

    def append_log(self, log):
        color = self.highlight_log(log)
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 2, 5, 2)

        # ← Button
        expand_button = QPushButton("←")
        expand_button.setStyleSheet("color: white; font-size: 12px;")
        expand_button.setFixedWidth(30)
        expand_button.clicked.connect(lambda _, full_log=log: self.show_full_log(full_log))

        # Line number
        line_label = QLabel(f"{self.line_number:>4}")
        line_label.setStyleSheet("color: gray; font-family: monospace; font-size: 12px;")
        line_label.setFixedWidth(40)

        # Log text
        log_label = QLabel(log)
        log_label.setStyleSheet(f"color: {color}; font-size: 12px; font-family: monospace;")
        log_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        layout.addWidget(expand_button)
        layout.addWidget(line_label)
        layout.addWidget(log_label)
        layout.addStretch()
        widget.setLayout(layout)

        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        self.log_list.addItem(item)
        self.log_list.setItemWidget(item, widget)

        self.line_number += 1

    def show_full_log(self, log_text):
        dlg = QDialog(self)
        dlg.setWindowTitle("Full Log")
        dlg.setStyleSheet("background-color: #2E3440; color: white; font-size: 14px;")
        dlg.setMinimumSize(600, 200)

        layout = QVBoxLayout()
        label = QLabel(log_text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(label)

        dlg.setLayout(layout)
        dlg.exec()

    # def open_file(self):
    #     file_name, _ = QFileDialog.getOpenFileName(
    #         self, "Open Log File", "", "Log Files (*.log *.txt *.json *.csv *.xml);;All Files (*)"
    #     )
    #     if file_name:
    #         self.log_file = file_name
    #         self.log_list.clear()
    #         self.line_number = 1
    #         try:
    #             with open(file_name, 'r', encoding='utf-8', errors='ignore') as file:
    #                 for line in file:
    #                     self.append_log(line.strip())
    #         except Exception as e:
    #             self.append_log(f"Error opening file: {str(e)}")
    

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Log File", "", "Log Files (*.log *.txt *.json *.csv *.xml);;All Files (*)"
        )
        if file_name:
            self.log_file = file_name
            self.log_list.clear()
            self.line_number = 1
            self.setDisabled(True)
            self.loading_label.setText("Loading: 0%")

            try:
                with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
                    total_lines = sum(1 for _ in f)
            except Exception as e:
                self.append_log(f"Error reading file: {str(e)}")
                self.setDisabled(False)
                return

            self.loader_thread = LogFileLoader(file_name, total_lines)
            self.loader_thread.log_signal.connect(self.append_log)
            self.loader_thread.progress_signal.connect(self.update_loading_label)
            self.loader_thread.finished_signal.connect(self.on_file_loaded)
            self.loader_thread.start()


    def update_loading_label(self, percent):
        self.loading_label.setText(f"Loading: {percent}%")

    def on_file_loaded(self):
        self.setDisabled(False)
        self.loading_label.setText("")  # Clear loading status

    
    def analyze_logs(self, query):
        logs = "\n".join(
            [self.log_list.item(i).text() for i in range(max(0, self.log_list.count() - 50), self.log_list.count())]
        )
        prompt = f"Logs:\n{logs}\n\nQuestion: {query}\nAnswer:"

        try:
            response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
            if "message" in response and "content" in response["message"]:
                return response["message"]["content"]
            else:
                return "AI response is empty or improperly formatted."
        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"

    def handle_query(self):
        query = self.query_input.text().strip()
        if query:
            response = self.analyze_logs(query)
            self.append_log(f"[AI Response] {response}")
        self.query_input.clear()
