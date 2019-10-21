# CAN ids we want "0CFFF048, 0CFFF148, 0CFFF248, 0CFFF348, 0CFFF448, 0CFFF548, 0CFFFC48"
# CAN ids after self conversion [218099784, 218100040, 218100296, 218100552, 218100808, 218101064, 218102856]

#!/usr/bin/env python

import rospy 
from std_msgs.msg import Int16
from std_msgs.msg import String

import can 
import time 


class pyCAN:
	
	def __init__(self):
		
		self.channel = 'can0'
		self.bustype = 'socketcan'
		self.bitrate = 1000000 
		self.tireT_out = [0 for i in range(0,16)]
		self.ecu_out = [0 for i in range(0,16)]

		self.bus = can.interface.Bus(channel = self.channel, bustype = self.bustype, bitrate = self.bitrate)
		self.reader = can.BufferedReader()
		#self.logger = can.Logger('logfile.asc')
		self.listeners = [self.reader] #, self.logger]
		self.notifier = can.Notifier(self.bus, self.listeners)
		self.ecu_arbitaions = [218099784, 218100296, 218100552, 218100808, 218101064, 218102856]

		rospy.init_node('driver', anonymous=True)
		rate = rospy.Rate(20)
		can_pub =  rospy.Publisher("can_bus", String, queue_size = 100)



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

			tire_id = [i for i in range (1200, 1212 + 1)]
			for i in tire_id:
				if i == tire_id[i - 1200]:
					self.tireT_out[i - 1200] = [str(i) + ":", tmp]
			
			return self.tireT_out
			

		def ecu_arbitation_filter(canid):
			#ECU lsb to msb, [0],[1]

			if canid ==	  218101064:
				Voltage = dec_converter(msg.data[1], msg.data[0])
				AirT = dec_converter(msg.data[3], msg.data[2])
				self.ecu_out[0] = [Voltage*0.01, AirT*0.1]
			# Get analog inputs
			elif canid == 218100296:
				analog1_4 = [ (dec_converter(msg.data[i + 1], msg.data[i]) * 0.001) for i in range(0,4)]
				self.ecu_out[1] = ["analog1_4:", analog1_4]
			elif canid == 218100552:
				analog5_8 = [ (dec_converter(msg.data[i + 1], msg.data[i]) * 0.001) for i in range(0,4)]
				self.ecu_out[2] = ["analog5_8:", analog5_8]
			elif canid == 218100808:
				freq1_4 = [ (dec_converter(msg.data[i + 1], msg.data[i]) * 0.02) for i in range(0,4)]
				self.ecu_out[3] = ["freq5_8:", freq1_4]
			elif canid == 218099784:
				RPM = dec_converter(msg.data[1], msg.data[0])
				TPS = dec_converter(msg.data[3], msg.data[2])
				self.ecu_out[4] = [RPM, TPS * 0.1]
			
			# for i in ecu_arbitaions:
			# 	if canid = ecu_arbitaions[i]:
		
			#rospy.loginfo(self.out)
			#can_pub.publish(str(self.out[0][1204]))
			print self.ecu_out


		while not rospy.is_shutdown():
			
			msg = self.reader.get_message()
			if msg is not None:
				msg_id = msg.arbitration_id	
				ecu_arbitation_filter(msg_id)
				tireT_arbitation_filter(msg_id)


	# def flush_buffer(self):

 #        msg = self.buffer.get_message()
 #        while (msg is not None):
 #            msg = self.buffer.get_message()

if __name__ == '__main__':
	try:

		C = pyCAN()
		rospy.spin()

	except rospy.ROSInterruptException:
		pass

