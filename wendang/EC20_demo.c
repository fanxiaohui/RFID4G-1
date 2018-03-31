/***
 *  EC20_demo.c
 *	编译：arm-linux-gcc -o EC20_demo EC20_demo.c -static
 *  运行：./EC20_demo ip port
 *	eg:   ./EC20_demo 192.168.6.5 8080
 ****/

#include <stdio.h>  
#include <strings.h>  
#include <unistd.h>  
#include <errno.h>
#include <sys/types.h>  
#include <sys/socket.h>  
#include <stdlib.h>  
#include <memory.h>  
#include <arpa/inet.h>  
#include <netinet/in.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <fcntl.h> 
#include <termios.h> 
  

#define MAX_BUF 36 

//测试程序拷贝至A5 运行    ./EC20_demo ip地址 端口号 

void EC20_init(void);  
void EC20_init2(void);  
  
int main(int argc,char *argv[])  
{  
    int server_port;
    
	int sockfd;  
   	char buffer[2014];  
   	struct sockaddr_in server_addr;  
   	struct hostent *host;  
   	int nbytes;
   	int addr_len = sizeof(struct sockaddr_in); 
   
    if(3 != argc) {
        printf("./EC20_demo ip port\n ");  
    	return -1;  
    }
    
    server_port=atoi(argv[2]);
    
    /*************************************************/
    EC20_init();
    
    system("pppd call quectel-ppp &");
    
    sleep(10);
  
  
    /*******************connect()*********************/  
 	
 	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) == -1)  
   	{  
      	fprintf(stderr, "Socket Error is %s\n", strerror(errno));  
      	exit(EXIT_FAILURE);  
   	}  
   	bzero(&server_addr, sizeof(server_addr));  
   	server_addr.sin_family = AF_INET;  
   	server_addr.sin_port = htons(server_port);  
  	server_addr.sin_addr.s_addr = htonl(INADDR_ANY); 
 	
    server_addr.sin_addr.s_addr = inet_addr(argv[1]);  
  	
	if (connect(sockfd, (struct sockaddr *)(&server_addr), sizeof(struct sockaddr)) == -1)  
   	{  
      	printf("Connect failed\n");  
      	exit(0);  
   	}  
   	printf("Connect to server\n");  
   	char sendbuf[1024]={0x70,0x08,0x00,0x08,0x00,0x70,0xC0,0x00,0x00,0x5E,0x27,0x00,0x47,0x02,0x8E,0x20}; 
	char sendbuffer[1024];
  	char recvbuf[2048];
  	pid_t pid;
  	int i,len;
  	pid = fork();
  	if(pid<0)
  	{
  		perror("fork fail");
        exit(0);
  	}
  	printf("create fork success\n"); 
  	if(pid == 0)
  	{
  		printf("start send.\n");
  		while(1)
       	{
       		 
      		sleep(5);
//       		fgets(sendbuffer, sizeof(sendbuffer), stdin);  
//     		sendto(sockfd, sendbuffer, strlen(sendbuffer), 0,&server_addr, addr_len);
			len = sendto(sockfd, sendbuf, 16, 0, &server_addr, addr_len);
			if(len < 0)
			{
				printf("send fail\n");
			}else
			{
     			printf("send success\n");
   			}
   			if (strcmp(sendbuf, "exit\n") == 0)  
      			break;  
//      		memset(sendbuffer, 0, sizeof(sendbuffer));
       }
  	}else
  	{
  		
  		while(1)
       	{
       		printf("\nwait recv...\n"); 
       		len = recvfrom(sockfd, recvbuf, sizeof(recvbuf), 0, &server_addr, &addr_len);
       		for(i=0;i<len;i++){
    			printf("%02X ", recvbuf[i]);
    		}
//     		printf("recv success\n"); 
      		memset(recvbuf, 0, sizeof(recvbuf));
       	}
  	}
  
} 



/*4g modle init*/

// eg: ver=138  
// echo 138 > /sys/class/gpio/export  
int gpio_export(char * ver)  
{  
        int fd;  
        fd = open("/sys/class/gpio/export", O_WRONLY);  // write only  
        if (fd < 0) {  
                perror("gpio/export");  
                return fd;  
        }  
        write(fd, ver ,sizeof(ver));  
        close(fd);  
  
        return 0;  
}  
  
// eg: ver=138  
// echo 138 > /sys/class/gpio/unexport  
int gpio_unexport(char * ver)  
{  
        int fd;  
        fd = open("/sys/class/gpio/unexport", O_WRONLY);        // write only  
        if (fd < 0) {  
                perror("gpio/uexport");  
                return fd;  
        }  
        write(fd, ver ,sizeof(ver));  
        close(fd);  
  
        return 0;  
}  
  
/** 
 * echo out > /sys/class/gpio/pioE10/direction  
 * str  : pioE10,... 
 * 0    : sucess 
 * other: err 
 */  
int gpio_set_dir(char* str)  
{  
        int fd;  
        int len;  
        char buf[MAX_BUF];  
        len = snprintf(buf,sizeof buf,"/sys/class/gpio/%s/direction", str);  
        printf("str=%s,buf=%s\n",str,buf);  
        fd = open(buf, O_WRONLY);       // write only  
        if (fd < 0) {  
                perror("gpio/direction");  
                return fd;  
        }  
        write(fd, "out", sizeof("out"));  
        close(fd);  
  
        return 0;  
}  
  
/** 
 * echo 1 > /sys/class/gpio/pioE10/value 
 * str   :  "pioE10", ... 
 * value :  "1","0" 
 */  
int gpio_set_value(char *str, unsigned int value)  
{  
        int fd;  
        int len;  
        char buf[MAX_BUF];  
        len = snprintf(buf,sizeof buf,"/sys/class/gpio/%s/value", str);  
//      printf("buf=%s\n",buf);  
        fd = open(buf, O_RDWR);  
        if (fd < 0) {  
                perror("gpio/set_value");  
                return fd;  
        }  
        if(value)  
                write(fd, "1", sizeof("1"));  
        else  
                write(fd, "0", sizeof("0"));  
  
        close(fd);  
        return 0;  
}  

void EC20_init(void)
{
	char *io_id[2];
	io_id[0] = "pioE10";
	io_id[1] = "pioE3";
	gpio_export("138");
	gpio_export("131");
	gpio_set_dir(io_id[0]);
	gpio_set_dir(io_id[1]);
	gpio_set_value(io_id[1], 0);
	sleep(1);
	gpio_set_value(io_id[0], 1);
	sleep(1);
	gpio_set_value(io_id[1], 1);
	sleep(1);
	gpio_unexport("138");
	gpio_unexport("131");
	sleep(20);
}

void EC20_init2(void)
{
	char *io_id[2];
	io_id[0] = "pioE10";
	io_id[1] = "pioE3";
	gpio_export("138");
	gpio_set_dir(io_id[0]);
	gpio_set_value(io_id[0], 1);
	sleep(20);
	gpio_export("131");
	gpio_set_dir(io_id[1]);
	gpio_set_value(io_id[1], 0);
	sleep(1);
	gpio_set_value(io_id[1], 1);
	sleep(10);
	gpio_unexport("138");
	gpio_unexport("131");
	sleep(5);
}
