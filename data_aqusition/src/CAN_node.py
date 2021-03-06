# CAN ids we want "0CFFF048, 0CFFF148, 0CFFF248, 0CFFF348, 0CFFF448, 0CFFF548, 0CFFFC48"
# CAN ids after self conversion [218099784, 218100040, 218100296, 218100552, 218100808, 218101064, 218102856]

#!/usr/bin/env python

import rospy 

from data_aqusition.msg import tire_t
from data_aqusition.msg import ecu_msg

import can 
import time 


class pyCAN:
	
	
	def __init__(self):
		# Can bus properties for can0
		self.channel = 'can0'
		self.bustype = 'socketcan'
		self.bitrate = 1000000 # Adjust everything except ecu to this speed or reprogramm tire temperature sensors
				
		# Can bus properties for can1
		self.channel = 'can1'
		self.bitrate = 500000 # ECU can only run upto 500 kbits/sec, I don't remember it working with 1 Mbit/sec
		
		self.bus = can.interface.Bus(channel = self.channel, bustype = self.bustype, bitrate = self.bitrate)
		self.reader = can.BufferedReader()
		#self.logger = can.Logger('logfile.asc')   Can be used for logging without ros
		self.listeners = [self.reader] #, self.logger]
		self.notifier = can.Notifier(self.bus, self.listeners)
		
		# Initilize custom messages 
		self.tire_msg = tire_t()
		self.ecu_msg = ecu_msg()

		# Initizile ros publsihers and set rate of the main loop
		rospy.init_node('can_driver', anonymous=True)
		can_pub = rospy.Publisher("can_data", tire_t , queue_size = 100)
		ecu_pub = rospy.Publisher('ecu_data', ecu_msg, queue_size = 100)
		rate = rospy.Rate(100)
		
		# Initilize fixed value list for data
		self.tire_id = [i for i in range (1200, 1212 + 1)]
		self.avr_t = [0,0,0,0]
		self.tireT_out = [0 for i in range(0,16)]
		self.ecu_out = [0 for i in range(0,16)]

		ecu_arbitaions = [218099784, 218100296, 218100552, 218100808, 218101064, 218102856]
		n_steps = 0


		def dec_converter(msb,lsb):
			dec = 256 * msb + (lsb/16) * 16 + lsb//16 
			return dec


		def tire_temp(tTemp):
			tTemp = tTemp/10 - 100
			return tTemp


		def tireT_arbitation_filter(canid):
			#take first readings per channel and assign them accordingly
			msb = msg.data[0]
			lsb = msg.data[1]
			tmp = tire_temp(dec_converter(msb, lsb))
			
			# Switcher use is not optimal for data output 
			# can set a list from case
			# values drift when bus drops
			# switcher = {
			# 1204: self.out[0] = tmp,
			# 1205: self.out[1] = tmp,
			# 1206: self.out[2] = tmp,
			# 1207: self.out[3] = tmp
			# }

			#Switcher for tire temperature (1200, 1216)
			# switcher = {}
			# for i in range(1204, 1207 + 1):
			#  	switcher[i] = tmp
			# out = {canid: switcher.get(canid, "nothing")}

			# Will look ugly but works
			# Look for elegant way to create bunch of function in a loop
			#list of list is easier to output in ros than dictionery
			
			# if canid   ==   1204:
			# 	self.out[0] = ["1204:", tmp]
			# elif canid == 1205:
			# 	self.out[1] = ["1205:", tmp]
			# elif canid == 1206:
			# 	self.out[2] = ["1206:", tmp]
			# elif canid == 1207:
			# 	self.out[3] = ["1207:", tmp]

			for i in self.tire_id:
				if i == canid:
					#self.tireT_out[i - 1200] = [str(i) + ":", tmp]
					self.tireT_out[i - 1200] = tmp
			print self.tireT_out
			# Assign average temperature per sensor
			self.tire_msg.avr_t_1200 = sum(self.tireT_out[0:4])/4
			self.tire_msg.avr_t_1204 = sum(self.tireT_out[5:8])/4
			self.tire_msg.avr_t_1208 = sum(self.tireT_out[9:12])/4
			self.tire_msg.avr_t_1212 = sum(self.tireT_out[13:16])/4


		def ecu_arbitation_filter(canid):
			#ECU lsb to msb, [0],[1]

			if canid ==	  218101064:
				Voltage = dec_converter(msg.data[1], msg.data[0])
				AirT = dec_converter(msg.data[3], msg.data[2])
				self.ecu_out[0] = [Voltage*0.01, AirT*0.1]
				self.ecu_msg.Battery_Voltage = Voltage
				self.ecu_msg.ait_T = AirT
			# Get analog inputs
			elif canid == 218100296:
				analog1_4 = [ (dec_converter(msg.data[i + 1], msg.data[i]) * 0.001) for i in range(0,4)]
				self.ecu_out[1] = ["analog1_4:", analog1_4]
				self.ecu_msg.analog1_4 = analog1_4
			elif canid == 218100552:
				analog5_8 = [ (dec_converter(msg.data[i + 1], msg.data[i]) * 0.001) for i in range(0,4)]
				self.ecu_out[2] = ["analog5_8:", analog5_8]
				self.ecu_msg.analog5_8 = analog5_8
			#Get wheel speed data
			elif canid == 218100808:
				freq1_4 = [ (dec_converter(msg.data[i + 1], msg.data[i]) * 0.02) for i in range(0,4)]
				self.ecu_out[3] = ["freq1_4:", freq1_4]
				self.ecu_msg.freq1_4 = freq1_4
			elif canid == 218099784:
				RPM = dec_converter(msg.data[1], msg.data[0])
				TPS = dec_converter(msg.data[3], msg.data[2])
				self.ecu_out[4] = [RPM, TPS * 0.1]
				self.ecu_msg.RPM = RPM
				self.ecu_msg.TPS = TPS
			
			# for i in ecu_arbitaions:
			# 	if canid = ecu_arbitaions[i]:
		
			#rospy.loginfo(self.out)
			#can_pub.publish(str(self.out[0][1204]))
			#print self.ecu_out

		while not rospy.is_shutdown():
			n_steps += 1
			msg = self.reader.get_message()
			if msg is not None:
				msg_id = msg.arbitration_id	
				ecu_arbitation_filter(msg_id)
				tireT_arbitation_filter(msg_id)
			# Limit message publish rate 
			if (n_steps + 1) % 100 == 0:
				ecu_pub.publish(self.ecu_msg)
				can_pub.publish(self.tire_msg) 
			#rate.sleep()

if __name__ == '__main__':
	try:

		C = pyCAN()
		#rospy.spin() Only needed with subsribers 

	except rospy.ROSInterruptException:
		pass

