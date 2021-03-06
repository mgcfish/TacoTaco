#!/usr/bin/python
__author__ = 'GreenDog'
import hashlib
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="A converter of a Tacacs+ packet to a format of HashCat. ")

    parser.add_argument(
        '-t', '--type', type=str, help="Type of a packet. 1 - SSH , the second authentication packet (from a tacacs+ server to a cisco device); " +
                                       "2 - Telnet, the second authentication packet (from a tacacs+ server to a cisco device) "+
                                       "You should set a greeting meesage of the cisco device in -m. "+
                                       "A default value is \"\\nUser Access Verification\\n\\nUsername: \". Set \"Password: \" for SSH",  required=True)
    parser.add_argument(
        '-m', '--mess', type=str, help='Message for the second type', default="\nUser Access Verification\n\nUsername: ", required=False)

    parser.add_argument(
        '-p', '--packet', type=str, help='A Tacacs+ packet in hex', required=True)
    parser.add_argument(
        '-v', '--verbose', help='Verbose mode', action="store_true", dest="verbose", default=False, required=False)
    args = parser.parse_args()
    return args.type, args.packet, args.mess, args.verbose


def verb(x):
    if verbose:
        print x

print("Tac2Cat / Tacacs+ to HashCat  v0.2 beta")
print("Alexey Tyurin - agrrrdog [at] gmail.com")
print

p_type, packet, message,verbose = parse_args()
vers=packet[0:2]
seq_num = packet[4:6]
ses_id =packet[8:16]
verb("Tacacs+ version: "+vers)
verb("Packen number: "+seq_num)
verb("Session id: "+ses_id)
length=int(packet[16:24],16)
verb("Packet length: "+str(length))

enc_data=packet[24:24+32]
verb("Encrypted data: " + enc_data)

if(p_type=="1"):

    print("SSH")
    message=message.replace('\\n', "\n")
    mes_hex=message[0:10].encode('hex')
    verb("Part of message in hex: "+mes_hex)
    len_mes="0%x" % len(message)
    #hex(len(message))[2:]
    hash_file = open("hashes.txt", "w")
    data = "05"+ "01"+ "00"+ len_mes + "00"+ "00" +mes_hex
    verb("data: "+data)

    md5_1=hex(int(data, 16) ^ int(enc_data, 16))[2:34]
    print("md5_1 : "+md5_1)
    hash_file.write("%s:%s%s\n" % (md5_1, vers,seq_num))
    print("hashes.txt was created")
    print("hashcat-cli64.exe -a 3 -m 10 --hex-charset --hex-salt hashes.txt %s?your_mask_here"%ses_id)
    hash_file.close()


elif(p_type=="2"):

    print("Telnet")
    message=message.replace('\\n', "\n")
    mes_hex=message[0:10].encode('hex')
    verb("Part of message in hex: "+mes_hex)
    len_mes="%x" % len(message)
    #hex(len(message))[2:]
    hash_file = open("hashes.txt", "w")
    data = "04"+ "00"+ "00"+ len_mes + "00"+ "00" +mes_hex
    verb("data: "+data)

    md5_1=hex(int(data, 16) ^ int(enc_data, 16))[2:34]
    print("md5_1 : "+md5_1)
    hash_file.write("%s:%s%s\n" % (md5_1, vers,seq_num))
    print("hashes.txt was created")
    print("hashcat-cli64.exe -a 3 -m 10 --hex-charset --hex-salt hashes.txt %s?your_mask_here"%ses_id)
    hash_file.close()

else:
    print("Incorrect type of packet")
