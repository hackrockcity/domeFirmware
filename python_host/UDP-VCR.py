import socket
import time
import sys
import Queue
import multiprocessing
import LedStrips

# UDP settings
host = "0.0.0.0"
port = 58082
buffer_size = 19201

# Image settings
image_height = 160
image_width = 40

frameSize = (image_width * image_height * 3) + 1

class Recorder:

	recFile = None
	recordedFrames = 0
	lastReceived = time.time()
	timeout = 6
	recording = False
	avgFrameRate = 0

	def __init__(self, sock):
		
		self.sock = sock

		# Open the data file
		self.recFile = open("recfile.dat", "w")

	def record(self):

		# Set socket to blocking, one second timeout
		self.sock.setblocking(1)
		self.sock.settimeout(1)
		
		self.recording = True

		frame_time = time.time()
		total_time = time.time()

		while self.recording == True:

			try:
				
				# Receive the data from the socket
				data, addr = sock.recvfrom(buffer_size)

				self.lastReceived = time.time()

				# If the data is valid, write the data to the recording file
				if self.process_data(data):
					self.write_frame(data)
					self.recordedFrames += 1

				# Every 30 frames, output framerate data
				if self.recordedFrames % 30 == 0:
					frame_rate = 30 / (time.time() - frame_time)
					frame_time = time.time()
					self.avgFrameRate = (self.avgFrameRate + frame_rate) / 2

			except socket.timeout:
				# Stopped receiving UDP data, get ready to stop the recorder
				print "Timed out waiting for UDP data. Last received %s seconds ago." % int(time.time() - self.lastReceived)

				if time.time() - self.lastReceived > self.timeout:
					self.stop()

		return self.avgFrameRate
				
	def process_data(self, data):
		if not data:
			print "no data."
			return

		if data[0] != '\x01':
			print "bad header, expected=%i, got=%i"%(1, ord(data[0]))
			return

		expected_length = image_width*image_height*3+1
		if len(data) != expected_length:
			print "bad data length, expected %i, got %i"%(expected_length, len(data))
			return

		return True

	def write_frame(self, data):
		self.recFile.write(data)
		
	def stop(self):
		self.recFile.close()
		self.recording = False

		print "Stopped recording after %i frames." % self.recordedFrames


class Playback:

	playFile = None
	data = None
	numFrames = None
	currentFrame = 0
	frameRate = 0
	loops = 1
	loopNum = 0

	strips = []

	blinkyboards = [
		['/dev/cu.usbmodem66661', 0]
	]	

	new_data_event = multiprocessing.Event()
	draw_event = multiprocessing.Event()
	image_data = multiprocessing.Array('c', image_width*image_height*3)

	# Initiate a player with the playback framerate and the number of loops to do
	# Set loops to -1 for infinite playback
	def __init__(self, avgFrameRate, loops):
		# Open the recorded file
		self.playFile = open("recfile.dat", "r")

		# Load the recorded frames into RAM and close the file.
		# This will take a lot of RAM. About 500kb per second.
		self.data = self.playFile.read()
		self.playFile.close()

		self.numFrames = (len(self.data) / frameSize)

		self.frameRate = avgFrameRate
		self.loops = loops

		# print "Loaded %i frames" % self.numFrames

		# Spawn a new thread for every BB8 listed in blinkyboards[]
		for blinkyboard in self.blinkyboards:
			strip = threadedLedStrips(blinkyboard[0], blinkyboard[1],
				self.image_data, self.new_data_event, self.draw_event)
			strip.start()
			self.strips.append(strip)

		time.sleep(.5)

	def play(self):

		# Die if no frames recorded
		if self.numFrames == 0:
			self.stop()
			return

		self.playing = True
		frame_time = time.time()

		while self.playing == True:
			# Grab the current frame of data from the huge heap of data loaded from the file
			startByte = self.currentFrame * frameSize
			endByte = startByte + frameSize
			idata = self.data[startByte : endByte]
			
			start_time = time.time()
			#send_draw_start_time = time.time()
			
			# Clock out the previous frame
			self.new_data_event.clear()
			self.draw_event.set()
			#send_draw_time = time.time() - send_draw_start_time

			# Load in the next frame
			load_frame_start_time = time.time()
			self.image_data[:] = idata[1:]

			load_frame_time = time.time() - load_frame_start_time

		#	print "Send data--"
			send_data_start_time = time.time()
			self.draw_event.clear()
			self.new_data_event.set()
			send_data_time = time.time() - send_data_start_time

			# Print current loop and frame position, along with frame rate
			if self.currentFrame % 30 == 0:
				frame_rate = self.currentFrame / (time.time() - frame_time)
				print "\tLoop: %i Frame: %i Frame rate: %.2f" % (self.loopNum, self.currentFrame, frame_rate)

			# Insert an appropriate delay so that the output frame rate tracks the avg requested frame rate
			if time.time() - start_time < (1.0 / self.frameRate):
				time.sleep((1.0 / self.frameRate) - (time.time() - start_time))

			self.currentFrame +=1

			# We've played all of the available frames!
			if self.currentFrame >= self.numFrames:
				self.end()

	def end(self):
		if self.loopNum == self.loops:
			self.stop()
		else:
			self.loopNum += 1
			self.currentFrame = 0

	def stop(self):
		# Terminate the playback!
		self.playing = False
		for strip in self.strips:
			strip.terminate()

		print "Stopped playing after %i loops of %i/%i frames" % (self.loops, self.currentFrame, self.numFrames)


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
			# Wait for new_data_event semaphore
			self.new_data_event.wait()

			# Load data into strip
			self.strip.load_data(self.data)

			# Wait for draw_event semaphore
			self.draw_event.wait()
			
			# Clock out the flip bits (0x00)
			self.strip.flip()

if __name__ == "__main__":

	avgFrameRate = 30

	if len(sys.argv) > 1 and sys.argv[1] == "-r":
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind((host,port))

		# Start the recording
		recorder = Recorder(sock)
		avgFrameRate = recorder.record()

	# Recording is over, start playback
	player = Playback(avgFrameRate, -1)
	while True:
		player.play()



