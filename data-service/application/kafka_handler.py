import json
import os
import threading
from time import sleep

from confluent_kafka import Consumer, KafkaError, KafkaException


class KafkaService:
    def __init__(self, config=None):
        if config is None:
            self.config = {
                'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS'),
                'group.id': os.environ.get('KAFKA_GROUP_ID'),
                'auto.offset.reset': os.environ.get('KAFKA_AUTO_OFFSET_RESET')
            }

        else:
            self.config = config

        self.consumer = Consumer(self.config)

    def subscribe(self, topics):
        self.consumer.subscribe(topics)

    def consume(self):
        return self.consumer.poll(timeout=1.0)

    def receive(self):
        msg = self.consume()
        sleep(1)
        if msg is None:
            print("No message received")
            return None
        if msg.error():
            if msg.error().code() == KafkaError.PARTITION_EOF:
                print('End of partition reached {0}/{1}')
                return None
            else:
                raise KafkaException(msg.error())
        else:
            return msg.value().decode('utf-8')

    def gen_messages(self):
        while True:
            msg = self.consume()
            sleep(1)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError.PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            else:
                yield f'data:{msg.value()}\n\n'

    def close(self):
        try:
            self.consumer.close()
        except Exception as e:
            print(f"Error closing Kafka consumer: {e}")


class KafkaSocketIO(threading.Thread):
    def __init__(self, socketio, kafka_service: KafkaService, event, name_space=None):
        threading.Thread.__init__(self)
        self.kafka_service = kafka_service
        self.socketio = socketio
        self.event = event
        self.state = 'pause'
        self.name_space = name_space

        self._stop_event = threading.Event()  # flag to stop the thread
        self._pause_event = threading.Event()  # flag to pause the thread
        self._pause_event.set()  # Set to True to pause the thread

    def run(self):
        try:
            print("Kafka socket started")
            self.state = 'running'
            while not self._stop_event.is_set():
                msg = self.kafka_service.consume()
                sleep(1)
                self._pause_event.wait()  # block until told to resume
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError.PARTITION_EOF:
                        print('End of partition reached {0}/{1}')
                        # logging.info('End of partition reached {0}/{1}')
                    else:
                        raise KafkaException(msg.error())
                else:
                    msg_json = json.loads(msg.value().decode('utf-8'))
                    print(msg_json)
                    self.socketio.emit(self.event, msg_json, namespace=self.name_space)

        except Exception as e:
            print(f"Error: {e}")
            # logging.error(f"Error: {e}")

    def pause(self):
        self._pause_event.clear()
        self.state = 'pause'

    def resume(self):
        self._pause_event.set()
        self.state = 'running'

    def stop(self):
        self._stop_event.set()
        sleep(2)
        self.state = 'stop'
        self.kafka_service.close()
        print("Kafka socket stopped")
