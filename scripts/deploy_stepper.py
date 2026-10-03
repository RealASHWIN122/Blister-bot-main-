import paramiko
import os

host = '192.168.10.43'
user = 'arduino'
password = 'ardunoq4'

try:
    print("Connecting...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, look_for_keys=False, allow_agent=False)
    
    print("Transferring zip...")
    sftp = client.open_sftp()
    sftp.put('stepper_deploy.zip', '/home/arduino/Blister-bot-main-/stepper_deploy.zip')
    sftp.close()
    
    print("Extracting...")
    client.exec_command('cd /home/arduino/Blister-bot-main- && unzip -o stepper_deploy.zip && rm stepper_deploy.zip')
    
    client.close()
    print("Deployment done!")
except Exception as e:
    print(f"Error: {e}")
