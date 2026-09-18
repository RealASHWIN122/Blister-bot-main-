import paramiko
import sys

def run_ssh(host, user, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=password, look_for_keys=False, allow_agent=False)
        stdin, stdout, stderr = client.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read().decode()
        print("STDOUT:", out)
        print("STDERR:", err)
        return out, err
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    else:
        cmd = "echo 'ardunoq4' | sudo -S systemctl disable blisterbot.service"
    
    run_ssh('192.168.10.43', 'arduino', 'ardunoq4', cmd)
