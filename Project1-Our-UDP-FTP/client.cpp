#include <iostream>
#include <sys/socket.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <netdb.h>
#include <fstream>
#include <vector>
#include <thread>
#include <unistd.h>
#include <sys/stat.h>
#include <netinet/in.h>

#define PAYLOAD 8192
#define PORTNO 5050

using namespace std;

class UDPClient
{
    private:
        struct hostent* host;
        const char* filename;
        int server_socket;
        int file_size;
        int N;
        int Total_packets;
        struct sockaddr_in server_addr ;
        unsigned int len;
        char*file_Memory;
        int *marksent;
	    int sent_count;
	    int Noofpackets;
        struct ourUDPFTP
        {
            int seq_number;
            unsigned int ack_no;
            int size;
            bool ack_flag;
            char buffer[PAYLOAD];
        }packet;
        struct ourUDPFTP*file_sent;
        void getFile(const char* name);
        void ThrdFunc();

    public:
        void ErrorMsg(const char* msg);
        void getHostByName(char* hostname);
        void setSocket();
        void setServerAddr(int );
        void sendTo(const char*name);
};

void UDPClient::getFile(const char* name)
{
    filename = name;

    ifstream inputfile(filename,ios_base::binary);
    inputfile.seekg(0,ios::end);
    file_size = inputfile.tellg();

    file_Memory=new char[file_size];
    inputfile.seekg(0,ios::beg);
    inputfile.read(&file_Memory[0],file_size);
    inputfile.close();
}

void UDPClient::ErrorMsg(const char* msg)
{
	cerr << msg << endl;
	exit(1);    
}

void UDPClient::getHostByName(char* hostname)
{
    host = gethostbyname(hostname);
    if(host==NULL) ErrorMsg("Such Host is not present!");
}

void UDPClient::setSocket()
{
    server_socket = socket(AF_INET,SOCK_DGRAM,0);
    if(server_socket < 0) ErrorMsg("Client Socket Opening Failed!");
}

void UDPClient::setServerAddr(int portNo)
{
    bzero((char*)&server_addr,sizeof(server_addr));
	server_addr.sin_family = AF_INET;
	bcopy((char*)host->h_addr,(char*)&server_addr.sin_addr.s_addr,host->h_length);
	server_addr.sin_port = htons(portNo);
    len=sizeof(server_addr);
}

void UDPClient::ThrdFunc()
{
    while(sent_count!=Noofpackets||N!=0)
    {
        ourUDPFTP ackpac;
        recvfrom(server_socket,&ackpac,sizeof(ackpac),0,(struct sockaddr *)&server_addr,&len);

        if(ackpac.seq_number<0)
        {
            N=ackpac.ack_no;
            break;
        }
        if(marksent[ackpac.seq_number]==0)  
        {
            marksent[ackpac.seq_number]=1;
	    sent_count++;
        }
    }

}


void UDPClient::sendTo(const char*name)
{
    N=1;
    getFile(name);
    sendto(server_socket,&file_size,sizeof(file_size),0,(struct sockaddr *)&server_addr,len);
    cout << "Size of the file sent: " << file_size << endl;
    Noofpackets = file_size/PAYLOAD;
    marksent=new int [Noofpackets+1];

    file_sent = new ourUDPFTP[Noofpackets+1];
    sent_count=0;
    for(int i=0;i<Noofpackets+1;i++)
    {
        int start;
        ourUDPFTP data;
        memset(&data,0,sizeof(ourUDPFTP));
        marksent[i]=0;

        if(i==Noofpackets)
        {
            int remaining_data= file_size%PAYLOAD,start=Noofpackets*PAYLOAD;

            memcpy(data.buffer,&file_Memory[start],remaining_data);
            data.seq_number=i;
            data.size=remaining_data;
            data.ack_no=0;
            file_sent[i]=data;
        }
        else
        {
            start=i*PAYLOAD;
            memcpy(data.buffer,&file_Memory[start],PAYLOAD);

            data.seq_number=i;
            data.size=PAYLOAD;
            data.ack_no=0;
            file_sent[i]=data;
        }
            
    }
    int n_th=1,index=0;
    std::thread rv_threads[n_th];
    

    for(int i=0;i<n_th;i++)
    {
        rv_threads[i]=std::thread(&UDPClient::ThrdFunc,this);
    }

   
    while(N==1)
    {
        int j=0;
       //usleep(3000);
        for(int i=index;i<Noofpackets+1;i++)
        {   	
            if(marksent[i]==0)
            {   
                if(j==0)
                {
                    j=1;
                    index=i;
                }

                //usleep(600);                
                sendto(server_socket,&file_sent[i],sizeof(ourUDPFTP),0,(struct sockaddr *)&server_addr,len); 
                Total_packets++;
            }

        }
    }

    for(int i=0;i<n_th;i++)
    {
        rv_threads[i].join();
    }

   //double packet_loss = float(Total_packets-Noofpackets-1)/float(Total_packets);
   //cout << "Packet loss percent:" << packet_loss*100 << endl;
}

int main(int argc, char* argv[])
{
    UDPClient client;
    if(argc < 4)    client.ErrorMsg("Please provide proper input");
    client.getHostByName(argv[2]);	
    client.setSocket();	
	int portno = atoi(argv[3]);
    client.setServerAddr(portno);
    client.sendTo(argv[1]);
    
	return 0;
}

