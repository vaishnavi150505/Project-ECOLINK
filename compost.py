import serial
from pymongo import MongoClient
from datetime import datetime

# Connect to MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    # Test the connection
    client.admin.command('ping')
    print("Connected to MongoDB successfully.")
    
    db = client['arduino_data']
    collection = db['dht_sensor_data']
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    exit()  # Exit the program if the connection fails

# Connect to Arduino via serial
try:
    ser = serial.Serial('COM4', 9600)  # Update port name as needed
    print("Connected to Arduino serial port successfully.")
except Exception as e:
    print(f"Failed to connect to Arduino serial port: {e}")
    exit()  # Exit the program if the connection fails

# Main loop
while True:
    try:
        # Read data from serial
        data = ser.readline().strip()
        try:
            data = data.decode('utf-8')  # Decode serial data
        except UnicodeDecodeError:
            print("Error decoding data:", data)
            continue  # Skip this iteration

        print("Raw data from Arduino:", data)
        
        # Parse the data
        if "Humidity:" in data:
            # Extract humidity, temperature (Celsius & Fahrenheit), and heat index (Celsius & Fahrenheit)
            try:
                parts = data.split()
                humidity = float(parts[1].replace('%', ''))
                temp_c = float(parts[3].replace('°C', ''))
                temp_f = float(parts[4].replace('°F', ''))
                heat_index_c = float(parts[7].replace('°C', ''))
                heat_index_f = float(parts[8].replace('°F', ''))
                
                # Prepare data for insertion
                sensor_data = {
                    'humidity': humidity,
                    'temperature_c': temp_c,
                    'temperature_f': temp_f,
                    'heat_index_c': heat_index_c,
                    'heat_index_f': heat_index_f,
                    'timestamp': datetime.now()
                }
                
                # Insert data into MongoDB
                collection.insert_one(sensor_data)
                print('Data inserted:', sensor_data)
                
            except (ValueError, IndexError) as parse_error:
                print("Error parsing data:", data, "Error:", parse_error)
        
    except Exception as e:
        print(f"Error: {e}")
