import time
import random
from datetime import datetime

LOG_FILE = "hello.txt"

def generate_random_text():
    words = ["apple", "banana", "cherry", "developer", "log", "Python", "error", "debug", "test", "random"]
    return " ".join(random.choices(words, k=5))  # Pick 5 random words

def write_log():
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            random_text = generate_random_text()
            log_entry = f"[{timestamp}] {random_text}\n"

            file.write(log_entry)
            file.flush()  # Ensure immediate writing to file

            print(log_entry, end="")  # Print in console too (optional)

            time.sleep(1)  # Write every second

if __name__ == "__main__":
    write_log()
