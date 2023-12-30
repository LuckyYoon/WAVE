# WAVE - “Waterborne Autonomous Vessel for Emergencies” 

Jonghoo “Justin” Yoon - jonghoo.yoon@valorschool.org

Abstract – This study introduces the Waterborne Autonomous Vessel for Emergencies (WAVE), a system engineered to identify and rescue individuals at risk of drowning or entering restricted aquatic zones. Upon detecting a potential emergency, WAVE promptly alerts the relevant authorities and deploys an autonomous vessel. This vessel is adept at independently navigating to the emergency site and carrying out rescue operations. The design phase of WAVE involved constructing a Proof-of-Concept (PoC) vessel, equipped with specialized aquatic motors, controlled by an Arduino Uno. This microcontroller interfaces with a Raspberry Pi 4, serving as the navigation controller, which processes data and issues navigational commands. The system’s command hub, a dedicated local server outfitted with a camera, employs State-of-the-Art (SOTA) Image Detection, Pose, and Segmentation algorithms in Computer Vision (CV) to accurately identify dangers in real-time water settings, ensuring timely and precise directives are sent to the vessel. Tested in controlled shoreline simulations, WAVE has proven effective in detection and rescue, positioning itself as a viable, cost-effective solution for enhancing water safety. It can serve as a safeguard for swimmers and beachgoers, aiming to significantly reduce the risks associated with drowning and unauthorized entry into hazardous zones.

The Server folder holds the code for the local server and the ground station Raspberry Pi 4.

Vessel_Arduino.ino file holds the code for the PoC rescue vessel's Arduino Uno.
