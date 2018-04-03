
#include <iostream>
#include "string.h"

#define	uint16	unsigned short//int //short
#define	uint8	unsigned char
#define	MAX_SYS_STR_NUMS	20
uint8 sendbuf[255];

uint8 ReadMemBankFields = 0x06;

char  SysStrData[MAX_SYS_STR_NUMS][20] = { { "Command:" },
{ "Status:" },
{ "DeviceID:" },//设备Id
{ "Timestamp:" },//执行该指令到标签首次被盘存到时的时间，单位毫秒
{ "EPC:" },//EPC
{ "TID:" },//TID
{ "USER:" },//USER
{ "RESERVED:" },//RESERVED
{ "AntID:" },//天线ID
{ "Power:" },//标签信号强度
{ "Times:" },//标签被盘存到的次数
{ "BVer:" },
{ "HVer:" },
{ "Fdata:" },
{ "FVer:" },
{ "SProtocol:" },
{ "SYS:BOOTLOADER" },
{ "SYS:APP" },
{ "SN:" },
{ "NUMS:" }
};
struct COMMAND_Struct {
	uint8 Header;
	uint8 DataLength;
	uint8 Command;
	//uint8 * pData;
	uint8 pData[255 - 3];
};
struct COMMANDRECV_Struct {
	uint8 Header;
	uint8 DataLength;
	uint8 Command;
	uint8  Status[2];
	//uint8 * pData;
	uint8 pData[255 - 5];
};
uint8 HexToA[20] = { "0123456789ABCDEF" };
#define MSG_CRC_INIT		    0xFFFF
#define MSG_CCITT_CRC_POLY		0x1021
uint8 Sub_M[16] = "Moduletech";

extern "C" {
	uint8 BootLoadToApp(uint8 * pOutbuf);
	uint8 SetBaudRate(uint8 * pOutbuf, int BaudRate);
	uint8 AppToBootLoad(uint8 * pOutbuf);
	uint8 GetDeviceNum(uint8 * pOutbuf);
	uint8 isAppOrBootLoad(uint8 * pOutbuf);
	uint8 GetTagMultiple(uint8 * pOutbuf, uint16 msTimes, uint16 SearchFlags);//0X22:多标签盘存命令，READ TAG MULTIPLE
	uint8 GetTagMultipleCommand(uint8 * pOutbuf); //0X29: 获取盘存到标签信息命令
	uint8 SetAntEnable(uint8 * pOutbuf, uint8 ant1, uint8 ant2, uint8 ant3, uint8 ant4);
	uint8 SetAntPower(uint8 * pOutbuf, uint8 ant1, uint8 ant2, uint8 ant3, uint8 ant4, uint16 rpower, uint16 wpower, uint16 stime);
	uint8 SubSetGetTagData(uint8 * pOut, uint8 timesm);
	uint8 SubSetGetTagDataStop(uint8 * pOut);

	//uint8 GetBOOTLOADERorFIRMWARE(uint8 * pOutbuf);
	uint16 ProcessorData(uint8 * pOutBuf, uint8 * pPdata, uint16 pdatalen);//串口接收处理
}

