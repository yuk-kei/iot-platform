# Data dispatcher service

## Description

This Flask-based application is designed to handle data streams from Kafka. It offers integration with InfluxDB for data storage and provides the ability to query, stream, and visualize data in real-time.

## Components and Capabilities

1. **Data handling**

   - Handles various data requests like:
     - Querying and streaming data from Influx DB.
     - Accessing the latest data from Kafka and streaming it.
     - Capable of managing multiple Kafka streams in real-time and pushing data to socketio clients.
   - Utilizes `data_handler.py` for interacting with Influx DB and `kafka_handler.py` for Kafka operations.

   

2. **Kafka Integration**

   - `KafkaService`: A class to consume data from Kafka, supporting single or multiple topics.
   - `KafkaStreamHandler`: Used to manage and access the latest data from Kafka via HTTP.
   - `KafkaSocketIO`: Interfaces with Kafka to handle data transfer to socketio.

------

## Setup and Running the Application

### Configuration

1. Navigate to the directory:

   ```shell
   cd device-service
   ```
   
2. Set up environment variables. Create and copy the `.env.example` to `.env` and adjust variables accordingly:

   ```
   cp .env.example .env
   ```

### Run

1. **Running with Docker**:

   ```sh
   docker build -t "data-handler" .
   docker run -p 9001:9001 data-handler
   ```

2. **Running Natively**:

   - Ensure you have all necessary dependencies installed:

     ```sh
     pip install -r requirements.txt
     ```

     

   - Run in flask built-in server:
   
     ``` python
     python run.py
     ```
     
     
     
   - Run in gurnicorn:
   
     ```
     gunicorn -c guni_config.py run:app
     ```