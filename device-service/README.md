# Device Service

## Description

`device-service` is responsible for managing and maintaining the state of various devices. It provides an API for registering, updating, pausing, and resuming devices among other functionalities.

## Setup

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

#### Run in native

1. Install the required dependencies:

   ```shell
   pip install -r requirements.txt
   ```

   

2. Run in flask built-in server:

   ``` python
   python run.py
   ```

   

3. Run in gurnicorn:

   ```
   gunicorn -c guni_config.py run:app
   ```

#### Run in Docker

1. Build the Docker Image

   Navigate to the root directory of your `device-service` project where the `Dockerfile` is located. Run the following command to build your Docker image:

   ```shell
   docker build -t device-service:latest .
   ```

   This will create a Docker image named `device-service` with the tag `your tag`.

   

2. Run the Docker Container

   After building the image, you can run it using:

   ```shell
   docker run -p 9002:9002 device-service:latest
   ```



