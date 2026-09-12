import serial
import time
import getpass
import sys

def connect_wifi():
    print("--- Uno Q Wi-Fi Setup ---")
    ssid = input("Enter your Wi-Fi Network Name (SSID): ")
    password = getpass.getpass("Enter your Wi-Fi Password (hidden): ")

    try:
        print("\nConnecting to Uno Q on /dev/ttyACM0...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
        
        # Wake up / Login if needed
        ser.write(b'\n')
        time.sleep(0.5)
        ser.write(b'root\n')
        time.sleep(1)
        ser.write(b'\n')
        
        print(f"Sending Wi-Fi configuration for '{ssid}'...")
        # Send nmcli command
        cmd = f'nmcli dev wifi connect "{ssid}" password "{password}"\n'
        ser.write(cmd.encode())
        
        print("Waiting for network connection (10 seconds)...")
        # Print a simple progress bar
        for _ in range(10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
        print()
        
        print("Fetching new IP address...")
        ser.write(b'hostname -I\n')
        time.sleep(2)
        
        # Read whatever comes back
        output = ser.read(2048).decode('utf-8', errors='replace')
        
        print("\n--- Output from Uno Q ---")
        # Filter and print lines that look like IP addresses
        lines = output.split('\n')
        ip_found = False
        for line in lines:
            line = line.strip()
            if line and not line.startswith('root') and not line.startswith('nmcli') and not line.startswith('hostname'):
                print(line)
                ip_found = True
                
        if not ip_found:
            print(output)
            
        print("-------------------------")
        ser.close()
        print("\nIf you see an IP address above (e.g., 192.168.x.x), you can now open your browser and navigate to: http://<THAT_IP_ADDRESS>:5000")
    except Exception as e:
        print(f"Error connecting: {e}")

if __name__ == "__main__":
    connect_wifi()