void CRC_calcCrc8(uint16 *crcReg, uint16 poly, uint16 u8Data)
{
	uint16 i;
	uint16 xorFlag;
	uint16 bit;
	uint16 dcdBitMask = 0x80;
	for (i = 0; i<8; i++)
	{
		xorFlag = *crcReg & 0x8000;
		*crcReg <<= 1;
		bit = ((u8Data & dcdBitMask) == dcdBitMask);
		*crcReg |= bit;
		if (xorFlag)
		{
			*crcReg = *crcReg ^ poly;
		}
		dcdBitMask >>= 1;
	}
}
uint16 CalcCRC(uint8 *msgbuf, uint8 msglen)
{
	uint16 calcCrc = MSG_CRC_INIT;
	uint8  i;
	for (i = 1; i < msglen; ++i)
		CRC_calcCrc8(&calcCrc, MSG_CCITT_CRC_POLY, msgbuf[i]);
	return calcCrc & 0xFFFF;
}
uint16 SetHexStr(uint8 * pOut, uint8 * pData, uint8 len)
{
	uint16 ret;
	int i;
	uint8 * p;
	uint8 c;
	p = pOut;
	for (i = 0; i < len; i++)
	{
		c = pData[i];
		p[i * 2 + 0] = HexToA[(c & 0xF0) >> 4];
		p[i * 2 + 1] = HexToA[(c & 0x0F)];
	}
	ret = len * 2;
	p[i * 2 + 0] = 0x0D;
	p[i * 2 + 1] = 0x0A;

	return ret + 2;
}
uint16 SetSysStrDataToStr(uint8 * pOut, uint8 n)
{
	uint8 ret;
	char * pstr;
	if ((n > MAX_SYS_STR_NUMS) || (n < 0))
		return -1;
	pstr = SysStrData[n];
	ret = strlen(pstr);
	memcpy(pOut, pstr, ret);

	return ret;
}
uint16 ProcessorSubSetGetTagData(uint8 * pOut, uint8 *pPdata, uint8 pdatalen)
{
	uint16 ret;
	int i;
	uint8 passdatas;
	uint16 temp;
	uint16 MetadataFlags;
	ret = 0;
	temp = strlen((char *)Sub_M);
	if (pdatalen > temp)
	{
		for (i = 0; i < temp; i++)
		{
			if (pPdata[i] != Sub_M[i])
			{
				break;
			}
		}
		if (i == temp)
		{
			pOut[0] = 'S';
			pOut[1] = 'u';
			pOut[2] = 'b';
			pOut[3] = ':';
			ret = SetHexStr(pOut + 4, pPdata + i, 2);
			ret += 4;
			//if ((pPdata[i] == 0xAA) && (pPdata[i + 1] == 0x49))
			{
				return ret;
			}
		}
	}
	else {
		return ret;
	}
	passdatas = 2;
	temp = 0;
	MetadataFlags = MetadataFlags = ((pPdata[0] & 0x00FF) << 8) + (pPdata[1] & 0x00FF);
	if (MetadataFlags & 0x0001) {
		temp = SetSysStrDataToStr(pOut + ret, 10);
		ret += temp;
		temp = SetHexStr(pOut + ret, pPdata + passdatas, 1);
		ret += temp;
		passdatas += 1;
	}
	if (MetadataFlags & 0x0002) {
		temp = SetSysStrDataToStr(pOut + ret, 9);
		ret += temp;
		temp = SetHexStr(pOut + ret, pPdata + passdatas, 1);
		ret += temp;
		passdatas += 1;
	}
	if (MetadataFlags & 0x0004) {
		temp = SetSysStrDataToStr(pOut + ret, 8);
		ret += temp;
		temp = SetHexStr(pOut + ret, pPdata + passdatas, 1);
		ret += temp;
		passdatas += 1;
	}
	if (MetadataFlags & 0x0008) {
		//temp = SetSysStrDataToStr(pOuut, 3);
		//ret += temp;
		//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
		//ret += temp;
		passdatas += 3;
	}
	if (MetadataFlags & 0x0010) {
		temp = SetSysStrDataToStr(pOut + ret, 3);
		ret += temp;
		temp = SetHexStr(pOut + ret, pPdata + passdatas, 4);
		ret += temp;
		passdatas += 4;
	}
	if (MetadataFlags & 0x0020) {
		//temp = SetSysStrDataToStr(pOuut, 3);
		//ret += temp;
		//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
		//ret += temp;
		passdatas += 2;
	}
	if (MetadataFlags & 0x0040) {
		//temp = SetSysStrDataToStr(pOuut, 3);
		//ret += temp;
		//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
		//ret += temp;
		passdatas += 1;
	}
	if (MetadataFlags & 0x0080) {
		//temp = SetSysStrDataToStr(pOuut, 3);
		//ret += temp;
		//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
		//ret += temp;
		passdatas += 2;
	}
	i = pPdata[passdatas];
	passdatas += 1;
	temp = SetSysStrDataToStr(pOut + ret, 4);
	ret += temp;
	if (i > 4) {
		temp = SetHexStr(pOut + ret, pPdata + passdatas + 2, i - 4);
		ret += temp;
	}
	return ret;
}
uint16 ProcessorBRorFIRMWARE(uint8 * pOuut, uint8 * pPdata, uint8 pdatalen)
{
	uint16 ret;
	uint16 temp;
	if (pdatalen < 0x14)return 0;
	ret = 0;
	temp = SetSysStrDataToStr(pOuut + ret, 11);
	ret += temp;
	temp = SetHexStr(pOuut + ret, pPdata, 4);
	ret += temp;

	temp = SetSysStrDataToStr(pOuut + ret, 12);
	ret += temp;
	temp = SetHexStr(pOuut + ret, pPdata + 4, 4);
	ret += temp;

	temp = SetSysStrDataToStr(pOuut + ret, 13);
	ret += temp;
	temp = SetHexStr(pOuut + ret, pPdata + 8, 4);
	ret += temp;

	temp = SetSysStrDataToStr(pOuut + ret, 14);
	ret += temp;
	temp = SetHexStr(pOuut + ret, pPdata + 12, 4);
	ret += temp;

	temp = SetSysStrDataToStr(pOuut + ret, 15);
	ret += temp;
	temp = SetHexStr(pOuut + ret, pPdata + 16, 4);
	ret += temp;
	return ret;
}
uint16 ProcessorGetTagEPCOne(uint8 * pOuut, uint8 * pPdata, uint8 pdatalen)
{
	uint16 ret;
	uint16 temp;
	uint16 MetadataFlags;
	uint8 passdatas;
	uint8 epclen;
	passdatas = 0;
	ret = 0;
	if (pPdata[0] & 0x10)
	{
		MetadataFlags = ((pPdata[1] & 0x00FF) << 8) + (pPdata[2] & 0x00FF);
		passdatas += 3;
		if (MetadataFlags & 0x0001) {
			temp = SetSysStrDataToStr(pOuut + ret, 10);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 1);
			ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0002) {
			temp = SetSysStrDataToStr(pOuut + ret, 9);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 1);
			ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0004) {
			temp = SetSysStrDataToStr(pOuut + ret, 8);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 1);
			ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0008) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 3;
		}
		if (MetadataFlags & 0x0010) {
			temp = SetSysStrDataToStr(pOuut + ret, 3);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			ret += temp;
			passdatas += 4;
		}
		if (MetadataFlags & 0x0020) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 2;
		}
		if (MetadataFlags & 0x0040) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0080) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 2;
		}
	}
	temp = SetSysStrDataToStr(pOuut + ret, 4);
	ret += temp;
	if (passdatas > 0)
	{
		epclen = pdatalen - passdatas - 2;
		temp = SetHexStr(pOuut + ret, pPdata + passdatas, epclen);
	}
	else {
		epclen = pdatalen - 3;
		temp = SetHexStr(pOuut + ret, pPdata + 1, epclen);
	}
	ret += temp;

	return ret;
}
uint16 ProssGetTagMemoryData(uint8 * pOuut, uint8 * pPdata, uint8 pdatalen)
{
	uint16 ret;
	uint16 temp;
	uint16 MetadataFlags;
	uint8 passdatas;
	uint8 epclen;
	uint8 RMemBankFields;
	passdatas = 0;
	ret = 0;
	if (pPdata[0] & 0x10)
	{
		MetadataFlags = ((pPdata[1] & 0x00FF) << 8) + (pPdata[2] & 0x00FF);
		passdatas += 3;
		if (MetadataFlags & 0x0001) {
			temp = SetSysStrDataToStr(pOuut + ret, 10);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 1);
			ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0002) {
			temp = SetSysStrDataToStr(pOuut + ret, 9);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 1);
			ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0004) {
			temp = SetSysStrDataToStr(pOuut + ret, 8);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 1);
			ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0008) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 3;
		}
		if (MetadataFlags & 0x0010) {
			temp = SetSysStrDataToStr(pOuut + ret, 3);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			ret += temp;
			passdatas += 4;
		}
		if (MetadataFlags & 0x0020) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 2;
		}
		if (MetadataFlags & 0x0040) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0080) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 2;
		}
	}
	if (ReadMemBankFields == 0x00)
	{
		RMemBankFields = 7;
	}
	else if (ReadMemBankFields == 0x01) {
		RMemBankFields = 4;
	}
	else if (ReadMemBankFields == 0x02) {
		RMemBankFields = 5;
	}
	else if (ReadMemBankFields == 0x03) {
		RMemBankFields = 6;
	}
	else {
		RMemBankFields = 7;
	}
	temp = SetSysStrDataToStr(pOuut + ret, RMemBankFields); //temp = SetSysStrDataToStr(pOuut, 4);
	ret += temp;
	if (passdatas > 0)
	{
		epclen = pdatalen - passdatas - 2;
		temp = SetHexStr(pOuut + ret, pPdata + passdatas, epclen);
	}
	else {
		epclen = pdatalen - 3;
		temp = SetHexStr(pOuut + ret, pPdata + 1, epclen);
	}
	ret += temp;
	return ret;
}
uint16 PrcoessorGetTagMultipleCommand(uint8 * pOuut, uint8 * pPdata, uint8 pdatalen)
{
	uint16 ret;
	uint16 MetadataFlags;
	uint8 tagcount;
	uint16 epclength;
	uint8 i;
	uint16 temp;
	uint8 passdatas;
	ret = 0;
	passdatas = 0;
	MetadataFlags = MetadataFlags = ((pPdata[0] & 0x00FF) << 8) + (pPdata[1] & 0x00FF);
	tagcount = pPdata[3];
	temp = SetSysStrDataToStr(pOuut + ret, 19);
	ret += temp;
	temp = SetHexStr(pOuut + ret, pPdata + 3, 1);
	ret += temp;
	passdatas += 4;
	for (i = 0; i < tagcount; i++)
	{
		if (MetadataFlags & 0x0001) {
			temp = SetSysStrDataToStr(pOuut + ret, 10);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 1);
			ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0002) {
			temp = SetSysStrDataToStr(pOuut + ret, 9);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 1);
			ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0004) {
			temp = SetSysStrDataToStr(pOuut + ret, 8);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 1);
			ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0008) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 3;
		}
		if (MetadataFlags & 0x0010) {
			temp = SetSysStrDataToStr(pOuut + ret, 3);
			ret += temp;
			temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			ret += temp;
			passdatas += 4;
		}
		if (MetadataFlags & 0x0020) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 2;
		}
		if (MetadataFlags & 0x0040) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 1;
		}
		if (MetadataFlags & 0x0080) {
			//temp = SetSysStrDataToStr(pOuut, 3);
			//ret += temp;
			//temp = SetHexStr(pOuut + ret, pPdata + passdatas, 4);
			//ret += temp;
			passdatas += 2;
		}
		epclength = ((pPdata[passdatas] & 0x00FF << 8) + pPdata[passdatas + 1] & 0x00FF) / 8;
		epclength -= 4;
		passdatas += 4;
		temp = SetSysStrDataToStr(pOuut + ret, 4);
		ret += temp;
		temp = SetHexStr(pOuut + ret, pPdata + passdatas, epclength);
		ret += temp;
		passdatas += (epclength + 2);
	}
	return ret;
}
uint16 ProcessorCommandRecv(uint8 * pOut, uint8 * pPdata, uint8 pdatalen, uint8 command)
{
	uint16 ret;
	uint16 temp;
	ret = 0;
	if (pdatalen < 1) {
		return ret;
	}
	if (command == 0x03) {
		ret = ProcessorBRorFIRMWARE(pOut, pPdata, pdatalen);
	}
	else if (command == 0x04) {
		return ret;
	}
	else if (command == 0x06) {
		return ret;
	}
	else if (command == 0x09) {
		return ret;
	}
	else if (command == 0x0C) {
		if (pPdata[0] == 0x11) {
			ret = SetSysStrDataToStr(pOut, 16);
		}
		else if (pPdata[0] == 0x12) {
			ret = SetSysStrDataToStr(pOut, 17);
		}
		else {
			return ret;
		}
	}
	else if (command == 0x10) {
		temp = SetSysStrDataToStr(pOut, 18);
		ret += temp;
		temp = SetHexStr(pOut + ret, pPdata, pdatalen);
		ret += temp;
	}
	else if (command == 0x21) {
		ret = ProcessorGetTagEPCOne(pOut, pPdata, pdatalen);
	}
	else if (command == 0x22) {
		temp = SetSysStrDataToStr(pOut, 19);
		ret += temp;
		if (pPdata[2] & 0x10)
		{
			temp = SetHexStr(pOut + ret, pPdata + 3, 4);
		}
		else {
			temp = SetHexStr(pOut + ret, pPdata + 3, 1);
		}
		//temp = SetHexStr(pOut + ret, pPdata, 1);
		ret += temp;
		return ret;
	}
	else if (command == 0x28) {
		ret = ProssGetTagMemoryData(pOut, pPdata, pdatalen);
	}
	else if (command == 0x29) {
		ret = PrcoessorGetTagMultipleCommand(pOut, pPdata, pdatalen);
	}
	else if (command == 0x2A) {
		return ret;
	}
	else if (command == 0x91) {
		return ret;
	}
	else if (command == 0xAA) {
		ret = ProcessorSubSetGetTagData(pOut, pPdata, pdatalen);
	}
	else {
		return ret;
	}
	return ret;
}

