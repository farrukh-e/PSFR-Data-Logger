 
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
			switcher = {
			1204: tmp,
			1205: tmp,
			1206: tmp,
			1207: tmp
			}

			#Switcher for tire temperature (1200, 1216)
			# switcher = {}
			# for i in range(1204, 1207 + 1):
			#  	switcher[i] = tmp
			out = {canid: switcher.get(canid, "nothing")}
			return out
			

		def ecu_arbitation_filter(canid):
			pass

		def buffered_reader(msg):
			pass


		while not rospy.is_shutdown():

			for i in range (0, 4):
				msg = self.reader.get_message()
				x =arbitation_filter(msg.arbitration_id)
				self.out[i] = x
			#print self.out

			#rospy.loginfo(self.out)
			#can_pub.publish(str(self.out[0][1204]))
		
		
			print(self.out)
			#print(self.out[0])
			#rate.sleep()
			









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

