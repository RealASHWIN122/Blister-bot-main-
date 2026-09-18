import paramiko

host = '192.168.10.43'
user = 'arduino'
password = 'ardunoq4'

try:
    print("Connecting...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, look_for_keys=False, allow_agent=False)
    sftp = client.open_sftp()
    
    print("Syncing master_controller.py...")
    sftp.put('/home/me/Videos/arduinohack/Blister-bot-main-/master_controller.py', '/home/arduino/Blister-bot-main-/master_controller.py')
    
    print("Syncing database.py...")
    sftp.put('/home/me/Videos/arduinohack/Blister-bot-main-/week2/facerecog-unoq/database.py', '/home/arduino/Blister-bot-main-/week2/facerecog-unoq/database.py')
    
    sftp.close()
    client.close()
    print("Done!")
except Exception as e:
    print(f"Error: {e}")
