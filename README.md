# PSFR-Data-Logger
This is repository for data acquisition system code 

Tested on Ubuntu 18 and ROS Melodic

use sudo ip link set can0 up type can bitrate 1000000 to start auxiliary can bus

use sudo ip link set can1 up type can bitrate 500000 to start ecu bas

# Current issues:
- [ ] Node refuses to start if usb2can is unplugged
- [ ] If watching can bus module led it is visible that time to time it goes off or something, dropping some messages
- [ ] Only sepparate parts were tested individually

![ROS Diagram](https://sites.psu.edu/ferg/files/2019/12/Screenshot-from-2019-12-02-14-55-59-e1575316765505-768x418.png)
