#!/bin/bash
echo "Cleaning remote structure..."
./code/utils/ssh_cmd.exp "rm -rf /home/arduino/Blister-bot-main-/code /home/arduino/Blister-bot-main-/week2 /home/arduino/Blister-bot-main-/master_controller.py /home/arduino/Blister-bot-main-/stepper_motor_controller"

echo "Creating rsync expect script..."
cat << 'EXPECT_EOF' > rsync.exp
#!/usr/bin/expect -f
set timeout -1
set password "ardunoq4"
set cmd [lindex $argv 0]

spawn sh -c "$cmd"
expect {
    "*assword:*" {
        send "$password\r"
        exp_continue
    }
    eof
}
EXPECT_EOF
chmod +x rsync.exp

echo "Syncing code/ directory..."
./rsync.exp "rsync -avz --exclude 'STT-streaming-zipformer-indian-en' --exclude 'qwen2.5-0.5b-instruct-q4_k_m.gguf' --exclude 'en_US-lessac-low.onnx' code/ arduino@192.168.10.43:~/Blister-bot-main-/code/"

echo "Done!"
