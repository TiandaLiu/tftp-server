# TFTP Server

## TFTP Server setup:
    $ python3 TFTPServer.py <port> <timeout>

#### For example, to run TFTPServer on port 8080 with timeout 5000ms:

    $ python3 TFTPServer.py 8080 5000

## TFTP Client setup:
### To open the TFTP client:

    $ tftp
    tftp> verbose
    Verbose mode on.
    tftp> binary
    tftp> trace
    Packet tracing on.
    tftp> connect 127.0.0.1 8080
    tftp> 

### To write a file to the TFTP server:
After running following code, you will find a file named "test.txt" on the server in the folder of TFTPServer.py

    tftp> put test.txt
    putting 1.txt to 127.0.0.1:1.txt [octet]
    sent WRQ <file=1.txt, mode=octet>
    received ACK <block=0>
    sent DATA <block=1, 512 bytes>
    received ACK <block=1>
    sent DATA <block=2, 512 bytes>
    received ACK <block=2>
    sent DATA <block=3, 512 bytes>
    received ACK <block=3>
    sent DATA <block=4, 351 bytes>
    received ACK <block=4>
    Sent 1887 bytes in 2.3 seconds [6427 bits/sec]
    tftp>

### To get a file from the TFTP server:
After running following code, you will find a file named "test.txt" in the folder where you run the TFTP client.

    tftp> get test.txt
    getting from 127.0.0.1:1.txt to 1.txt [octet]
    sent RRQ <file=1.txt, mode=octet>
    received DATA <block=1, 512 bytes>
    sent ACK <block=1>
    received DATA <block=2, 512 bytes>
    sent ACK <block=2>
    received DATA <block=3, 512 bytes>
    sent ACK <block=3>
    received DATA <block=4, 351 bytes>
    Received 1887 bytes in 0.8 seconds [18078 bits/sec]
    tftp>
