import serial
import time
import struct
import binascii
import optparse
import random

class LedStrips:
	def __init__(self, offset):
		"""
		Initialize an med strip
		@param offset X position of the image to get LED image data from
		"""
		self.offset = offset

	def connect(self, port):
		self.ser = serial.Serial(port, 1000002, timeout=0)

	def RgbRowToStrips(self, data):
		"""
		Convert a row of eight RGB pixels into LED strip data.
		@param data 24-byte array of 8bit RGB data for one row of pixels:
			0  1  2  3  4  5  6  7
			RGBRGBRGBRGBRGBRGBRGBRGB
		@return 24-byte stream to write to the USB port.
		"""
		if len(data) != 24:
			raise Exception('Expected 24 bytes of data, got %i'%(len(data)))

		output = ''

		# Blue byte
		output += '\xFF'
		for bit_index in range(7, 0, -1):
			c = 0x00
			for pixel_index in range(0, 8):
				c |= (ord(data[2+3*pixel_index]) >> bit_index & 1) << pixel_index
			output += chr(c)

		# Green byte
		output += '\xFF'
		for bit_index in range(7, 0, -1):
			c = 0x00
			for pixel_index in range(0, 8):
				c |= (ord(data[1+3*pixel_index]) >> bit_index & 1) << pixel_index
			output += chr(c)

		# Red byte
		output += '\xFF'
		for bit_index in range(7, 0, -1):
			c = 0x00
			for pixel_index in range(0, 8):
				c |= (ord(data[3*pixel_index]) >> bit_index & 1) << pixel_index
			output += chr(c)


		return output

	def draw(self, data, width):
		"""
		Draw a portion of an image frame to LED strips.
		@param data Image data, as a 1D, 8bit RGB array.
		@param width Width of the image, in pixels
		"""

		s = ''
		
		# for each 'row' in the data, assemble a byte stream for it.
		for row in range(0,len(data)/3/width):
			start_index = (width*row + self.offset)*3
			s += self.RgbRowToStrips(data[start_index:start_index+24])

		for x in range(0, len(s)/64): # TODO: What this means?
			t = s[64 * x : (64 * x) + 64]

			self.ser.write(t)

		# TODO: Why does 20 work? it make a'no sense.
                # 1 does not work with the listener.
		for i in range(0,20):
			self.ser.write('\x00')

if __name__ == "__main__":
	parser = optparse.OptionParser()
	parser.add_option("-p", "--serialport", dest="serial_port",
		help="serial port (ex: /dev/ttyUSB0)", default="/dev/tty.usbmodel12341")
	parser.add_option("-l", "--length", dest="strip_length",
		help="length of the strip", default=160, type=int)

	(options, args) = parser.parse_args()

	strip = LedStrips(0)
        strip.connect(options.serial_port)

        image_width = 8 # width of the picture index

	i = 0
	j = 0
	while True:
		data = ''
		for row in range (0, options.strip_length):
			for col in range (0, image_width):
				if j == 0:
					data += chr(0x0) # B
					data += chr(0x0) # B
					data += chr(0x0) # B
				else:
					if ((row+j)%3 == 0):
						data += chr(j) # B
						data += chr(0) # B
						data += chr(0) # B
					if ((row+j)%3 == 1):
						data += chr(0) # B
						data += chr(j) # B
						data += chr(0) # B
					if ((row+j)%3 == 2):
						data += chr(0) # B
						data += chr(0) # B
						data += chr(j) # B

		i = (i+1)%20
                if i == 0:
			j = (j+1)%255


	        strip.draw(data, image_width)
