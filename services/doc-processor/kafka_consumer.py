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
        self.consumer.subscribe([KAFKA_TOPIC, "file-deleted-topic"])
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
                    topic = msg.topic()
                    val = msg.value().decode('utf-8')
                    
                    if topic == KAFKA_TOPIC:
                        event = json.loads(val)
                        print(f"Received upload event: {event}")
                        file_id = event.get('fileId')
                        file_path = event.get('path')
                        user_id = event.get('userId')
                        
                        if file_id and file_path and user_id:
                            process_file(file_id, file_path, user_id)
                    elif topic == "file-deleted-topic":
                        # Value is just the fileId string (JSON serialized string)
                        file_id = json.loads(val) if val.startswith('"') else val
                        print(f"Received delete event for file: {file_id}")
                        from database import SessionLocal, DocumentChunk, ChatMessage
                        import uuid
                        db = SessionLocal()
                        try:
                            file_uuid = uuid.UUID(file_id)
                            db.query(DocumentChunk).filter(DocumentChunk.file_id == file_uuid).delete()
                            db.query(ChatMessage).filter(ChatMessage.file_id == file_uuid).delete()
                            db.commit()
                            print(f"Successfully deleted all chunks and messages for {file_id}")
                        except Exception as e:
                            db.rollback()
                            print(f"Error cleaning up deleted file {file_id}: {e}")
                        finally:
                            db.close()
                            
                except Exception as e:
                    print(f"Failed to process message: {e}")
        finally:
            self.consumer.close()

    def stop(self):
        self.running = False
