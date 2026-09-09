#!/bin/bash
echo "Pushing files to board..."
adb shell mkdir -p /home/arduino/appliance_terminal/faces
adb push /home/me/Videos/arduinohack/appliance_terminal/appliance.py /home/arduino/appliance_terminal/
adb push /home/me/Videos/arduinohack/Blister-bot-main-/week2/facerecog-unoq/attendance.db /home/arduino/appliance_terminal/
adb push /home/me/Videos/arduinohack/Blister-bot-main-/week2/facerecog-unoq/haarcascade_frontalface_default.xml /home/arduino/appliance_terminal/
adb push /home/me/Videos/arduinohack/Blister-bot-main-/week2/facerecog-unoq/faces /home/arduino/appliance_terminal/

echo "Installing dependencies on board (Using sudo)..."
adb shell "echo arduino | sudo -S apt-get update"
adb shell "echo arduino | sudo -S apt-get install -y python3-pip python3-opencv"
adb shell "echo arduino | sudo -S pip3 install pyserial numpy --break-system-packages"

echo "Setting up systemd auto-start..."
cat << 'SYS_EOF' > /tmp/appliance.service
[Unit]
Description=Face Recognition Appliance
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/arduino/appliance_terminal/appliance.py
WorkingDirectory=/home/arduino/appliance_terminal
StandardOutput=inherit
StandardError=inherit
Restart=always
User=arduino

[Install]
WantedBy=multi-user.target
SYS_EOF

adb push /tmp/appliance.service /tmp/
adb shell "echo arduino | sudo -S mv /tmp/appliance.service /etc/systemd/system/"
adb shell "echo arduino | sudo -S systemctl daemon-reload"
adb shell "echo arduino | sudo -S systemctl enable appliance.service"
adb shell "echo arduino | sudo -S systemctl restart appliance.service"
echo "Done!"
