import json
import os
import threading
from time import sleep

from confluent_kafka import Consumer, KafkaError, KafkaException

"""
This module provides the KafkaService class, which is used to consume data from Kafka.
It also provides the KafkaStreamHandler class, which is used to handle the latest kafka data with http.
It also provides the KafkaSocketIO class, which is used to handle the Kafka data to socketio.

Todo:
    * Add more features

"""


class KafkaService:
    """
    KafkaService is a class to consume data from Kafka.
    It can be used to consume data from a single topic or multiple topics.
    """

    def __init__(self, config=None):
        """
        Instantiated the class.
        It sets up the Kafka consumer configs and assigns it to self.consumer.

        :param self: Represent the instance of the class
        :param config: Pass in a dictionary of configuration options
        :return: A consumer object
        :doc-author: Yukkei
        """
        if config is None:
            self.config = {
                'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS'),
                'group.id': os.environ.get('KAFKA_GROUP_ID'),
                'auto.offset.reset': os.environ.get('KAFKA_AUTO_OFFSET_RESET'),
                'enable.auto.commit': False
            }

        else:
            self.config = config

        self.consumer = Consumer(self.config)

    def subscribe(self, topics):
        """
        The subscribe function subscribes to a list of topics.
            The function takes in a list of topics and assigns the consumer to those topics.

        :param topics: Specify the topics to subscribe to
        :doc-author: Yukkei
        """
        consumer = self.consumer
        consumer.subscribe(topics, on_assign=on_assign)

    def consume(self):
        """
        This consumes a single message from the Kafka queue.

        :return: A list of messages that have been consumed
        :doc-author: Yukkei
        """

        return self.consumer.poll(timeout=1.0)

    def receive(self):
        """
        This is used to receive a single message.
        If there are no messages in the queue, it will return None.
        If there is an error, it will raise an exception.
        If there is a message, it will return the decoded message value.

        :return: The decoded message value
        :doc-author: Trelent
        """
        msg = self.consume()
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

    def gen_messages(self, rate=0):
        """
        The gen_messages function is a generator that yields messages from the Kafka topic.
        It takes an optional rate argument, which defaults to 0.
        The rate argument specifies how long to wait between yielding each message.

        :param self: Represent the instance of the class
        :param rate: Control the speed of the message consumption
        :return: A generator object that contains the messages from the topic
        :doc-author: Yukkei
        """
        while True:

            msg = self.consume()
            sleep(rate)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError.PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            else:
                yield msg

    def close(self):
        """
        The close function closes the Kafka consumer.

        :doc-author: Yukkei
        """
        try:
            self.consumer.close()
        except Exception as e:
            print(f"Error closing Kafka consumer: {e}")


