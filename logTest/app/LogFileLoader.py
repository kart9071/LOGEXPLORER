from PyQt6.QtCore import QThread, pyqtSignal
import time

class LogFileLoader(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, file_path, total_lines):
        super().__init__()
        self.file_path = file_path
        self.total_lines = total_lines

    def run(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for idx, line in enumerate(file, start=1):
                    self.log_signal.emit(line.strip())
                    percent = int((idx / self.total_lines) * 100)
                    self.progress_signal.emit(percent)
                    time.sleep(0.004)
        except Exception as e:
            self.log_signal.emit(f"Error opening file: {str(e)}")
        self.finished_signal.emit()
