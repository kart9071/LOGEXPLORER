import sys
import traceback
import logging
from PyQt6.QtWidgets import QApplication
from app.file_opener import FileOpenerApp
import os

log_path = os.path.join(os.getenv("APPDATA"), "KafkaLogApp")
os.makedirs(log_path, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_path, "error.log"),
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    try:
        app = QApplication(sys.argv)
        window = FileOpenerApp()
        window.show()
        sys.exit(app.exec())
    except Exception:
        error = traceback.format_exc()
        logging.error("Unhandled exception:\n" + error)
        print("An error occurred. Check the log file.")
        input("Press Enter to exit...")  # Keep the window open for debugging

if __name__ == "__main__":
    main()