//uint16 ProcessorData(uint8 * pOutBuf, uint8 * pPdata, uint16 pdatalen)
uint16 ProcessorDataMultiLine(uint8 * pOutBuf, uint8 * pPdata, uint16 pdatalen)
{
	uint16 ret;
	struct COMMANDRECV_Struct * p;
	uint16 crc;
	uint16 temp;
	uint16 len;
	uint16 status;
	temp = 0;
	ret = 0;
	//char * pstr;
	if (pdatalen < 7) {
		return ret;// -1;
	}
	if (pPdata[0] != 0xFF) {
		return ret;// -1;
	}
	len = pPdata[1] & 0x00FF;
	//crc = ((pPdata[pdatalen - 2] & 0x00FF) << 8) + (pPdata[pdatalen - 1] & 0x00FF);
	//if (crc != CalcCRC(pPdata, pdatalen - 2))
	//{
	//	return -1;
	//}
	crc = ((pPdata[len + 3 + 2] & 0x00FF) << 8) + (pPdata[len + 3 + 2 + 1] & 0x00FF);
	if (crc != CalcCRC(pPdata, len + 5))
	{
		return ret;// -1;
	}
	p = (struct COMMANDRECV_Struct *)pPdata;
	//p->Status = (pPdata[3] & 0xFF << 8) + (pPdata[4] & 0x00FF);
	//p->pData = pPdata + 5;
	//pstr = SysStrData[0];
	//ret = strlen(pstr);
	//memcpy(pOutBuf, pstr, ret);
	temp = SetSysStrDataToStr(pOutBuf, 0);
	if (temp)
	{
		ret = temp;
	}
	temp = SetHexStr(pOutBuf + ret, pPdata + 2, 1);
	if (temp)
	{
		ret += temp;
	}
	temp = SetSysStrDataToStr(pOutBuf + ret, 1);
	if (temp)
	{
		ret += temp;
	}
	temp = SetHexStr(pOutBuf + ret, pPdata + 3, 2);
	if (temp)
	{
		ret += temp;
	}
	status = (p->Status[0] & 0x00FF << 8) + (p->Status[1] & 0x00FF);
	if (status != 0x0000)
		//if (p->Status != 0x0000)
	{
		return ret;
	}
	temp = ProcessorCommandRecv(pOutBuf + ret, p->pData, p->DataLength, p->Command);
	if (temp) {
		ret += temp;
	}
	return ret;
}
//uint16 ProcessorDataMultiLine(uint8 * pOutBuf, uint8 * pPdata, uint16 pdatalen)
uint16 ProcessorData(uint8 * pOutBuf, uint8 * pPdata, uint16 pdatalen)
{
	uint16 i;
	uint16 ret;
	uint16 packagelen;
	uint16 PendingPackagelen;
	uint16 tempret;
	uint8 * temppPdata;
	uint8 * ptempOut;

	uint16 bbb;
	uint16 ttt;
	//uint8 * ptemppdata;
	tempret = 0;
	temppPdata = pPdata;
	PendingPackagelen = pdatalen;
	ptempOut = pOutBuf;
	packagelen = 0;
	ret = 0;
	PendingPackagelen = pdatalen - 0;
	if (pdatalen < 7) {
		return ret;// -1;
	}
	if (pPdata[0] != 0xFF) {
		return ret;// -1;
	}
	//int ttt;
	//ttt = pPdata[1];
	//ptempOut = pOutBuf + ret;// packagelen;
	//ptemppdata = pPdata + PendingPackagelen;
	//PendingPackagelen = pdatalen - packagelen;
	while (1)
		//while (PendingPackagelen >= 7)
	{
		//int bbb;
		ttt = pdatalen - PendingPackagelen + 1;
		bbb = pPdata[ttt];
		packagelen = bbb + 7;// (ttt & 0x00FF + 5);// packagelen = (temppPdata[1] & 0x00FF + 5);

		if (packagelen > PendingPackagelen)
		{
			break;
		}
		//PendingPackagelen -= packagelen;
		//tempret = ProcessorDataMultiLine(ptempOut, temppPdata, PendingPackagelen);
		tempret = ProcessorDataMultiLine(ptempOut, pPdata + (pdatalen - PendingPackagelen), packagelen);
		ret += tempret;
		PendingPackagelen -= packagelen;

		if (PendingPackagelen < 7)
		{
			break;
		}

		ptempOut = pOutBuf + ret;// += ret; //ptempOut = pOutBuf + ret;// packagelen;
		temppPdata += packagelen; //temppPdata = pPdata + packagelen;//PendingPackagelen;
		for (i = 0; i < PendingPackagelen; i++)
		{
			if (temppPdata[i] == 0xFF)
			{
				PendingPackagelen -= i;
				temppPdata += i;
				break;
			}
		}
	}
	//packagelen = (temppPdata[1] & 0x00FF + 5);
	//while()
	return ret;
}
uint8 MakeCommandToBuf(uint8 command, uint8 * psendbuf, uint8 * pdata, uint8 datalength)
{
	uint8 ret = 0;
	uint16 crc;
	struct COMMAND_Struct * p;
	p = (struct COMMAND_Struct *)psendbuf;
	//p->pData = psendbuf + 3;
	//memset(psendbuf, 0, 255);
	p->Header = 0xFF;
	p->DataLength = datalength;
	p->Command = command;
	if (datalength > 0) {
		memcpy(p->pData, pdata, datalength);
	}
	ret = datalength + 3;
	crc = CalcCRC(psendbuf, ret);
	//crc = CalcCRC(psendbuf + 1, ret - 1);
	psendbuf[ret] = (crc & 0xFF00) >> 8;
	psendbuf[ret + 1] = (crc & 0x00FF);
	ret += 2;
	return ret;
}
uint8 GetBOOTLOADERorFIRMWARE(uint8 * pOutbuf)//0X03:获取BOOTLOADER/FIRMWARE版本信息（APP应用层也可用）
{
	uint8 ret;
	ret = MakeCommandToBuf(0x03, pOutbuf, NULL, 0);
	return ret;
}
uint8 BootLoadToApp(uint8 * pOutbuf)//0X04:BOOT FIRMWARE命令，运行到APP层（APP应用层也可用）
{
	uint8 ret;
	ret = MakeCommandToBuf(0x04, pOutbuf, NULL, 0);
	return ret;
}
uint8 SetBaudRate(uint8 * pOutbuf, int BaudRate)//0X06:设置波特率命令（APP应用层也可用）pOutbuf为返回组织成的命令行数据，函数返回这个buf数据长度
{
	uint8 ret;
	uint8 BR[4];
	if (BaudRate == 9600)
	{
		BR[0] = 0x00; BR[1] = 0x00;
		BR[2] = 0x25; BR[3] = 0x80;
	}
	else if (BaudRate == 19200) {
		BR[0] = 0x00; BR[1] = 0x00;
		BR[2] = 0x4B; BR[3] = 0x00;
	}
	else if (BaudRate == 38400) {
		BR[0] = 0x00; BR[1] = 0x00;
		BR[2] = 0x96; BR[3] = 0x00;
	}
	else if (BaudRate == 57600) {
		BR[0] = 0x00; BR[1] = 0x00;
		BR[2] = 0xE1; BR[3] = 0x00;
	}
	else if (BaudRate == 115200) {
		BR[0] = 0x00; BR[1] = 0x01;
		BR[2] = 0xC2; BR[3] = 0x00;
	}
	else {
		BR[0] = 0x00; BR[1] = 0x01;
		BR[2] = 0xC2; BR[3] = 0x00;
	}
	ret = MakeCommandToBuf(0x06, pOutbuf, BR, 4);
	return ret;
}
uint8 AppToBootLoad(uint8 * pOutbuf)//0X09:运行到BOOTLOADER层（APP应用层也可用）
{
	uint8 ret;
	ret = MakeCommandToBuf(0x09, pOutbuf, NULL, 0);
	return ret;
}
uint8 isAppOrBootLoad(uint8 * pOutbuf)//0X0C:获取目前是运行在BOOTLOADER层还是APP应用层（APP应用层也可用）
{
	uint8 ret;
	ret = MakeCommandToBuf(0x0C, pOutbuf, NULL, 0);
	return ret;
}
uint8 GetDeviceNum(uint8 * pOutbuf)//0X10:获取模块序列号；（APP应用层也可用）
{
	uint8 ret;
	uint8 buf[2];
	buf[0] = 0x00;//Option:1字节，预留参数，目前该值无意义
	buf[1] = 0x00;//Data flags:1字节，预留参数，目前该值无意义
	ret = MakeCommandToBuf(0x10, pOutbuf, buf, 2);
	return ret;
}
uint8 GetTagEPCOne(uint8 * pOutbuf, uint16 msTimes = 0x01F4)//0X21:单标签盘存命令
{//第一个盘点EPC，默认时间500ms
	uint8 ret;
	uint8 buf[20];
	uint16 Metadata;
	Metadata = 0x0000 + 0x0001 + 0X0002 + 0x0004 + 0x0010;//0x0000返回标签EPC号(包括标签CRC)+0x0001盘存到的次数+0x0002标签的RSSI信号值+0x0004天线ID号+0X0010被盘存到时的时间
	buf[0] = (msTimes & 0xFF00) >> 8;
	buf[1] = (msTimes & 0x00FF);
	buf[2] = 0x10;//Option
	buf[3] = (Metadata & 0xFF00) >> 8;
	buf[4] = (Metadata & 0x00FF);
	ret = MakeCommandToBuf(0x21, pOutbuf, buf, 5);
	return ret;
}
uint8 GetTagEPCOneFilter(uint8 * pOutbuf, uint8 * filterdata, uint8 fdatalen, int address, uint8 filter = 0x01, uint16 msTimes = 0x01F4)
{//filter 0x01 Select on the value of the EPC; 0x02 Select on contents of TID memory bank;
 //0x03 Select on contents of USER Memory memory bank; 0x04 Select on contents of EPC memory bank
	uint8 ret;
	uint8 buf[100];
	uint16 Metadata;
	uint16 flen;
	uint8 t;
	int i;
	if ((filter < 0x01) || (filter > 0x05)) return 0;
	Metadata = 0x0000 + 0x0001 + 0X0002 + 0x0004 + 0x0010;//0x0000返回标签EPC号(包括标签CRC)+0x0001盘存到的次数+0x0002标签的RSSI信号值+0x0004天线ID号+0X0010被盘存到时的时间
	buf[0] = (msTimes & 0xFF00) >> 8;
	buf[1] = (msTimes & 0x00FF);
	buf[2] = 0x10 + filter;//Option
	buf[3] = (Metadata & 0xFF00) >> 8;
	buf[4] = (Metadata & 0x00FF);

	flen = fdatalen * 8;
	t = 5;
	if (flen > 0xFF) {
		buf[t] = (flen & 0xFF00) >> 8;
		buf[t + 1] = flen & 0x00FF;
		t += 1;
	}
	else {
		buf[t] = flen & 0x00FF;
	}
	t += 1;
	if (filter != 0x01)
	{
		buf[t] = 0x00;
		buf[t + 1] = 0x00;
		buf[t + 2] = (address & 0xFF00) >> 8;
		buf[t + 3] = address & 0x00FF;
		t += 4;
	}
	for (i = 0; i < fdatalen; i++)
	{
		buf[t + i] = filterdata[i];
	}

	ret = MakeCommandToBuf(0x21, pOutbuf, buf, t + i);
	return ret;

}
uint8 GetTagMultipleFilter(uint8 * pOutbuf, uint8 * filterdata, uint8 * password, uint8 * address, uint8 fdatalen, uint8 filter = 0x00, uint16 msTimes = 0x01F4, uint16 SearchFlags = 0x0000)
{//password和address为4字节数据
	uint8 ret;
	//uint8 buf[100];
	uint8 * buf;
	int i;
	buf = pOutbuf;
	if ((filter < 0x00) || (filter > 0x05))return 0;
	buf[0] = filter;
	buf[1] = ((SearchFlags & 0xFF00) >> 8);
	buf[2] = SearchFlags & 0x00FF;
	//buf[1] = 0x00; 
	//buf[2] = 0x00;
	buf[3] = ((msTimes & 0xFF00) >> 8);
	buf[4] = msTimes & 0x00FF;
	if (filter == 0x00)
	{
		ret = 5;
		return ret;
	}
	for (i = 0; i < 4; i++)
	{
		buf[5 + i] = password[i];
	}
	ret = 9;
	if (filter == 0x05) {
		return ret;
	}
	if (filter != 0x01)
	{
		for (i = 0; i < 4; i++)
		{
			buf[ret + i] = address[i];
		}
		ret += 4;
	}
	buf[ret] = fdatalen * 8;
	ret += 1;
	for (i = 0; i < fdatalen; i++)
	{
		buf[ret + i] = filterdata[i];
	}
	ret += i;
	return ret;
}
uint8 GetTagMultiple(uint8 * pOutbuf, uint16 msTimes = 0x01F4, uint16 SearchFlags = 0x0000)//0X22:多标签盘存命令，READ TAG MULTIPLE
{
	uint8 ret;
	uint8 temp;
	uint8 password[4];
	uint8 address[4];
	uint8 buf[100];
	memset(buf, 0, 100);
	temp = GetTagMultipleFilter(buf, NULL, password, address, 0, 0x00, msTimes, SearchFlags);
	ret = MakeCommandToBuf(0x22, pOutbuf, buf, temp);

	return ret;
}

