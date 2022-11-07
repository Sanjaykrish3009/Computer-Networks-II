import socket, threading
from Rtpmodule import RtpPacket
import cv2, pickle, pyaudio, struct,time
import kivy
kivy.require('1.0.7')
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.graphics.texture import Texture

class Client(Widget):
	INIT, READY, PLAYING = 1,2,3
	SETUP, RESET, PLAY, PAUSE, TEARDOWN = 1,2,3,4,5
	present_state = INIT
	message = ObjectProperty(None)

	def __init__(self,serveraddr, serverport, videoport, audioport):
		super(Client,self).__init__()
		self.serveraddr = serveraddr
		self.serverPort = int(serverport)
		self.videoport = int(videoport)
		self.audioport = int(audioport)
		self.connect()
		self.Seq_no, self.sn_id,self.sent_req,self.ack_exit = 0,0,-1,0
	
				
	def connect(self):
		self.rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.rtsp_socket.connect((self.serveraddr, self.serverPort))
		except:
			print("Connection to Server Failed")

	def client_details(self,screen_manager):
		self.screen_manager = screen_manager
		self.name = self.screen_manager.get_screen('LoginScreen').ids.name.text

		if self.name.isspace() or self.name == "":
			self.screen_manager.get_screen('LoginScreen').showpopup()
		else:
			self.rtsp_socket.send(self.name.strip().encode('utf-8'))
			self.screen_manager.get_screen('LoginScreen').movetonext()
			
	def stream_type(self, type):
		self.stream = str(type)
		self.rtsp_socket.send(self.stream.encode('utf-8'))

		if self.stream =="2":
			self.fileName ="Live stream"

			self.rtsp_socket.send(self.fileName.encode('utf-8'))	

	def file_details(self,screen_manager):
		self.screen_manager = screen_manager
		self.fileName = self.screen_manager.get_screen('Thirdtab').ids.file.text
		self.rtsp_socket.send(self.fileName.encode('utf-8'))	
		reply = self.rtsp_socket.recv(1024).decode('utf-8')
		
		if reply=="no":
			self.screen_manager.get_screen('Thirdtab').showpopup()
		elif reply=="yes":
			self.screen_manager.get_screen('Thirdtab').movetonext()

	def setup_video(self):
		if self.present_state == self.INIT:
			self.send_request(self.SETUP)

	def reset_video(self):
		if self.present_state == self.PLAYING or self.present_state == self.READY:
			self.send_request(self.RESET)


	def play_video(self,screen_manager):
		self.screen_manager=screen_manager

		if self.present_state == self.READY:
			time.sleep(0.04)
			threading.Thread(target=self.audio_stream).start()
			threading.Thread(target=Clock.schedule_interval(self.videostream,1.0/70.0)).start()

			self.Event = threading.Event()
			self.Event.clear()
			self.send_request(self.PLAY)

	def pause_video(self):
		if self.present_state == self.PLAYING:
			self.send_request(self.PAUSE)

	def teardown_video(self):
		self.send_request(self.TEARDOWN)

	def send_request(self, request):
		# Setup request
		if request == self.SETUP and self.present_state == self.INIT:

			#thread creation for receiving acknowledgements
			threading.Thread(target=self.receive_Ack).start()
			self.Seq_no += 1
			self.sent_req = self.SETUP 
			req = 'Sending SETUP Request with sequence no: '+str(self.Seq_no) + '\nvideo_port= ' + str(self.videoport) + '\naudio_port= ' + str(self.audioport)

		#reset request
		elif request == self.RESET and (self.present_state == self.PLAYING or self.present_state==self.READY):
			self.Seq_no += 1
			self.sent_req = self.RESET
			req = 'Sending RESET Request with sequence no: '+str(self.Seq_no) 

		# Play request
		elif request == self.PLAY and self.present_state == self.READY:
			self.Seq_no += 1
			self.sent_req = self.PLAY
			req = 'Sending PLAY Request with sequence no: '+str(self.Seq_no) 

		# Pause request
		elif request == self.PAUSE and self.present_state == self.PLAYING:
			self.Seq_no += 1
			self.sent_req = self.PAUSE
			req = 'Sending PAUSE Request with sequence no: '+str(self.Seq_no) 

		# Teardown request
		elif request == self.TEARDOWN and not self.present_state == self.INIT:
			self.Seq_no += 1
			self.sent_req = self.TEARDOWN
			req = 'Sending TEARDOWN Request with sequence no: '+str(self.Seq_no) 

		else:
			return

		# Sending request using rtsp_socket.
		print('\nRequest sent:\n' + req)
		req = req.encode('utf-8')
		self.rtsp_socket.send(req)		

	def videostream(self,*args):		
		#receiving video frames
		try:
			x=self.rtp_video_socket.recvfrom(100000000)    # Recieve byte code sent by client using recvfrom
			rtpPacket = RtpPacket()
			rtpPacket.decode(x[0])
			data= rtpPacket.get_payload()
			data=pickle.loads(data)    # All byte code is converted to Numpy Code 
			data = cv2.imdecode(data, cv2.IMREAD_COLOR)  # Decode 
			buffer = cv2.flip(data,0).tostring()
			texture = Texture.create(size=(data.shape[1],data.shape[0]),colorfmt='bgr')
			texture.blit_buffer(buffer,colorfmt='bgr',bufferfmt='ubyte')

			if self.stream=="1":
				self.screen_manager.get_screen('Fourthtab').ids.vid.texture = texture
			elif self.stream=="2":
				self.screen_manager.get_screen('Fifthtab').ids.vid.texture = texture

		except:
			# Stop after requesting RESET or PAUSE or TEARDOWN
			if self.Event.isSet(): 
				return
			#checking exit acknowledgent
			if self.ack_exit == 1:
				self.rtp_video_socket.shutdown(socket.SHUT_RDWR)
				self.rtp_video_socket.close()
				return
		cv2.destroyAllWindows()  

	def audio_stream(self):

		#receiving audio frames
		if self.stream == "2":
			socket_address = (self.serveraddr,self.audioport)
			print('server listening at',socket_address)
			self.rtp_audio_socket.connect(socket_address) 
			print("CLIENT CONNECTED TO",socket_address)

		p = pyaudio.PyAudio()
		CHUNK = 1024
		stream = p.open(format=pyaudio.paInt16,
						channels=2,
						rate=44100,
						output=True,
						frames_per_buffer=CHUNK)
						
		audio_frame = b""
		sizeof_payload = struct.calcsize("Q")
		while True:
			try:
				while len(audio_frame) < sizeof_payload:
					packet = self.rtp_audio_socket.recv(5120) # 4K
					if not packet: break
					audio_frame+=packet

				size = audio_frame[:sizeof_payload]
				audio_frame = audio_frame[sizeof_payload:]
				msg_size = struct.unpack("Q",size)[0]
				while len(audio_frame) < msg_size:
					packet = self.rtp_audio_socket.recv(5120)
					audio_frame+=packet
				frame_data = audio_frame[:msg_size]
				audio_frame  = audio_frame[msg_size:]
				frame = pickle.loads(frame_data)
				stream.write(frame)

			except:
				# Stop after requesting RESET or PAUSE or TEARDOWN
				if self.Event.isSet(): 
					break
				#checking exit acknowledgent
				if self.ack_exit == 1:
					self.rtp_video_socket.shutdown(socket.SHUT_RDWR)
					self.rtp_video_socket.close()
					break
		cv2.destroyAllWindows() 
		
	def receive_Ack(self):

		#Receiving acknowlegment from server
		while True:
			acknowledge = self.rtsp_socket.recv(1024)

			if acknowledge: 
				acknowledge = acknowledge.decode('utf-8')
				self.processing_state(acknowledge)

			if self.sent_req == self.TEARDOWN:
				self.rtsp_socket.shutdown(socket.SHUT_RDWR)
				self.rtsp_socket.close()
				break

	def processing_state(self, ack):

	    #changing present state after receiving acknowledgement
		lines = ack.split('\n')
		seq_no, sn  = int(lines[0].split(' ')[-1]), int(lines[1].split(' ')[-1])

		if self.sn_id == 0:
				self.sn_id = sn

		if seq_no == self.Seq_no and self.sn_id == sn:
				
			if self.sent_req == self.SETUP:
				self.present_state = self.READY
				self.Video_Audio_Ports()

			elif self.sent_req == self.PLAY:
				self.present_state = self.PLAYING

			elif self.sent_req == self.PAUSE or self.sent_req == self.RESET:
				self.present_state = self.READY
				self.Event.set()

			elif self.sent_req == self.TEARDOWN:
				self.present_state = self.INIT
				self.ack_exit = 1 


	def Video_Audio_Ports(self):

		#creating sockets using UDP and RTP Protocols for video and audio streaming
		self.rtp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.rtp_audio_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

		# Set the timeout value of the socket to 0.5sec
		self.rtp_video_socket.settimeout(0.5)
		try:
			self.rtp_video_socket.bind(("", self.videoport))
		except:
			print("Unable to Bind to Video Port")

		self.rtp_audio_socket.settimeout(1)
		if self.stream == "1":
			socket_address = (self.serveraddr,self.audioport)
			print('server listening at',socket_address)
			self.rtp_audio_socket.connect(socket_address) 
			print("CLIENT CONNECTED TO",socket_address)

