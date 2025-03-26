from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal
from kafka import KafkaConsumer
import sys

class KafkaLogConsumer(QThread):
    """Thread to consume Kafka logs and update GUI."""
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.consumer = KafkaConsumer("log_topic", bootstrap_servers="localhost:9092", auto_offset_reset="latest")

    def run(self):
        """Continuously listens for Kafka messages and emits them."""
        for message in self.consumer:
            self.log_signal.emit(message.value.decode("utf-8"))

class FileOpenerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Kafka Log Explorer")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #2E3440;")

        self.button = QPushButton("Start Listening", self)
        self.button.clicked.connect(self.start_listening)
        self.button.setStyleSheet("background-color: #88C0D0; color: black; font-size: 14px;")
        self.button.setFixedSize(150, 40)

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("background-color: white; color: black; font-size: 14px;")

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.text_area)
        self.setLayout(layout)

    def start_listening(self):
        """Starts Kafka consumer thread and connects it to UI."""
        self.consumer_thread = KafkaLogConsumer()
        self.consumer_thread.log_signal.connect(self.append_log)
        self.consumer_thread.start()

    def append_log(self, log):
        """Appends new log messages to QTextEdit."""
        self.text_area.append(log)

app = QApplication(sys.argv)
window = FileOpenerApp()
window.show()
sys.exit(app.exec())