uint8 GetTagMemoryData(uint8 * pOut, uint8 * raddress, uint8 * accesspassword, uint8 * accessaddress, uint8 * selectdata, uint8 selectdlen = 0x00,
	uint8 option = 0x00, uint16 metadataflg = 0x0017, uint8 rmembank = 0x00, uint8 rwordcount = 0x60, uint16 mstimeout = 0x01F4)//0X28：读标签存储区命令
																																//uint8 GetTagMemoryData(uint8 * pOut, uint16 mstimeout, uint8 option, uint16 metadataflg, uint8 rmembank, uint8 * raddress, uint8 rwordcount,
																																//	uint8 * accesspassword, uint8 * accessaddress, uint8 selectdlen, uint8 * selectdata)
{
	uint8 ret;
	int i;
	uint8 flg;
	ret = 0;
	pOut[0] = ((mstimeout & 0xFF00) >> 8); pOut[1] = mstimeout & 0x00FF;
	pOut[2] = option;
	ret = 3;
	if (option & 0x10)
	{
		pOut[3] = ((metadataflg & 0xFF00) >> 8); pOut[4] = metadataflg & 0x00FF;
		ret += 2;
	}
	if ((rmembank < 0x00) || (rmembank > 0x03))rmembank = 0x00;

	ReadMemBankFields = rmembank;
	pOut[ret++] = rmembank;
	for (i = 0; i < 4; i++)
	{
		pOut[ret++] = raddress[i];
	}
	if (rwordcount > 0x60)rwordcount = 0x60;
	pOut[ret++] = rwordcount;
	flg = option & 0x0F;
	if (flg > 0x00)
	{
		//if (flg != 0x00) {
		for (i = 0; i < 4; i++)
		{
			pOut[ret++] = accesspassword[i];
		}
		//}
		if (flg > 0x01)
		{
			for (i = 0; i < 4; i++)
			{
				pOut[ret++] = accessaddress[i];
			}
		}
		pOut[ret++] = selectdlen * 8;
		for (i = 0; i < selectdlen; i++)
		{
			pOut[ret++] = selectdata[i];
		}
		//pOut[++ret] = rmembank;
		//for (i = 0; i < 4; i++)
		//{
		//	pOut[++ret] = raddress[i];
		//}
		//if (rwordcount > 0x60)rwordcount = 0x60;
		//pOut[++ret] = rwordcount;
		//flg = option & 0x0F;
		//if (flg > 0x00)
		//{
		//	//if (flg != 0x00) {
		//		for (i = 0; i < 4; i++)
		//		{
		//			pOut[++ret] = accesspassword[i];
		//		}
		//	//}
		//	if (flg > 0x01)
		//	{
		//		for (i = 0; i < 4; i++)
		//		{
		//			pOut[++ret] = accessaddress[i];
		//		}
		//	}
		//	pOut[++ret] = selectdlen * 8;
		//	for (i = 0; i < selectdlen; i++)
		//	{
		//		pOut[++ret] = selectdata[i];
		//	}
	}
	return ret;
}
uint8 GetTagMemoryDataReserved(uint8 * pOutbuf)//0X28：读标签存储区命令  获得 Reserved
{
	uint8 ret;
	uint8 temp;
	uint8 buf[100];
	uint8 raddress[4] = { 0x00, 0x00, 0x00, 0x00 };
	temp = GetTagMemoryData(buf, raddress, raddress, raddress, raddress, 0x00, 0x10);
	ret = MakeCommandToBuf(0x28, pOutbuf, buf, temp);
	return ret;
}
uint8 GetTagMemoryDataEPC(uint8 * pOutbuf)//0X28：读标签存储区命令   获得EPC
{
	uint8 ret;
	uint8 temp;
	uint8 buf[100];
	uint8 raddress[4] = { 0x00, 0x00, 0x00, 0x00 };
	temp = GetTagMemoryData(buf, raddress, raddress, raddress, raddress, 0x00, 0x10, 0x0017, 0x01);
	ret = MakeCommandToBuf(0x28, pOutbuf, buf, temp);
	return ret;
}
uint8 GetTagMemoryDataTID(uint8 * pOutbuf)//0X28：读标签存储区命令 获得  TID
{
	uint8 ret;
	uint8 temp;
	uint8 buf[100];
	uint8 raddress[4] = { 0x00, 0x00, 0x00, 0x00 };
	temp = GetTagMemoryData(buf, raddress, raddress, raddress, raddress, 0x00, 0x10, 0x0017, 0x02);
	ret = MakeCommandToBuf(0x28, pOutbuf, buf, temp);
	return ret;
}
uint8 GetTagMemoryDataUserMemory(uint8 * pOutbuf)//0X28：读标签存储区命令  获得 UserMemory
{
	uint8 ret;
	uint8 temp;
	uint8 buf[100];
	uint8 raddress[4] = { 0x00, 0x00, 0x00, 0x00 };
	temp = GetTagMemoryData(buf, raddress, raddress, raddress, raddress, 0x00, 0x10, 0x0017, 0x03);
	ret = MakeCommandToBuf(0x28, pOutbuf, buf, temp);
	return ret;
}
uint8 GetTagMultipleCommand(uint8 * pOutbuf) //0X29: 获取盘存到标签信息命令
{
	uint8 ret;
	uint8 buf[100];
	uint16 Metadata;
	Metadata = 0x0000 + 0x0001 + 0X0002 + 0x0004 + 0x0010;//0x0000返回标签EPC号(包括标签CRC)+0x0001盘存到的次数+0x0002标签的RSSI信号值+0x0004天线ID号+0X0010被盘存到时的时间
	buf[0] = (Metadata & 0xFF00) >> 8;
	buf[1] = (Metadata & 0x00FF);
	buf[2] = 0x00;
	ret = MakeCommandToBuf(0x29, pOutbuf, buf, 3);
	return ret;
}
uint8 ClearMemDataS(uint8 * pOutbuf)//0X2A:清除标签缓存区命令
{
	uint8 ret;
	ret = MakeCommandToBuf(0x2A, pOutbuf, NULL, 0);
	return ret;
}
uint8 SetAntEnable(uint8 * pOutbuf, uint8 ant1 = 0x01, uint8 ant2 = 0x00, uint8 ant3 = 0x00, uint8 ant4 = 0x00)
{//0X91:天线口设置命令 使能天线
	uint8 ret;
	uint8 buf[10];
	uint8 i;
	buf[0] = 0x02;
	i = 1;
	if (ant1 > 0)
	{
		buf[i] = ant1;
		buf[i + 1] = ant1;
		i += 2;
	}
	if (ant2 > 0)
	{
		buf[i] = ant2;
		buf[i + 1] = ant2;
		i += 2;
	}
	if (ant3 > 0)
	{
		buf[i] = ant3;
		buf[i + 1] = ant3;
		i += 2;
	}
	if (ant4 > 0)
	{
		buf[i] = ant4;
		buf[i + 1] = ant4;
		i += 2;
	}
	ret = MakeCommandToBuf(0x91, pOutbuf, buf, i);
	return ret;
}
uint8 SetAntPower(uint8 * pOutbuf, uint8 ant1 = 0x01, uint8 ant2 = 0x02, uint8 ant3 = 0x03, uint8 ant4 = 0x04, uint16 rpower = 0x0400, uint16 wpower = 0x0BB8, uint16 stime = 0x01F4)
{//当Option=3或Option=4时都可以设置天线发射功率，仅当Option=4时可以设置天线配置时间
	uint8 ret;
	uint8 i;
	uint8 buf[30];
	if (stime != 0x0000)
	{
		buf[0] = 0x04;
	}
	else {
		buf[0] = 0x03;
	}
	i = 1;
	if (ant1 > 0)
	{
		buf[i] = ant1;
		buf[i + 1] = (rpower & 0xFF00) >> 8;
		buf[i + 2] = (rpower & 0x00FF);
		buf[i + 3] = (wpower & 0xFF00) >> 8;
		buf[i + 4] = (wpower & 0x00FF);
		i += 5;
		if (buf[0] == 0x04)
		{
			buf[i + 5] = (stime & 0xFF00) >> 8;
			buf[i + 6] = (stime & 0x00FF);
			i += 2;
		}
	}
	if (ant2 > 0)
	{
		buf[i] = ant2;
		buf[i + 1] = (rpower & 0xFF00) >> 8;
		buf[i + 2] = (rpower & 0x00FF);
		buf[i + 3] = (wpower & 0xFF00) >> 8;
		buf[i + 4] = (wpower & 0x00FF);
		i += 5;
		if (buf[0] == 0x04)
		{
			buf[i + 5] = (stime & 0xFF00) >> 8;
			buf[i + 6] = (stime & 0x00FF);
			i += 2;
		}
	}
	if (ant3 > 0)
	{
		buf[i] = ant3;
		buf[i + 1] = (rpower & 0xFF00) >> 8;
		buf[i + 2] = (rpower & 0x00FF);
		buf[i + 3] = (wpower & 0xFF00) >> 8;
		buf[i + 4] = (wpower & 0x00FF);
		i += 5;
		if (buf[0] == 0x04)
		{
			buf[i + 5] = (stime & 0xFF00) >> 8;
			buf[i + 6] = (stime & 0x00FF);
			i += 2;
		}
	}
	if (ant4 > 0)
	{
		buf[i] = ant4;
		buf[i + 1] = (rpower & 0xFF00) >> 8;
		buf[i + 2] = (rpower & 0x00FF);
		buf[i + 3] = (wpower & 0xFF00) >> 8;
		buf[i + 4] = (wpower & 0x00FF);
		i += 5;
		if (buf[0] == 0x04)
		{
			buf[i + 5] = (stime & 0xFF00) >> 8;
			buf[i + 6] = (stime & 0x00FF);
			i += 2;
		}
	}
	ret = MakeCommandToBuf(0x91, pOutbuf, buf, i);
	return ret;
}

