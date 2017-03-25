# Echo server program
import socket

clientHost = ''                 # Symbolic name meaning all available interfaces
clientPort = 50006              # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((clientHost, clientPort))
s.listen(1)              # allow only one outstanding request
# s is not a factory for connected sockets

conn, addr = s.accept()  # wait until incoming connection request (and accept it)
print 'Connected by', addr
while 1:
    data = conn.recv(1024)
    if not data: break
    sendMsg = "Echoing %s" % data
    print "Received '%s', sending '%s'" % (data, sendMsg)
    conn.send(sendMsg)
conn.close()

import socket
import select
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 8881))
sock.listen(5)

# lists of sockets to watch for input and output events
ins = [sock]
ous = []

# mapping socket -> (host, port) on which the client is running
adrs = {}
#map for states 
states ={}
outputMap ={}
inputMap ={}
S_INIT = "init"
S_GET = "get"
S_FIN = "fin"
try:
    while True:
        i, o, e = select.select(ins, ous, [])  # no excepts nor timeout
        for x in i:
            if x is sock:
                # input event on sock means client trying to connect
                newSocket, address = sock.accept(  )
                print "Connected from", address
                ins.append(newSocket)
                adrs[newSocket] = address
                states[newSocket] = S_INIT
            else:
                # other input events mean data arrived, or disconnections
                newdata = x.recv(8192)
                if newdata:
                    # data arrived, prepare and queue the response to it
                    print "%d bytes from %s" % (len(newdata), adrs[x])
                    inputSet[x] = newdata
                    if x not in ous: ous.append(x)
                else:
                    # a disconnect, give a message and clean up
                    print "disconnected from", adrs[x]
                    del adrs[x]
                    try: ous.remove(x)
                    except ValueError: pass
                    x.close(  )
        for x in o:
            state = state.get(x)
            input = JSONdecode(inputMap.get(x))
            if state == S_INIT and input['request'] == "GET":
                try:
                    state[x] = S_ACK
                    outputMap[x] = getFile(input['params'])
                except:
                    state[x] = S_FIN
                    outputMap[x] = "404"
            elif state == S_ACK and input['request']=="ACK":
                state[x] = S_FIN
                outputMap[x] = "FIN"
            elif state == S_FIN:
                try: del inputMap[x]
                except KeyError: pass
                try: del outputMap[x]
                except KeyError: pass
                try: del state[x]
                except KeyError: pass
                break;
            output = outputMap[x]
            if output:
                nsent = x.send(output)
                print "%d bytes to %s" % (nsent, adrs[x])
                # remember data still to be sent, if any
                output = output[nsent:]
            if output: 
                print "%d bytes remain for %s" % (len(tosend), adrs[x])
                outputMap[x] = tosend
                state[x]= S_GET
            else:
                print "No data currently remain for", adrs[x]
                state[x]= S_FIN
finally:
    sock.close(  )