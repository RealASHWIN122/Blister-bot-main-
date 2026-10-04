# Blister Bot 💊🤖
# Motivation
What if you didnt have to manually strip pils from medicine packets everytime you  had a cold?What if eldery people in nursing homes and living alone at home could be safely monitored and assisted even when there is no one around? And what if all of this was hands free and handled by speaking as if you were talking to a regular person,and to top it off, all offline,so your private talks remain within your circle?




Thats what blister bot was all about.Not only has AI become more capable,it has also become more efficient,and now even small models that can run on your old laptop with no dedicated gpu can run some great models for a variety of tasks including conversational chatbots,coding work,character recognition,speech to text and vice versa and facial recognition.All of this opens up the possibilites of creating useful things with intelligence without having an internet connection.


The only limitation was that we lacked  lightweight but powerful and cheap hardware that could help build these intelligence projects,and we were stuck to using tinyml on classic boards like esp32 and the arduino uno r4 boards which at the end of the day are just microcontrollers and lack the raw memory to hold complex workflows.Luckily,with the creation of the arduino uno q and other boards we finally have the hardware to pull off these ai hardware projects without having to compromise .

DIY Edge AI Automated Medicine Dispenser (Blister Bot)
We can see automated medicine dispensers ranging from simple timed plastic boxes to massive pharmacy robotics. When we generally talk about home dispensers, they usually require the user to manually pop out pills and load them into daily bins. But what if a robot could handle the original packaging directly?
In this project, we challenge ourselves to build a complex mechatronic system that combines rotational indexing with a Cartesian CNC movement to mechanically punch pills right out of their original foil blister packs. Instead of relying on cloud APIs, this robot is powered entirely by Local Edge AI to ensure patient privacy (HIPAA compliance), offline reliability, and low-latency mechanical targeting. If you're wondering how to make a smart, AI-driven pill dispenser at home using an Arduino Uno Q, this build walks through the full process, from CNC kinematics to the conversational code.
Table of Contents
What is the Blister Bot?
Key Advantages
Components Used
How Does the Blister Bot Work?
Circuit Architecture
3D Model & Mechanical Design
AI and Software Interface
Repository Structure
Final Result
What is the Blister Bot?
The Blister Bot is a prototype DIY automated medicine dispenser designed to securely manage, schedule, and dispense medication directly from standard foil/plastic blister packs. It utilizes a 3-axis mini CNC machine to trace and drill the blister out. It also features a conversational AI interface and facial recognition to authenticate users before dispensing, running entirely offline on edge hardware.
Key Advantages of This Blister Bot
Zero Prep Work: Dispenses directly from original blister packs using a CNC punch, eliminating the need to pre-sort pills into weekly bins.
100% Offline AI: Uses miniaturized, local AI models (like Qwen 0.5B and Sherpa) to ensure medical data privacy and zero latency. No internet connection is required.
Conversational Interface: Talk to it naturally instead of using a complex touchscreen or app.
Biometric Security: Prevents accidental or unauthorized overdoses by physically verifying the patient's face before cutting the foil.
Components Used for Making the Blister Bot
Below is the complete list of components used for making this automated dispenser, along with what each part does in the overall system.
:
   ```bash
   python3 master_controller.py
   ```