uint8 SubSetGetTagData(uint8 * pOut, uint8 timesm = 0x05)
{
	uint8 ret;
	int i;
	//uint8 M[16] = "Moduletech";
	uint8 buf[100];
	uint8 Ml;
	uint8 SubCrc;
	uint16 metadataflag;//意义与0X29命令中的一样
	uint8 option;//意义与0X22命令中的一样
	uint16 searchflg;//SEARCHFLAGS：意义与0X22命令中的一样；另SEARCHFLAGS高字节的低4位表示不停止盘存过程中的停顿时间，取值范围为0-15
	if ((timesm < 0) || (timesm > 15))
	{
		timesm = 5;
	}
	//Ml = strlen((char *)M);
	Ml = strlen((char *)Sub_M);
	for (i = 0; i < Ml; i++)
	{
		buf[i] = Sub_M[i]; //buf[i] = M[i];
	}
	buf[i++] = 0xAA; buf[i++] = 0x48;
	//ret = GetTagMultiple(buf + i - 1);
	metadataflag = 0x0017;
	buf[i++] = ((metadataflag & 0xFF00) >> 8);
	buf[i++] = metadataflag & 0x00FF;

	option = 0x10;
	buf[i++] = option;

	searchflg = (0x0000 + timesm) << 8;
	buf[i++] = timesm;//((searchflg & 0xFF00) >> 8);
	buf[i++] = 0x00;// searchflg & 0x00FF;

	ret = 0;
	ret += i;
	SubCrc = 0;
	i = 0;
	for (i = 0; i < ret - Ml; i++)
	{
		SubCrc += buf[Ml + i];
	}
	buf[ret++] = SubCrc;
	buf[ret++] = 0xBB;

	ret = MakeCommandToBuf(0xAA, pOut, buf, ret);
	return ret;
}
uint8 SubSetGetTagDataStop(uint8 * pOut)
{
	uint8 ret;
	int i;
	//uint8 M[16] = "Moduletech";
	uint8 buf[100];
	uint8 Ml;
	uint8 SubCrc;
	//Ml = strlen((char *)M);
	Ml = strlen((char *)Sub_M);
	for (i = 0; i < Ml; i++)
	{
		buf[i] = Sub_M[i]; //buf[i] = M[i];
	}
	buf[i++] = 0xAA; buf[i++] = 0x49;
	SubCrc = 0;
	for (ret = 0; ret < i - Ml; ret++)
	{
		SubCrc += buf[Ml + i];
	}
	buf[i++] = SubCrc;
	buf[i++] = 0xBB;
	ret = MakeCommandToBuf(0xAA, pOut, buf, i);

	return ret;
}