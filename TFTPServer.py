import threading
import socket
import sys
import struct
import random
from os import path
import os

def main():
    serverPort, timeout = int(sys.argv[1]), int(sys.argv[2])
    print("serverPort: {0}, timeout: {1}".format(serverPort, timeout))

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverAddress = ('', serverPort)
    serverSocket.bind(serverAddress)
    print("The server is ready to receive")

    while True:
        message, clientAddress = serverSocket.recvfrom(1024)
        th = threading.Thread(target=handleRequest, args=(message, clientAddress,timeout,))
        th.start()
        print("A new thread has beed ")

def handleRequest(packet, clientAddress,timeout):
    # get opcode from packet
    opcode = struct.unpack("!H", packet[0:2])[0]
    
    # generate a random port number
    port = random.randrange(1024, 65535+1)
    # create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverAddress = ('', port)
    sock.bind(serverAddress)
    sock.settimeout(timeout/1000)
    # handle request
    if opcode == 1:
        fileName = getFileName(packet)
        handleRRQ(fileName, clientAddress, sock) # receive ack, send data
    elif opcode == 2:
        fileName = getFileName(packet)
        handleWRQ(fileName, clientAddress, sock) # receive data, send ack
    else:
        print("Unsupported request type!")

def handleRRQ(fileName, address, sock):
    # check file
    try:
        f = open(fileName, "br")
    except:
        sendError(sock, address, 5, 1, "File not found.")
        print("File not found.")
        return
    
    blockNum = 0
    receivedBlockNum = 0
    while True:
        # send data
        if receivedBlockNum == blockNum: # handle duplicate ACKs
            # update data packet
            fileData = f.read(512)
            blockNum += 1
            data = struct.pack("!HH%ds"%len(fileData),3,blockNum,fileData) # generate new data
            sock.sendto(data, address) # send new data
            print("sent DATA <block={}, 512 bytes>".format(blockNum))
        else:
            # send last data packet
            sock.sendto(data, address)
            print("sent DATA <block={}, 512 bytes>".format(blockNum))
        # check ack
        try:
            message, clientAddress = sock.recvfrom(1024)
            if clientAddress != address: # check client address
                sendError(sock, address, 5, 5, "Unknown transfer ID.")
                continue
            receivedOpcode = struct.unpack("!H", message[0:2])[0]
            if receivedOpcode == 5: # print error message, then terminate thread
                errmsg = getErrorMsg(message)
                print(errmsg)
                break
            elif receivedOpcode == 4:
                receivedBlockNum = struct.unpack("!H", message[2:4])[0]
                print("received ACK <block={}>".format(receivedBlockNum))
            else: # send error packet, then terminate
                sendError(sock, address, 5, 4, "Illegal TFTP operation.")
                break
            # check the end of file
            if len(fileData) < 512: # transmit the last packet multiple times to ensure the client can get the last data packet, then exit the thread.
                for i in range(10):
                    sock.sendto(data, address)
                    print("sent DATA <block={}, 512 bytes>".format(blockNum))
                print("the end of file has been transmitted")
                f.close()
                return
        except: # timeoput
            print("Timeout, retransmit DATA")
            # retransmit data
            continue
    f.close()

def handleWRQ(fileName, address, sock):
    if not path.exists(fileName):
        f = open(fileName, "bw")
    else:
        print("File already exists.")
        sendError(sock, address, 5, 6, "File already exists.")
        return

    ackNum = 0
    receivedBlockNum = 0
    while True:
        # send ack
        if receivedBlockNum == ackNum: # handle duplicate DATA blocks
            ackPacket = struct.pack("!HH", 4, ackNum) # generate new ack
            sock.sendto(ackPacket, address) # send new ack
            ackNum += 1
        else:
            # send last ack
            sock.sendto(ackPacket, address)
        print("sent ACK <block={}>".format(ackNum-1))
        # check data
        try:
            data, cliendAddress = sock.recvfrom(1024)
            if cliendAddress != address:
                sendError(sock, address, 5, 5, "Unknown transfer ID")
                continue
            opcode = struct.unpack("!H", data[0:2])[0]
            if opcode == 5: # print error message, then terminate thread
                errmsg = getErrorMsg(data)
                print(errmsg)
                os.unlink(fileName)
                return
            elif opcode == 3:
                receivedBlockNum = struct.unpack("!H", data[2:4])[0]
                print("received DATA <block={}, 512 bytes>".format(receivedBlockNum))
                if ackNum == receivedBlockNum:
                    f.write(data[4:])
            else:
                sendError(sock, address, 5, 4, "Illegal TFTP operation.")
                break
            # check the end of file
            if len(data) < 516:
                print("the end of file has been received")
                ackPacket = struct.pack("!HH", 4, ackNum)
                for i in range(10): # transmit the last ack multiple times to ensure that client can get the last ack, then exit the thread
                    sock.sendto(ackPacket, address)
                break
        except: # timeout
            print("Timeout, retransmit ACK")
            # retransmit acknowledgement
            continue
    f.close()

def sendError(sock, address, opcode, errorCode, errmsg):
    message = struct.pack("!HH", opcode, errorCode)
    message += errmsg.encode()
    message += b'\x00'
    sock.sendto(message, address)

def getFileName(packet):
    fileName = ""
    last = 2
    while packet[last] != 0:
        last += 1
    for i in range(2, last):
        fileName += chr(packet[i])
    return fileName

def getErrorMsg(packet):
    errmsg = packet[4:-1].decode('ASCII')
    return errmsg

if __name__ == "__main__":
    main()
