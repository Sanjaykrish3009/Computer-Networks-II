import pickle, wave, pyaudio, struct

class AudioStream:
	def __init__(self,stream):
		self.val = stream
		self.start=0
		if stream =="1":
			self.CHUNK = 512

		else:
			self.open = True
			self.rate = 44100
			self.CHUNK = 512
			self.channels = 2
			self.format = pyaudio.paInt16
			self.audio = pyaudio.PyAudio()
			
		self.frame_number = 0
	
	def frame_number(self):
		return self.frame_number

	def go_to_nextframe(self):
		if self.val=="1":
			if self.start==0:
				self.wf = wave.open("temp.wav", 'rb')
				self.start=1
			
			data = self.wf.readframes(self.CHUNK)
			a = pickle.dumps(data)
			message = struct.pack("Q",len(a))+a
			self.frame_number +=1
			return message

		else:
			if self.start ==0:
				self.wf = self.audio.open(format=self.format,
											channels=self.channels,
											rate=self.rate,
											input=True,
											frames_per_buffer = self.CHUNK)
			

				self.wf.start_stream()
				self.start=1
			data = self.wf.read(self.CHUNK)
			a = pickle.dumps(data)
			message = struct.pack("Q",len(a))+a
			self.frame_number+=1
			return message

		

	
	