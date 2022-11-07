import cv2, pickle, os, time

class VideoStream:
	def __init__(self, streamType,filename):

		if streamType=="1":
			self.filename = filename
			self.cap = cv2.VideoCapture(self.filename) 
		else:
			self.cap = cv2.VideoCapture(0) 
			
		try:
			self.FPS = self.cap.get(cv2.CAP_PROP_FPS)
			self.TS = (0.5/self.FPS)
			self.fps,self.st,self.frames_to_count,self.cnt = (0,0,1,0)
		except:
			raise IOError
		self.frame_no = 0
	
	def frame_number(self):
		return self.frame_no

	def rescale_frame(self,frame):
		height = 537
		width = 956
		dim = (width, height)
		return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)
		
	def go_to_nextframe(self):
		ret,photo = self.cap.read()      # Start Capturing a images/video
		photo = self.rescale_frame(photo)
		ret, buffer = cv2.imencode(".jpg", photo, [int(cv2.IMWRITE_JPEG_QUALITY),50])  # ret will returns whether connected or not, Encode image from image to Buffer code(like [123,123,432....])
		x_as_bytes = pickle.dumps(buffer)       # Convert normal buffer Code(like [123,123,432....]) to Byte code(like b"\x00lOCI\xf6\xd4...")
		self.frame_no += 1
		if self.cnt == self.frames_to_count:
			try:
				self.fps = (self.frames_to_count/(time.time()-self.st))
				self.st=time.time()
				self.cnt=0
				if self.fps>self.FPS:
					self.TS+=0.001
				elif self.fps<self.FPS:
					self.TS-=0.001
				else:
					pass
			except:
				pass
		self.cnt+=1

		key = cv2.waitKey(int(1000*self.TS)) & 0xFF	
		if key == ord('q'):
			os._exit(1)
		return x_as_bytes
		

	
	