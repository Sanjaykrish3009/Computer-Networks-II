#include <iostream>
#include <sys/socket.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <string.h>
#include <netdb.h>
#include <fstream>
#include <sys/time.h> 
#include <vector>
#include <unistd.h>
#include <thread>
#include <mutex>

#define PAYLOAD 8192
#define PORTNO 5050

using namespace std;


struct sockaddr_in server_addr,client_addr;

class UDPServer
{
	private:
		int server_socket,file_size;
		struct sockaddr_in server_addr;
		unsigned int len;
		int packets_received=0;
		int Noofpackets;
		struct ourUDPFTP
        {
            int seq_number;
            unsigned int ack_no;
			int size;
            bool ack_flag;
			char buffer[PAYLOAD];
        };
		int *markreceive;
		struct ourUDPFTP*file_received;
		struct timeval start,end1,end2;
		void ThrdFunc();
		mutex Lock;

	public :
		void ErrorMsg(const char* msg);
		void setSocket();
		void bindAddr(int portNo);
		void recvFrom();
};

void UDPServer::ErrorMsg(const char * msg)
{
	cerr << msg << endl;
	exit(1);
}

void UDPServer::setSocket()
{
    server_socket = socket(AF_INET,SOCK_DGRAM,0);
    if(server_socket < 0) ErrorMsg("Server Socket Opening Failed!");
	cout << "Server socket created" << endl;
}

void UDPServer::bindAddr(int portNo)
{
	bzero((char*)&server_addr,sizeof(server_addr));
	server_addr.sin_family = AF_INET;
        server_addr.sin_addr.s_addr = INADDR_ANY;
	server_addr.sin_port = htons(portNo);
	
	
	if(bind(server_socket, (const sockaddr*) &server_addr, sizeof(server_addr))<0)  ErrorMsg("Problem occured while binding server socket to an address");
	
	cout << "Server Socket is succesfully binded" << endl;
	len=sizeof(server_addr);
}

void UDPServer::ThrdFunc()
{
	while(Noofpackets+1!=packets_received)
	{
		ourUDPFTP data;
		recvfrom(server_socket,&data,sizeof(data),0,(struct sockaddr *)&server_addr,&len);

		if(markreceive[data.seq_number]==0)
		{
			file_received[data.seq_number]=data;
			packets_received++;
	 	}
	    markreceive[data.seq_number]=1;
	}
}

void UDPServer::recvFrom()
{
	int n = recvfrom(server_socket,&file_size,sizeof(file_size),0,(struct sockaddr *)&server_addr,&len);
	gettimeofday(&start,NULL);

	if(n<0) ErrorMsg("Error in receiving message");

	Noofpackets= file_size/PAYLOAD;
	int index=0;
	markreceive=new int[Noofpackets+1];
	
	for(int i=0;i<Noofpackets+1;i++)
	{
		markreceive[i]=0;
	}
	file_received = new ourUDPFTP[Noofpackets+1];

    std::thread threads,threads2;

    threads=std::thread(&UDPServer::ThrdFunc,this);
 
	while(1)
	{   
		int j=0;

		for(int i=0;i<Noofpackets+1;i++)
		{
			if(markreceive[i]==1)
			{
				if(j==0)
				{
					index=i;
					j=1;
				}
				markreceive[i]=2;  //Acknowledges that client has received this 'ack'
				//usleep(100);
				ourUDPFTP ackpac;
				memset(&ackpac,0,sizeof(ourUDPFTP));
				ackpac.ack_no=1;
				ackpac.seq_number=i;
				sendto(server_socket,&ackpac,sizeof(ackpac),0,(struct sockaddr *)&server_addr,len);
			}
		}
		//usleep(500);

		//Re-sending Acknowledgements for better reliability
		
		for(int i=0;i<Noofpackets+1;i++)
		{
			if(markreceive[i]==1)
			{
				if(j==0)
				{
					index=i;
					j=1;
				}
				markreceive[i]=2;
				//usleep(100);
				ourUDPFTP ackpac;
				memset(&ackpac,0,sizeof(ourUDPFTP));
				ackpac.ack_no=1;
				ackpac.seq_number=i;
				sendto(server_socket,&ackpac,sizeof(ackpac),0,(struct sockaddr *)&server_addr,len);
			}
		}

        
        if(packets_received==Noofpackets+1)
		{
			//usleep(100000);
			ourUDPFTP ackpac;
			memset(&ackpac,0,sizeof(ourUDPFTP));
			ackpac.seq_number=-1;  // Indicates end of file transfer and all packets are received.

			ackpac.ack_no=0;
			//sending more empty packets to ensure that client acknowledges the end of file transfer
			sendto(server_socket,&ackpac,sizeof(ackpac),0,(struct sockaddr *)&server_addr,len);   
			sendto(server_socket,&ackpac,sizeof(ackpac),0,(struct sockaddr *)&server_addr,len);   
		    sendto(server_socket,&ackpac,sizeof(ackpac),0,(struct sockaddr *)&server_addr,len);   		
			sendto(server_socket,&ackpac,sizeof(ackpac),0,(struct sockaddr *)&server_addr,len);   
			cout << "Whole File Received" << endl;
			break;
		}
	}

	threads.join();
	ofstream Outfile;
	Outfile.open("received_file");

	for(int i=0;i<Noofpackets+1;i++)	Outfile.write((file_received[i].buffer),file_received[i].size);	
	gettimeofday(&end2,NULL);

	double total_time_taken = (end2.tv_sec-start.tv_sec)*1000000 + end2.tv_usec-start.tv_usec;

    cout << "Size of the file received: " << file_size << "Bytes" << endl;
	cout << "Total Time Taken For File Transfer Using OurUDPFTP: " << total_time_taken/1000000 << " seconds" << endl;

    double Time = (float)(total_time_taken/1000000);
	double Throughput = (float)(file_size/(Time*1024*1024));

    cout << "Throughput: " << Throughput << " MBps" << endl;
}

int main(int argc, char* argv[])
{
	UDPServer server;
	server.setSocket();
	int portno = atoi(argv[1]);
	server.bindAddr(portno);
	server.recvFrom();
	return 0;
}
