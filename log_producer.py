from kafka import KafkaProducer
import time

LOG_FILE = "hello.txt"
KAFKA_TOPIC = "log_topic"

producer = KafkaProducer(bootstrap_servers="localhost:9092")

def watch_file():
    """Reads new lines from the log file and sends them to Kafka."""
    with open(LOG_FILE, "r", encoding="utf-8") as file:
        file.seek(0, 2)  # Move to the end of file
        while True:
            line = file.readline()
            if line:
                producer.send(KAFKA_TOPIC, line.strip().encode("utf-8"))
                producer.flush()  # Ensure messages are sent
            time.sleep(1)  # Check every second

if __name__ == "__main__":
    watch_file()
