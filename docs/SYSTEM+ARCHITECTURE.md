when the arduino uno q boots up,it first has to search if its connected to all the necessary devices(cams,mic) and also check bluetooth(the speaker for the llm output tts),Then,it needs to use the speaker to say"hi,im awake."


once that happens,if the bot is being used for the first time,the user has to say "bot,setup",in order to start setting up users.the device then outputs "phone or voice" through the speaker(tts),and waits for the users reply("phone or voice")



if phone:
........



if voice:
device asks to define caretakers,each caretaker needs a name,and a time of work(morning,evening,full day),and if the caretaker itself is the patient.facial scanning and adding to the database will be done in parallel using cam1
if the last sentence is false:
after defining each caretaker,the device will ask if the list of caretakers is over,to which the user has to reply yes or no.
if no ,this repeats

if the last sentence is true,skip to patient definition,then go back to the caretaker loop


after the caretaker process is done,the device outputs:"enter patient name:",and waits for the users reply.also scans their face to store in the database
and also asks for age,gender,health issues,medicines to take along with their time(morning/evening,before food/after food),caretaker assigned to which the user can either reply in one word answers or can respond in a couple of sentences,whose meaning and relevant data will be extracted by the llm,and then sqlite tables will be created for everyone
.device asks if there are more patients,user replies yes/no
if yes,repeat
if no,break



this ends part1 of setup mode


in part2 of setup mode
the user has to insert the meds,after the user verbally confirms that all the meds have been inserted,the device uses cam 2 to scan each med text to dermine med name,dosage etc.it will have a separate table containing info related to mediicnes,so it will cross check it with this if its either unable to read the ocr small text or just to double check.the count of each medicines will also be stored alongisde



this ends setup mode



normal running mode:
after setup mode has been finished,the device will work normally.it will speak and alert the users using the speaker to alert people when they have to take their medicines.when the user walks in front of the camera or speaks near the mic,the facial recognition tool will work and scan the user to see if its a previously established user.if its a patient,the device will ask if they have had food (if they have special post food meds) and the same for if they have pre food meds.if they havent had food,then the device will them to eat their food and come back.if its a caretaker,they will be asked about whuch patient they are attending for,and the steps proceed as above.Once the conditions are met,the mediicnes are cut and dispensed using the motors.the wheel isrorated until the correct med comes in view,cam 2 is used to identify where the boundaries need to be drawn using the sam2 model,and then the motors are drawn along these boundaries.first the z motor or thrusting motor is thrust into the boundary,and then the xy gantry is used to create a hole arounf the med.then,the med holder is rotated by exactly enough degrees so that the cut med is facing the ground and it falls off.repeat if there are other meds.
update the med counter for all the meds,if n(one specific med)=1,alert user using speaker,and store reminder and alert the next dispensing timeslot right before dispensing the medicines

