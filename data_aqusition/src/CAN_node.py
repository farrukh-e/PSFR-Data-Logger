 
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
		self.out = [0,0,0,0]

		self.bus = can.interface.Bus(channel = self.channel, bustype = self.bustype, bitrate = self.bitrate)
		#self.buffer = queue.Queue(0)
		self.reader = can.BufferedReader()
		self.listeners = [self.reader]
		self.notifier = can.Notifier(self.bus, self.listeners)

		rospy.init_node('driver', anonymous=True)
		rate = rospy.Rate(20)
		can_pub =  rospy.Publisher("can_bus", String, queue_size = 100)

		


		def dec_converter(msb,lsb):
			dec = 256 * msb + (lsb/16) * 16 + lsb//16 
			return dec


		def tire_temp(tTemp):
			tTemp = tTemp/10 - 100
			return tTemp


		def arbitation_filter(canid):
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
			if canid ==1204:
				self.out[0] = ["1204:", tmp]
			elif canid ==1205:
				self.out[1] = ["1205:", tmp]
			elif canid ==1206:
				self.out[2] = ["1206:", tmp]
			elif canid ==1207:
				self.out[3] = ["1207:", tmp]

			
			return self.out
			

		def ecu_arbitation_filter(canid):
			pass

		def buffered_reader(msg):
			pass

		def something_something():

			for i in range (0, 4):
				x =arbitation_filter(msg.arbitration_id)
				
			#print self.out

			#rospy.loginfo(self.out)
			#can_pub.publish(str(self.out[0][1204]))
		
		
			print(self.out)
			#print(self.out[0])
			#rate.sleep()
			
		while not rospy.is_shutdown():
			msg = self.reader.get_message()

			something_something()








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

