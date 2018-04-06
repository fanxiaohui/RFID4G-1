
#include<stdio.h> 
#include<stdlib.h> 
#include<unistd.h> 
#include<sys/types.h> 
#include<sys/stat.h> 
#include<fcntl.h> 
#include<termios.h> 
#include<errno.h> 
#include<string.h>

#define FALSE -1
#define TRUE 0

extern "C" {
	//int UART_Open(int fd, char* port);
	int UART_OpenCom(int fd, char* port,int speed);
	void UART_Close(int fd);
	//int UART_Set(int fd, int speed, int flow_ctrl, int databits, int stopbits, int parity);
	//int UART_Init(int fd, int speed, int flow_ctrlint, int databits, int stopbits, char parity);
	int UART_Recv(int fd, char *rcv_buf, int data_len);
	int UART_Send(int fd, char *send_buf, int data_len);
}
int UART_Open(int fd, char* port);
int UART_Set(int fd, int speed, int flow_ctrl, int databits, int stopbits, int parity);
int UART_Init(int fd, int speed, int flow_ctrlint, int databits, int stopbits, char parity);
/*****************************************************************
* ���ƣ� UART0_Open
* ���ܣ� �򿪴��ڲ����ش����豸�ļ�����
* ��ڲ����� fd :�ļ������� port :���ں�(ttyS0,ttyS1,ttyS2)
* ���ڲ����� ��ȷ����Ϊ1�����󷵻�Ϊ0
*****************************************************************/
int UART_Open(int fd, char* port)
{

	fd = open(port, O_RDWR | O_NOCTTY | O_NDELAY);
	if (FALSE == fd) {
		perror("Can't Open Serial Port");
		return(FALSE);
	}

	//�жϴ��ڵ�״̬�Ƿ�Ϊ����״̬ 
	if (fcntl(fd, F_SETFL, 0) < 0) {
		printf("fcntl failed!\n");
		return(FALSE);
	}
	else {
		//    printf("fcntl=%d\n",fcntl(fd, F_SETFL,0));
	}

	//�����Ƿ�Ϊ�ն��豸
	if (0 == isatty(STDIN_FILENO)) {
		printf("standard input is not a terminal device\n");
		return(FALSE);
	}

	return fd;
}

void UART_Close(int fd)
{
	close(fd);
}

