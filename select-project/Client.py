# Echo client program
import socket
import sys
import json
serverHost = 'localhost'
serverPort = 50005

S_INIT = "init"
S_GET = "get"
S_ACK = "ack"
S_FIN = "fin"
state = S_INIT

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print "creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto)
        s = socket.socket(af, socktype, proto)
    except socket.error, msg:
        print " error: %s" % msg
        s = None
        continue
    try:
        print " attempting to connect to %s" % repr(sa)
        s.connect(sa)
    except socket.error, msg:
        print " error: %s" % msg
        s.close()
        s = None
        continue
    break

if s is None:
    print 'could not open socket'
    sys.exit(1)
flag = 1;
buffer = ""
while flag:
    if state == S_INIT:
        s.send(json.dumps({'request':'get','params':'file1.txt'}))
        state = S_ACK
    data = s.recv(1024)
    print "data: %s state:%s" %(data,state)
    if data and state == S_ACK:
        s.send(json.dumps({'request':'ack', 'params':'ack'}))
        buffer = data;
        state = S_FIN
        print "%s" % state
    elif data == "404" and state == S_ACK:
        s.send(json.dumps({'request':'ack', 'params':'ack'}))
        state = S_FIN
    elif data == state and state == S_FIN:
        print "fin fin fin"
print "%s" % buffer

