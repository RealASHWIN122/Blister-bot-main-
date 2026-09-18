import subprocess
import time

def main():
    p = subprocess.Popen(
        ['bluetoothctl'], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
    )
    p.stdin.write('power on\n')
    p.stdin.write('agent on\n')
    p.stdin.write('default-agent\n')
    p.stdin.write('scan on\n')
    p.stdin.flush()
    print("Scanning...")
    time.sleep(15)

    p.stdin.write('pair CE:9B:AB:F5:D4:BE\n')
    p.stdin.flush()
    print("Pairing...")
    time.sleep(10)

    p.stdin.write('trust CE:9B:AB:F5:D4:BE\n')
    p.stdin.write('connect CE:9B:AB:F5:D4:BE\n')
    p.stdin.flush()
    print("Trusting and Connecting...")
    time.sleep(10)
    
    p.stdin.write('quit\n')
    p.stdin.flush()
    
    stdout, stderr = p.communicate()
    print(stdout)

if __name__ == '__main__':
    main()
