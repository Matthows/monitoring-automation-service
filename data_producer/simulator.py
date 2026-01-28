import time
import random
import requests
import logging

# Configuration
API_URL = "http://localhost:8000/api/data"
DEVICES = ["SENSOR_OFFICE", "SENSOR_WAREHOUSE", "SENSOR_LAB"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_data():
    """Generates realistic random data"""
    device = random.choice(DEVICES)
    # Temperature: mean 22, occasional peaks above 30
    temp = round(random.gauss(24, 4), 1) 
    humidity = round(random.uniform(30, 70), 1)
    
    return {
        "device_id": device,
        "temperature": temp,
        "humidity": humidity
    }

def main():
    print(f"🚀 Avvio simulatore sensori... Target: {API_URL}")
    print("Premi CTRL+C per fermare.")
    
    while True:
        try:
            payload = generate_data()
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                logging.info(f"✅ Inviato: {payload} -> DB OK")
            else:
                logging.error(f"❌ Errore API: {response.status_code}")
                
        except Exception as e:
            logging.error(f"⚠️ Connessione fallita: {e}")
            
        time.sleep(2)  # Send data every 2 seconds

if __name__ == "__main__":
    main()
