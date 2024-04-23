# IoT Platform Backend Services

## Introduction

The IoT Platform Backend Services comprise a set of microservices designed to cater to Internet of Things (IoT) devices. These services facilitate data processing, device management, and supervisory control, all unified under a single reverse proxy for scalability and performance.

## IoT Platform Architecture

- Infrastructure

  ![](screenshots\iot-workflow.png)

- For edge-device part, see [edge-device](https://github.com/yuk-kei/Edge-Device) repository.

- For storing the clips of video streaming , see [video-segmenter](https://github.com/yuk-kei/live-stream-segmenter) repository.

## Services Overview

- **Data Dispatcher (data-dispatcher)**: Responsible for dispatching data, handling data requests, and managing data streams.
- **Device Manager (device-manager)**: Handles CRUD operations for devices and device groups
- **Supervisor (supervisor)**: A service that provides supervisory control and configuration for whole system and devices.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Configure environment variables for each service using the respective `.env.example` files.

### Running with Docker Compose

1. **Navigate to the project root**:

   ```bash
   cd path/to/iot-platform
   ```

2. **Start the services**:

   ```bash
   docker-compose up --build
   ```

3. Once all services are up, you can access them through the Nginx reverse proxy:

   - Data Dispatcher: `http://localhost/api/data`
   - Device Manager: `http://localhost/api/devices`
   - Supervisor: `http://localhost/api/control`

## Configuration

- **Nginx**: To adjust Nginx configurations, modify the `nginx.conf` file. If planning to enable HTTPS, ensure the SSL certificate paths are correctly mounted in the docker-compose file.
- **Environment Variables**: Each service comes with a `.env.example` file. Copy this file to `.env` within the respective service directory and adjust the configurations as necessary.