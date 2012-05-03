import socket
import time
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
	['/dev/tty.usbmodem63',    8],
	['/dev/tty.usbmodem64',    16],
]

strips = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host,port))

for strip_name in strip_names:
	strip = LedStrips.LedStrips(strip_name[1])
	strip.connect(strip_name[0])
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
		strip.draw(data[1:], image_width)

	frame_count = (frame_count + 1) % 30
	if (frame_count == 0):
		print "Frame rate: %3.1f"%(30/(time.time() - start_time))
		start_time = time.time()
		
