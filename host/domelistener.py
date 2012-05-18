import socket
import time
import Queue
import multiprocessing
import LedStrips

# UDP settings
host = "0.0.0.0"
port = 58082
buffer_size = 200000

# Image settings
image_height = 160
image_width = 25

# Serial port settings
strip_names = [
	['/dev/tty.usbmodem12341', 0],
	['/dev/tty.usbmodem121',   8],
	['/dev/tty.usbmodem122',   16],
]


class threadedLedStrips(multiprocessing.Process):

	def __init__(self, port_name, offset,
			data_array, new_data_event, draw_event):
		self.port_name = port_name
		self.offset = offset

		self.strip = LedStrips.LedStrips(image_width, offset)
		self.strip.connect(port_name)

		self.data = data_array
		self.new_data_event = new_data_event
		self.draw_event = draw_event

		multiprocessing.Process.__init__(self, target=self.run)

	def run(self):
		while True:
			# Wait for new data, then load it into the strip
#			print " %i wait for data"%self.offset
			self.new_data_event.wait()
#			print " %i got data"%self.offset
			self.strip.load_data(self.data)

			# Wait for a write event, then signal the frame to flip over
#			print " %i wait for draw--"%self.offset
			self.draw_event.wait()
#			print " %i got draw--"%self.offset
			self.strip.flip()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host,port))

strips = []

new_data_event = multiprocessing.Event()
draw_event = multiprocessing.Event()
image_data = multiprocessing.Array('c', image_width*image_height*3)

for strip_name in strip_names:
	strip = threadedLedStrips(strip_name[0], strip_name[1],
		image_data, new_data_event, draw_event)
	strip.start()
	strips.append(strip)

start_time = time.time()
frame_count = 0
while 1:
	data, addr = sock.recvfrom(buffer_size)
	
	if not data:
		print "no data."
		continue

	if data[0] != '\x01':
		print "bad header, expected=%i, got=%i"%(1, ord(data[0]))
		continue

	expected_length = image_width*image_height*3+1
	if len(data) != expected_length:
		print "bad data length, expected %i, got %i"%(expected_length, len(data))
		continue

#	print "Send draw"
	# Clock out the previous frame
	new_data_event.clear()
	draw_event.set()

	# Load in the next frame
	for pos in range(0, image_width*image_height*3):
		image_data[pos] = data[pos+1]

#	print "Send data--"
	draw_event.clear()
	new_data_event.set()

	frame_count = (frame_count + 1) % 30
	if (frame_count == 0):
		print "Frame rate: %3.1f"%(30/(time.time() - start_time))
		start_time = time.time()

