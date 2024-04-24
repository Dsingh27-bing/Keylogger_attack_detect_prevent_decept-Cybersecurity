import json
import subprocess
from scapy.all import sniff, TCP
from scapy.layers import http
import psutil

# Define a function to get a list of running processes on macOS
def get_process_list():
    process_list = []
    output = subprocess.check_output(["ps", "aux"]).decode("utf-8").split("\n")
    for line in output:
        if line:
            line = line.split()
            process_list.append(line)
    return process_list

# The below function is just to show that the keylogger detection tool is activated
def loading():
    print("Searching for KeyLoggers....")
    print("\033[1m Scanning Completed.\033[0m")  # Here, I have bolded the text

with open("keylogger_registry.json", "r") as keylogger_file:
    keylogger_name = json.load(keylogger_file)  # Registry names are stored in keylogger_name

# List to store detected keyloggers
detected_keyloggers = []

# Function to capture network packets
def capture_packets():
    packets = sniff(filter="tcp", count=100)  # Adjust the count as needed
    return packets

# Merge with the process waiting for input function
def find_processes_waiting_for_input(): #list all programs which are waiting for keyboard inputs
    for process in psutil.process_iter(attrs=['pid', 'name', 'status']):
        try:
            info = process.info
            if info['status'] == 'running':
                 # Check for keyloggers in the program list by matching with registry names
                for process in process_list:
                    if len(process) > 10:
                        process_cmd = process[10]
                        #print(process)
                        for item in keylogger_name:
                            if item["name"] in process_cmd and item["name"] in info['name']:
                                detected_keyloggers.append((process[1], process_cmd))
                                loading()
                                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

if __name__ == "__main__":
    
    process_list = get_process_list()
    email_packets = capture_packets()
    find_processes_waiting_for_input()

    # Print if detected keyloggers
    if detected_keyloggers and email_packets:
        print("\n\t\t \033[1m Keyloggers Detected!!!!!!!!!!!!!\033[0m \t\t\n ")
        for pid, cmd in detected_keyloggers:
            print(f"PID: {pid} - Command: {cmd}")
    else:
        print("\n  No Keyloggers Detected   \n ")
        print("  No email sending behavior detected")

    
