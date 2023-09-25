import subprocess
import csv
from datetime import datetime

# Run smartctl --scan to list all available drives
def get_all_disks():
    try:
        result = subprocess.run(["smartctl", "--scan"], capture_output=True, text=True, check=True)
        drive_lines = result.stdout.strip().split("\n")
        return [line.split()[0] for line in drive_lines]
    except subprocess.CalledProcessError as e:
        print(f"Error running smartctl --scan: {e}")
        return []

# CSV file name
csv_file = "/mnt/user/data/scripts/data_database.csv"

# Get the current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Get a list of all available drives
all_drives = get_all_disks()

# Open the CSV file for writing
with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    
    # Write the header if the file is empty
    if file.tell() == 0:
        writer.writerow(["Timestamp", "Disk", "Temperature (°C)"])
    
    # Loop through each drive
    for drive in all_drives:
        try:
            # Check if the drive starts with "sd"
            if drive.startswith("/dev/sd"):
                # Run smartctl to get temperature data
                result = subprocess.run(["smartctl", "-A", drive], capture_output=True, text=True, check=True)
                
                # Find the temperature from the smartctl output
                temperature = None
                for line in result.stdout.splitlines():
                    if "Temperature_Celsius" in line:
                        temperature = line.split()[9]
                        break
                
                # If temperature is None or couldn't be determined, set it to "N/A"
                if temperature is None:
                    temperature = "N/A"
            else:
                # For NVMe drives, use the previous logic to find temperature
                try:
                    # Run smartctl to get temperature data
                    result = subprocess.run(["smartctl", "-a", drive], capture_output=True, text=True, check=True)
                    
                    # Find the temperature from the smartctl output
                    temperature = None
                    for line in result.stdout.splitlines():
                        if "Temperature:" in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                temperature = parts[1]
                                break
                    
                    # If temperature is None or couldn't be determined, set it to "N/A"
                    if temperature is None:
                        temperature = "N/A"
                except subprocess.CalledProcessError as e:
                    print(f"Error running smartctl for {drive}: {e}")
                    temperature = "N/A"
        
            # Write the data to the CSV file
            writer.writerow([timestamp, drive, temperature])
            
            print(f"Timestamp: {timestamp}, Disk: {drive}, Temperature: {temperature}°C")
        
        except subprocess.CalledProcessError as e:
            print(f"Error running smartctl for {drive}: {e}")
        
        except Exception as e:
            print(f"Error: {e}")

print("Data written to", csv_file)