/*******************************************************************
* ���ƣ� UART0_Set
* ���ܣ� ���ô�������λ��ֹͣλ��Ч��λ
* ��ڲ����� fd �����ļ�������
* speed �����ٶ�
* flow_ctrl ����������
* databits ����λ ȡֵΪ 7 ����8
* stopbits ֹͣλ ȡֵΪ 1 ����2
* parity Ч������ ȡֵΪN,E,O,,S
*���ڲ����� ��ȷ����Ϊ1�����󷵻�Ϊ0
*******************************************************************/
int UART_Set(int fd, int speed, int flow_ctrl, int databits, int stopbits, int parity)
{

	int i;
	//    int status; 
	int speed_arr[] = { B38400, B19200, B9600, B4800, B2400, B1200, B300,
		B38400, B19200, B9600, B4800, B2400, B1200, B300
	};
	int name_arr[] = {
		38400, 19200, 9600, 4800, 2400, 1200, 300, 38400,
		19200, 9600, 4800, 2400, 1200, 300
	};
	struct termios options;

	/*tcgetattr(fd,&options)�õ���fdָ��������ز������������Ǳ�����options,�ú���,�����Բ��������Ƿ���ȷ���ô����Ƿ���õȡ������óɹ�����������ֵΪ0��������ʧ�ܣ���������ֵΪ1.
	*/
	if (tcgetattr(fd, &options) != 0) {
		perror("SetupSerial 1");
		return(FALSE);
	}

	//���ô������벨���ʺ����������
	for (i = 0; i < sizeof(speed_arr) / sizeof(int); i++) {
		if (speed == name_arr[i]) {
			cfsetispeed(&options, speed_arr[i]);
			cfsetospeed(&options, speed_arr[i]);
		}
	}
	//�޸Ŀ���ģʽ����֤���򲻻�ռ�ô���        
	options.c_cflag |= CLOCAL;
	//�޸Ŀ���ģʽ��ʹ���ܹ��Ӵ����ж�ȡ��������
	options.c_cflag |= CREAD;
	//��������������
	switch (flow_ctrl) {
	case 0: //��ʹ��������
		options.c_cflag &= ~CRTSCTS;
		break;
	case 1: //ʹ��Ӳ��������
		options.c_cflag |= CRTSCTS;
		break;
	case 2: //ʹ�����������
		options.c_cflag |= IXON | IXOFF | IXANY;
		break;
	}
	//��������λ
	options.c_cflag &= ~CSIZE; //����������־λ
	switch (databits) {
	case 5:
		options.c_cflag |= CS5;
		break;
	case 6:
		options.c_cflag |= CS6;
		break;
	case 7:
		options.c_cflag |= CS7;
		break;
	case 8:
		options.c_cflag |= CS8;
		break;
	default:
		fprintf(stderr, "Unsupported data size\n");
		return (FALSE);
	}
	//����У��λ
	switch (parity) {
	case 'n':
	case 'N': //����żУ��λ��
		options.c_cflag &= ~PARENB;
		options.c_iflag &= ~INPCK;
		//+++
		options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG); /*Input*/
		options.c_oflag &= ~OPOST;   /*Output*/
		//+++
		break;
	case 'o':
	case 'O': //����Ϊ��У�� 
		options.c_cflag |= (PARODD | PARENB);
		options.c_iflag |= INPCK;
		break;
	case 'e':
	case 'E': //����ΪżУ�� 
		options.c_cflag |= PARENB;
		options.c_cflag &= ~PARODD;
		options.c_iflag |= INPCK;
		break;
	case 's':
	case 'S': //����Ϊ�ո� 
		options.c_cflag &= ~PARENB;
		options.c_cflag &= ~CSTOPB;
		break;
	default:
		fprintf(stderr, "Unsupported parity\n");
		return (FALSE);
	}
	// ����ֹͣλ 
	switch (stopbits) {
	case 1:
		options.c_cflag &= ~CSTOPB;
		break;
	case 2:
		options.c_cflag |= CSTOPB;
		break;
	default:
		fprintf(stderr, "Unsupported stop bits\n");
		return (FALSE);
	}
//+++
	/* Set input parity option */
	if ((parity != 'n') && (parity != 'N'))
		options.c_iflag |= INPCK;

	options.c_cc[VTIME] = 5; // 0.5 seconds
	options.c_cc[VMIN] = 1;

	options.c_cflag &= ~HUPCL;
	options.c_iflag &= ~INPCK;
	options.c_iflag |= IGNBRK;
	options.c_iflag &= ~ICRNL;
	options.c_iflag &= ~IXON;
	options.c_lflag &= ~IEXTEN;
	options.c_lflag &= ~ECHOK;
	options.c_lflag &= ~ECHOCTL;
	options.c_lflag &= ~ECHOKE;
	options.c_oflag &= ~ONLCR;

	tcflush(fd, TCIFLUSH); /* Update the options and do it NOW */
	if (tcsetattr(fd, TCSANOW, &options) != 0)
	{
		perror("SetupSerial 3");
		return (FALSE);
	}
//+++
	////�޸����ģʽ��ԭʼ�������
	//options.c_oflag &= ~OPOST;
	////���õȴ�ʱ�����С�����ַ�
	//options.c_cc[VTIME] = 1; /* ��ȡһ���ַ��ȴ�1*(1/10)s */
	//options.c_cc[VMIN] = 1; /* ��ȡ�ַ������ٸ���Ϊ1 */

	//						//�����������������������ݣ����ǲ��ٶ�ȡ
	//tcflush(fd, TCIFLUSH);

	////�������� (���޸ĺ��termios�������õ������У�
	//if (tcsetattr(fd, TCSANOW, &options) != 0)
	//{
	//	perror("com set error!/n");
	//	return (FALSE);
	//}
	return (TRUE);
}


