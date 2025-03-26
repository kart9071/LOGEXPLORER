from kafka import KafkaConsumer

topic_name = "log_topic"

consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True
)

print(f"Listening to topic: {topic_name}...\n")
for message in consumer:
    print(f"{message.value.decode('utf-8')}")
