import subprocess
import csv
import os
import datetime

# Specify the path where the CSV file will be saved
csv_path = "/mnt/user/data/scripts/data_database.csv"

def get_active_disks_temperature():
    try:
        # Run smartctl to list all active disks
        cmd = ['smartctl', '--scan']
        output = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)

        # Split the output into lines
        lines = output.strip().split('\n')

        disk_info = []

        # Iterate through each line to extract disk information
        for line in lines:
            parts = line.split()
            if len(parts) >= 7 and (parts[0].startswith('/dev/sd') or parts[0].startswith('/dev/nvme')):  # Modify this pattern if needed
                disk = parts[0]
                temp_cmd = ['smartctl', '-A', disk]
                temp_output = subprocess.check_output(temp_cmd, universal_newlines=True, stderr=subprocess.STDOUT)
                temp_lines = temp_output.strip().split('\n')

                # Find the temperature line and extract the value
                temperature_line = next((line for line in temp_lines if 'Temperature_Celsius' in line), None)
                if temperature_line:
                    temperature_value = temperature_line.split()[9]
                    # Add a date and time stamp
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    disk_info.append({'Timestamp': timestamp, 'Disk': disk, 'Temperature': temperature_value})

        return disk_info

    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output}")
        return None

def save_to_database(data, database_filename, headers):
    # Check if the database file already exists, if not, create it and write the headers
    if not os.path.isfile(database_filename):
        with open(database_filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()

    # Remove the /dev/ prefix from the disk identifier before writing to the CSV
    data['Disk'] = data['Disk'][5:]

    # Append the new data to the database file
    with open(database_filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writerow(data)

if __name__ == "__main__":
    active_disks_temperature = get_active_disks_temperature()

    if active_disks_temperature:
        for disk_info in active_disks_temperature:
            print(f"Timestamp: {disk_info['Timestamp']}")
            print(f"Disk: {disk_info['Disk']}")
            print(f"Temperature: {disk_info['Temperature']}°C")
            print()
            # Save the data to the specified CSV file
            headers = ['Timestamp', 'Disk', 'Temperature']
            save_to_database(disk_info, csv_path, headers)
    else:
        print("Failed to retrieve disk temperature information.")