class KafkaStreamHandler:
    """
    KafkaStreamHandler is a class to handle the Kafka stream.
    It can be used to get the latest data from a single device or all the devices.
    It can also be used to get the latest data stream from a single device.
    """

    def __init__(self, kafka_service: KafkaService):
        self.kafka_service = kafka_service
        self.data = {}  # {device_name: measurement} use to store the last measurement
        self.flag = {}  # {device_name: write_flag} use to indicate if the measurement is new
        self.running = False  # flag to stop the thread
        self.thread = None  # thread to run the kafka consumer

    def storing_latest(self):
        """
        The storing_latest function is a thread that runs in the background.
        It consumes messages from Kafka and stores them in a dictionary called `self.data`,
        which is keyed by device_name (the name of the device that sent the message).
        The `self.flag` dictionary keeps track of whether the message is new or not.

        :doc-author: Yukkei
        """
        print("begin storing latest data")
        while self.running:
            msg = self.kafka_service.consume()
            sleep(0)  # to prevent the thread from blocking
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError.PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            else:
                msg_json = json.loads(msg.value().decode('utf-8'))
                device_name = msg_json.get("device_name", "")
                if device_name == "":
                    continue

                self.data[device_name] = msg_json
                self.flag[device_name] = True

    def get_latest_data_for_single(self, device_name):
        """
        The get_latest_data_for_single function returns the latest data for a single device.

        :param self: Represent the instance of the class
        :param device_name: Specify which device's data is being requested
        :return: The latest data for a single device
        :doc-author: Yukkei
        """
        if device_name in self.data:
            return self.data[device_name]
        else:
            return None

    def get_latest_data_for_all(self):
        """
        The get_latest_data_for_all function returns the latest data for all the sensors in a dictionary.
        The keys are sensor names and values are tuples containing (timestamp, value) pairs.

        :return: A dictionary of the latest data for all sensors
        :doc-author: Yukkei
        """
        return self.data

    def get_latest_data_stream(self, device_name, frequency=0):
        """
        The get_latest_data_stream function is a generator that yields the latest data from a device.
            It takes in two arguments:
                1) device_name - The name of the device to get data from.
                This must be one of the devices listed in `self.data`, or else an error will be thrown.
                2) frequency - How often (in seconds) to check for new data on this stream.

        :param self: Represent the instance of the class
        :param device_name: Specify which device's data stream you want to get
        :param frequency: The sampling frequency of the data stream
        :return: generator of the latest data from a device
        :doc-author: Yukkei
        """
        if device_name not in self.data:
            print("Error: device name not found")
            return None

        while self.running:
            sleep(frequency)
            if self.flag[device_name]:
                self.flag[device_name] = False

                yield f"data: {self.data[device_name]}\n\n"

    def start(self):
        """
        The start function starts the Kafka stream.
        It sets the running variable to True, which is used in storing_latest()
            to determine whether it should continue running.
        It also creates a thread that runs storing_latest(), and then starts that thread.

        :doc-author: Yukkei
        """
        print("Kafka stream starting")
        self.running = True
        self.thread = threading.Thread(target=self.storing_latest)
        self.thread.start()
        print("Kafka stream started")

    def stop(self):
        """
        The stop function is used to stop the service.
        It sets the running variable to False, which will cause the run function to exit.
        The thread is then joined and closed.

        :doc-author: Yukkei
        """
        self.running = False
        sleep(2)
        self.kafka_service.close()
        self.thread.join()


class KafkaSocketIO(threading.Thread):
    def __init__(self, socketio, kafka_service: KafkaService, event, name_space=None):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and defines any variables
        that will be used by all instances of this class.


        :param socketio: Emit messages to the client
        :param kafka_service: KafkaService: Pass the kafkaservice object to the thread
        :param event: Specify the event name that will be emitted to the client
        :param name_space: Identify the namespace of the socketio connection
        :doc-author: Yukkei
        """
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
        """
        The run function is the main function of the thread. It will be called when
        the thread starts and will run until it exits - either by returning, or by
        raising an unhandled exception that causes the thread to fail. The return value
        (if present) is ignored.

        :param self: Represent the instance of the class
        :return: Nothing
        :doc-author: Yukkei
        """
        try:
            print("Kafka socket started")
            self.state = 'running'
            while not self._stop_event.is_set():
                msg = self.kafka_service.consume()
                sleep(0)
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

                    self.socketio.emit(self.event, msg_json, namespace=self.name_space)

        except Exception as e:
            print(f"Error: {e}")
            # logging.error(f"Error: {e}")

    def pause(self):
        """
        pause the thread
        """
        self._pause_event.clear()
        self.state = 'pause'

    def resume(self):
        """
        Resume the thread
        """
        self._pause_event.set()
        self.state = 'running'

    def stop(self):
        """
        The stop function is used to stop the Kafka socket.
        It sets a stop event, waits for 2 seconds and then closes the kafka service.

        :doc-author: Yukkei
        """
        self._stop_event.set()
        sleep(2)  # wait for the thread to stop
        self.state = 'stop'
        self.kafka_service.close()
        print("Kafka socket stopped")


def on_assign(consumer, partitions):
    """
    The on_assign function is called when the consumer has been assigned partitions.
    The callback can be used to seek to particular offsets, or reset state associated with the assignment.
    This function should not raise exceptions.

    :param consumer: Assign the partitions to the consumer
    :param partitions: Assign the partitions to the consumer
    :return: The partitions to be consumed
    :doc-author: Yukkei
    """
    for p in partitions:
        p.offset = -1
    consumer.assign(partitions)
