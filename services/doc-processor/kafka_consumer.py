import json
import threading
from confluent_kafka import Consumer, KafkaError
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID, KAFKA_TOPIC
from processor import process_file

class KafkaConsumerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.consumer = Consumer({
            'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
            'group.id': KAFKA_GROUP_ID,
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([KAFKA_TOPIC])
        self.running = True

    def run(self):
        print(f"Starting Kafka consumer on topic {KAFKA_TOPIC}")
        try:
            while self.running:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                        print(f"Waiting for topic {KAFKA_TOPIC} to be created...")
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        break

                # Process message
                try:
                    val = msg.value().decode('utf-8')
                    event = json.loads(val)
                    print(f"Received event: {event}")
                    file_id = event.get('fileId')
                    file_path = event.get('path')
                    user_id = event.get('userId')
                    
                    if file_id and file_path and user_id:
                        process_file(file_id, file_path, user_id)
                except Exception as e:
                    print(f"Failed to process message: {e}")
        finally:
            self.consumer.close()

    def stop(self):
        self.running = False
