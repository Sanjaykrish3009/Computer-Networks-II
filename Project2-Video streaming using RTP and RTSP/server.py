from random import randint
import threading, socket

from VideoStream import VideoStream
from Audiostream import AudioStream
from Rtpmodule import RtpPacket

import cv2, os, sys

class Server:
	
	INIT, READY, PLAYING = 1,2,3
	present_state = INIT
	Ack,connection_error = 0, 1

	SETUP,RESET,PLAY,PAUSE,TEARDOWN = 'SETUP','RESET','PLAY','PAUSE','TEARDOWN'

	
	def __init__(self, client_socket,client_addr):
		self.server_socket = client_socket
		self.client_addr = client_addr[0]
		self.client_port = client_addr[1]
		self.filename=None
		
	def start(self):
		threading.Thread(target=self.receive_req).start()
	
	def receive_req(self):

		ClientNameMsg = self.server_socket.recv(256).decode('utf-8')
		print(ClientNameMsg," joined")
		self.stream = self.server_socket.recv(256).decode('utf-8')

		if self.stream == "1":
			reply = "no"
			while(reply=="no"):
				self.filename = self.server_socket.recv(256).decode('utf-8')

				if os.path.exists(self.filename):
					reply = "yes"

				self.server_socket.send(reply.encode('utf-8'))

		elif self.stream == "2":
			self.filename = self.server_socket.recv(256).decode('utf-8')

 
		while True:            
			info = self.server_socket.recv(256)
			if info:
				info = info.decode('utf-8')
				print ("Data received: ")
				self.processing_req(info)
	
	def processing_req(self, data):
		# Get the request type
		req = data.split('\n')
		reqType = req[0].split(' ')[1]
		seq = req[0][-1]

		# Process SETUP request
		if reqType == self.SETUP:

			if self.present_state == self.INIT:
				print("SETUP request received!\n")
				self.present_state = self.READY
			
				if os.path.exists("temp.wav"):
					os.remove("temp.wav")
				command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(self.filename,'temp.wav')
				os.system(command)

				self.video_streaming = VideoStream(self.stream,self.filename)
				self.audio_streaming = AudioStream(self.stream)

				# Get the RTP/UDP port from the last line
				self.video_port= req[1].split(' ')[1]
				self.audio_port = req[2].split(' ')[1]
				self.audio_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

				# Generate a randomized RTSP session ID
				self.session = randint(1000,100000)
				self.send_ack(self.Ack, seq)

				try:
					self.audio_socket.bind(("",int(self.audio_port )))
				except:
					print("Cannot bind address to port")

				self.audio_socket.listen(5)
				if self.stream =="1":
					self.rtp_audio_socket,addr = self.audio_socket.accept()

				self.rtp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				self.rtp_video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 10000000)

		elif reqType == self.RESET:
			if self.present_state == self.PLAYING or self.present_state == self.READY:
				print("RESET request received!\n")
				self.present_state = self.READY
				self.event.set()
				
				if os.path.exists("temp.wav"):
					os.remove("temp.wav")
				command = "ffmpeg -i {} -ab 160k -ac 2 -ar 44100 -vn {}".format(self.filename,'temp.wav')
				os.system(command)

				self.video_streaming = VideoStream(self.stream,self.filename)
				self.audio_streaming = AudioStream(self.stream)
				self.send_ack(self.Ack, seq)
		
		elif reqType == self.PLAY:
			if self.present_state == self.READY:
				print("PLAY request received!\n")
				self.present_state = self.PLAYING
				self.send_ack(self.Ack, seq)
				
				self.event = threading.Event()
				threading.Thread(target=self.video_stream).start()
				threading.Thread(target=self.audio_stream).start()
		
		elif reqType == self.PAUSE:
			if self.present_state == self.PLAYING:
				print("PAUSE request received!\n")
				self.present_state = self.READY
				self.event.set()
				self.send_ack(self.Ack, seq)

		elif reqType == self.TEARDOWN:
			print("TEARDOWN request received!\n")
			self.event.set()
			self.send_ack(self.Ack, seq)
			self.video_streaming.cap.release()
			self.rtp_video_socket.close()
			if self.stream == "1":
				self.rtp_audio_socket.close()

	def send_ack(self, Acknowledgment, seq):
		"""Send RTSP reply to the client."""
		if Acknowledgment == self.Ack:
			ack = 'Sending Acknowledgment with sequence no: ' + seq + '\nSession ID: ' + str(self.session)
			ack = ack.encode('utf-8')
			self.server_socket.send(ack)
		
		elif Acknowledgment == self.connection_error:
			print("CONNECTION ERROR")

	def video_stream(self):
		
		if self.rtp_video_socket:
			while True:
				self.event.wait(0.027) 
				if self.event.isSet(): 
					break 

				video_frame = self.video_streaming.go_to_nextframe()
				frameNumber = self.video_streaming.frame_number()
				self.rtp_video_socket.sendto(self.create_rtp_packet(frameNumber,video_frame),(self.client_addr, int(self.video_port))) # Converted byte code is sending to server(serverip:serverport)
		
		cv2.destroyAllWindows() 


	def audio_stream(self):

		if self.stream =="2":
			self.rtp_audio_socket,addr = self.audio_socket.accept()
		
		if self.rtp_audio_socket:
			while True:
				self.event.wait(0.01) 
				if self.event.isSet(): 
					break 

				audio_frame = self.audio_streaming.go_to_nextframe()
				self.rtp_audio_socket.sendall(audio_frame)

		cv2.destroyAllWindows() 	
			

	def create_rtp_packet(self, sequence_no,payload):
		V, P, E, cc, M, pt, seq, ssrc = 2, 0, 0, 0, 0, 26, sequence_no, 0		
		rtpPacket = RtpPacket()
		rtpPacket.encode(V, P, E, cc, seq, M, pt, ssrc, payload)		
		return rtpPacket.get_packet()
		

if __name__ == "__main__":

	try:
		SERVER_PORT = int(sys.argv[1])
	except:
		print("[FORMAT: Server.py Server_port]\n")
	rtsp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	rtsp_server_socket.bind(('', SERVER_PORT))
	rtsp_server_socket.listen(5)        

	while True:
		client_socket,client_addr = rtsp_server_socket.accept()
		Server(client_socket,client_addr).start()		
