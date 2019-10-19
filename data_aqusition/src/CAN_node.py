#!/usr/bin/env python

import rospy 
from std_msgs.msg import Int16

import can 
import time 



class pyCAN:
	
	def __init__(self):
		
		self.channel = 'can0'
		self.bustype = 'socketcan'
		self.bitrate = 1000000 

		self.bus = can.interface.Bus(channel = self.channel, bustype = self.bustype, bitrate = self.bitrate)
		self.buffer = can.BufferedReader()

		rospy.init_node('driver', anonymous=True)
		#can_pub =  rospy.Publisher("can_bus", Int16, queue_size = 100)

		def dec_converter(msb,lsb):

			dec = 256 * msb + (lsb/16) * 16 + lsb//16 
			return dec

		def tire_temp(tTemp):

			tTemp = tTemp/10 - 100
			return tTemp

		while True:

			msg = self.bus.recv()
			#can_id = msg.can_id
			msb = msg.data[0]
			if
			lsb = msg.data[1]
			# Tire temp conversion

			
			# if msg.arbitration_id == 1204:
			# 	x = tire_temp(dec_converter(msb, lsb))
			switch()
				print(x)
			#time.sleep(.05)





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




