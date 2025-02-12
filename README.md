# Web Oscilloscope

A web-based oscilloscope that displays real-time data broadcasted via HTTP POST requests.  
This application uses:

- **Flask** to receive incoming data,
- **Bokeh** to display an interactive, real-time oscilloscope,
- **Nginx** as a reverse proxy to route requests from a single public port,
- **Containerized** for easy deployment to the cloud (e.g., via Azure Web App for Containers).

Users can publish data to this oscilloscope and view the real-time graph via a web browser anywhere.

![Web Oscilloscope](./demo.gif)

---

## Features

- **Real-Time Visualization:**  
  Uses [Bokeh](https://bokeh.org/) to render a continuously updating oscilloscope.
- **Data Ingestion API:**  
  A [Flask](https://flask.palletsprojects.com/) endpoint receives data via HTTP POST requests.
- **Persistent Data Storage:**  
  A capped global deque stores incoming data points for persistent plotting.
- **Reverse Proxy with Nginx:**  
  Routes requests to the correct backend (Bokeh or Flask) while exposing a single public port.
- **Containerized Deployment:**  
  Dockerized for seamless deployment to cloud services like Azure.
- **Cloud Ready:**  
  Easily deployed on Azure Web App for Containers by pushing the image to a registry and configuring environment variables.

---

## Project Structure

```bash
.
├── Dockerfile        # Docker build instructions
├── README.md         # This documentation file
├── nginx.conf        # Nginx configuration for reverse proxying
├── oscilloscope.py   # Main application (Flask + Bokeh server)
├── requirements.txt  # Python dependencies list
├── send_data.py      # Utility script to simulate sending data
├── start.sh          # Startup script to launch the app and Nginx
└── venv              # (Optional) Local virtual environment folder
```

---

## Prerequisites

- [Docker](https://www.docker.com/) (Docker Desktop or similar)
- Python 3.7.13 if you wish to run parts of the application locally
- An [Azure account](https://azure.microsoft.com/) if you plan to deploy to Azure

---

## Getting Started (Local Testing)

### 1. Build the Docker Image

In your project directory, run:

```bash
docker build -t osc .
```

This command uses the Dockerfile to create an image named osc.

### 2. Run the Docker Container Locally

Run the container and map the container’s port 80 (Nginx) to a host port (e.g., 8080):

```bash
docker run -p 8080:80 osc
```

- Nginx listens on port 80 inside the container.
- The environment variable BOKEH_ALLOW_WS_ORIGIN is set to localhost:8080 (for local testing).

### 3. View the Oscilloscope

Open your browser and navigate to:

```bash
http://localhost:8080
```

You should see the oscilloscope interface (powered by Bokeh).

### 4. Send Data to the Oscilloscope

You can simulate data input by using the provided `send_data.py` script:

```bash
python send_data.py --url "http://localhost:8080/data"
```

Or manually send data via curl:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"x": 12.34, "y": 56.78}' http://localhost:8080/data
```

Successful responses will return JSON like:

```json
{ "status": "success" }
```

---

## Deployment to Azure

### 1. Build and Push the Docker Image

```bash
docker buildx build --platform linux/amd64 -t <your-dockerhub-username>/osc:latest --push .
```

### 2. Create an Azure Web App for Containers

1. In the Azure Portal, create a new Web App for Containers.
2. In the container settings:
   - Choose Docker Hub as the image source.
   - Enter the image name (e.g., `<your-dockerhub-username>/osc:latest`).
   - Azure will expose the container on port 80 by default.
3. In the Configuration section, add or update the environment variable:
   - Name: `BOKEH_ALLOW_WS_ORIGIN`
   - Value: `<your-azure-web-app-domain>` (e.g., `osc-yourapp.azurewebsites.net`)
4. Save the configuration and restart the container.

### 3. Access the Deployed Oscilloscope

After deployment, your application will be available at the URL provided by Azure (e.g., `https://osc-yourapp.azurewebsites.net`).

- **Oscilloscope Page**:
  Visit the Azure URL in your browser to view the oscilloscope.
- **Data Ingestion**:
  Send data to the oscilloscope by POSTing to `https://osc-yourapp.azurewebsites.net/data`.

---

## Configuration

- **BOKEH_ALLOW_WS_ORIGIN**:

  This environment variable controls which websocket origins are allowed by the Bokeh server.

  - Local Testing: Set to `localhost:8080` (as specified in the Dockerfile).
  - Azure Deployment: Set this in Azure's Application Settings to your Azure Web App domain.

- **Ports**:

  Internally, the Bokeh server listens on port 5001, and the Flask server listens on port 5002. Nginx proxies:

  - `/` → `http://localhost:5001` (Bokeh)
  - `/data` → `http://localhost:5002` (Flask)

---

## Usage

- View Oscilloscope:
  Open the URL in your browser to view the real-time oscilloscope.

- Publish Data:
  Send JSON data to the `/data` endpoint using the provided `send_data.py` script or other HTTP clients.

  Example JSON payload:

  ```json
  { "x": 12.34, "y": 56.78 }
  ```