int UART_Init(int fd, int speed, int flow_ctrlint, int databits, int stopbits, char parity)
{
	//���ô�������֡��ʽ
	if (FALSE == UART_Set(fd, speed, flow_ctrlint, databits, stopbits, parity)) {
		return FALSE;
	}
	else {
		return TRUE;
	}
}



/*******************************************************************
* ���ƣ� UART0_Recv
* ���ܣ� ���մ�������
* ��ڲ����� fd :�ļ�������
* rcv_buf :���մ��������ݴ���rcv_buf��������
* data_len :һ֡���ݵĳ���
* ���ڲ����� ��ȷ����Ϊ1�����󷵻�Ϊ0
*******************************************************************/
int UART_Recv(int fd, char *rcv_buf, int data_len)
{
	int len, fs_sel;
	fd_set fs_read;

	struct timeval time;

	FD_ZERO(&fs_read);
	FD_SET(fd, &fs_read);

	time.tv_sec = 10;
	time.tv_usec = 0;

	//ʹ��selectʵ�ִ��ڵĶ�·ͨ��
	fs_sel = select(fd + 1, &fs_read, NULL, NULL, &time);
	if (fs_sel) {
		len = read(fd, rcv_buf, data_len);
		return len;
	}
	else {
		return FALSE;
	}
}

/*******************************************************************
* ���ƣ� UART0_Send
* ���ܣ� ��������
* ��ڲ����� fd :�ļ�������
* send_buf :��Ŵ��ڷ�������
* data_len :һ֡���ݵĸ���
* ���ڲ����� ��ȷ����Ϊ1�����󷵻�Ϊ0
*******************************************************************/
int UART_Send(int fd, char *send_buf, int data_len)
{
	int ret;

	ret = write(fd, send_buf, data_len);
	if (data_len == ret) {
		return ret;
	}
	else {
		tcflush(fd, TCOFLUSH);
		return FALSE;

	}

}


int UART_OpenCom(int fd, char* port, int speed)
{
	int ret;
	fd = UART_Open(fd, port);
	if (FALSE == fd) {
		printf("open error\n");
		return -1;
	}
	ret = UART_Init(fd, speed, 0, 8, 1, 'N');
	if (FALSE == fd) {
		printf("Set Port Error\n");
		return -1;
	}
	return fd;
}
/*
int main(int argc, char **argv)
{
	int fd = FALSE;
	int ret;
	char rcv_buf[512];
	int i;
	if (argc != 2) {
		printf("Usage: %s /dev/ttySn \n", argv[0]);
		return FALSE;
	}
	fd = UART_Open(fd, argv[1]);
	if (FALSE == fd) {
		printf("open error\n");
		exit(1);
	}
	ret = UART_Init(fd, 9600, 0, 8, 1, 'N');
	if (FALSE == fd) {
		printf("Set Port Error\n");
		exit(1);
	}

	ret = UART_Send(fd, "*IDN?\n", 6);
	if (FALSE == ret) {
		printf("write error!\n");
		exit(1);
	}

	printf("command: %s\n", "*IDN?");
	memset(rcv_buf, 0, sizeof(rcv_buf));
	for (i = 0;; i++)
	{
		ret = UART_Recv(fd, rcv_buf, 512);
		if (ret > 0) {
			rcv_buf[ret] = '\0';
			printf("%s", rcv_buf);
		}
		else {
			printf("cannot receive data1\n");
			break;
		}
		if ('\n' == rcv_buf[ret - 1])
			break;
	}
	UART_Close(fd);
	return 0;
}
*/
