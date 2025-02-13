import requests
import random
import time
import argparse

def send_data(x, y, url):
    headers = {"Content-Type": "application/json"}
    data = {"x": x, "y": y}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Sent data point: x={x}, y={y}")
        print(f"Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")

def main():
    parser = argparse.ArgumentParser(description='Send data to oscilloscope server')
    parser.add_argument('--url', default='https://osc-e6agfvf6echyekav.canadacentral-01.azurewebsites.net/data',
                      help='URL of the oscilloscope server')
    args = parser.parse_args()
    
    print(f"Starting data transmission to {args.url}...")
    x = 0
    try:
        while True:
            y = random.uniform(-100, 100)
            send_data(x, y, args.url)
            x += 1
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\nStopping data transmission...")

if __name__ == "__main__":
    main()