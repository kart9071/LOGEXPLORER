from PyQt6.QtCore import QThread, pyqtSignal

class KafkaLogConsumer(QThread):
    """Thread to consume Kafka logs and update the GUI."""
    log_signal = pyqtSignal(str)

    def __init__(self, log_file):
        super().__init__()
        self.log_file = log_file
        self.running = True

    def run(self):
        """Continuously listens for new lines in the log file and emits them."""
        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                file.seek(0, 2)  # Move to end of file
                while self.running:
                    line = file.readline()
                    if line:
                        self.log_signal.emit(line.strip())
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")

    def stop(self):
        """Stops the log listener."""
        self.running = False
