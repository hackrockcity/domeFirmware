import serial
import time
import struct
import binascii

device = "/dev/tty.usbmodem12341"
ser = serial.Serial(device, 1000000, timeout=0)

num_leds = 32 * 5
pixels = []
for x in range(0, num_leds): pixels.append([0,0,0])
sprite = 0

latch = [0x00 for x in range(0, 1)]

level = 0
level_dir = 1

def translate_pixel(c):
	c |= 0x80
	mask = 0x80
	p = ''

	while(mask):
		if (c & mask):
			p += chr(0xFF)

		else:
			p += chr(0x00)

		mask >>= 1

	return p


for q in range(0, 31):
	#pixels[sprite] = [0,0,0]
	#sprite = (sprite - 1 + num_leds) % num_leds
	for x in range(0, num_leds - 1):
		pixels[x] = [level, level, level]
	
	if level_dir > 0: level += 1
	else: level -= 1

	if (level == 0x7f): level_dir = -1
	elif level == 0: level_dir = 1

	s = ''
	for p in pixels:
		
		s += translate_pixel(p[1])
		s += translate_pixel(p[0])
		s += translate_pixel(p[2])

	for x in range(0, 60):
		t = s[64 * x : (64 * x) + 64]


		
		ser.write(t)
		#time.sleep(0.01)
	#time.sleep(1)
	ser.write(''.join([chr(x) for x in latch]))
	print time.time()
		