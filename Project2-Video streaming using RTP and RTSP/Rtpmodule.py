from time import time
HEADER_SIZE = 12

class RtpPacket:	
	header = bytearray(HEADER_SIZE)
	
	def __init__(self):
		pass
		
	def encode(self, V, P, E, cc, seq, M, pt, ssrc, pl):
		timestamp = int(time())
		H = bytearray(HEADER_SIZE)

		H[0] = (H[0] | V << 6) & 0xC0; 
		H[0] = (H[0] | P << 5); 
		H[0] = (H[0] | E << 4); 
		H[0] = (H[0] | (cc & 0x0F)); 
		H[1] = (H[1] | M << 7); 
		H[1] = (H[1] | (pt & 0x7f)); 
		H[2] = (seq & 0xFF00) >> 8; 
		H[3] = (seq & 0xFF); 
		H[4] = (timestamp >> 24); 
		H[5] = (timestamp >> 16) & 0xFF;
		H[6] = (timestamp >> 8) & 0xFF;
		H[7] = (timestamp & 0xFF);
		H[8] = (ssrc >> 24); 
		H[9] = (ssrc >> 16) & 0xFF;
		H[10] = (ssrc >> 8) & 0xFF;
		H[11] = ssrc & 0xFF
		
		self.header = H
		self.payload = pl
		
	def decode(self, byte_stream):
		self.header = bytearray(byte_stream[:HEADER_SIZE])
		self.payload = byte_stream[HEADER_SIZE:]

	def get_packet(self):
		return self.header + self.payload
	
	def get_payload(self):
		return self.payload
		