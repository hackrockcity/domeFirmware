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
]



class threadedLedStrips(multiprocessing.Process):
	q = multiprocessing.Queue(2)

	def __init__(self, port_name, offset):
		self.port_name = port_name
		self.offset = offset

		multiprocessing.Process.__init__(self, target=self.run)
		self.strip = LedStrips.LedStrips(offset)
		self.strip.connect(port_name)

	def run(self):
		while True:
			command = self.q.get()
			self.strip.draw(command,image_width)


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host,port))

strips = []

for strip_name in strip_names:
	strip = threadedLedStrips(strip_name[0], strip_name[1])
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

	for strip in strips:
		if strip.q.full():
			print "dropped a frame!"
		else:
			strip.q.put(data[1:])

	frame_count = (frame_count + 1) % 30
	if (frame_count == 0):
		print "Frame rate: %3.1f"%(30/(time.time() - start_time))
		start_time = time.time()
		
