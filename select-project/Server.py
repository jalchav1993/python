# Echo server program
import socket
import json
import sys
import select

clientHost = ''                 # Symbolic name meaning all available interfaces
clientPort = 50005              # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((clientHost, clientPort))
s.listen(10)              

ins = [s]
ous = []

# mapping socket -> (host, port) on which the client is running
adrs = {}
#map for states 
states ={}
outputMap ={}
inputMap ={}
S_INIT = "init"
S_GET = "get"
S_ACK = "ack"
S_FIN = "fin"
try:
    while True:
        i, o, e = select.select(ins, ous, [])  # no excepts nor timeout
        for x in i:
            if x is s:
                # input event on sock means client trying to connect
                newSocket, address = s.accept(  )
                print "Connected from", address
                ins.append(newSocket)
                adrs[newSocket] = address
                states[newSocket] = S_INIT
            else:
                # other input events mean data arrived, or disconnections
                newdata = x.recv(1024)
                if newdata:
                    # data arrived, prepare and queue the response to it
                    print "%d bytes from %s" % (len(newdata), adrs[x])
                    inputMap[x] = newdata
                    if x not in ous: ous.append(x)
                else:
                    # a disconnect, give a message and clean up
                    print "disconnected from", adrs[x]
                    del adrs[x]
                    try: ous.remove(x)
                    except ValueError: pass
                    x.close(  )
        for x in o:
            output = ""
            state = states.get(x)
            input = json.loads(inputMap.get(x))
            print "%s %s" %(state,input)
            if state == S_INIT and input['request'] == "get":
                try:
                    file = open(input['params'], "r+")
                    states[x] = S_ACK
                    output=outputMap[x] = file.read()
                except:
                    states[x] = S_FIN
                    output=outputMap[x] = "404"
            elif state == S_ACK and input['request']=="ack":
                states[x] = S_FIN
                output=outputMap[x] = "FIN"
            if output:
                nsent = x.send(output)
                print "%d bytes to %s" % (nsent, adrs[x])
                # remember data still to be sent, if any
                output = output[nsent:]
            if output: 
                print "%d bytes remain for %s" % (len(tosend), adrs[x])
                outputMap[x] = output
                states[x]= S_GET
            else:
                print "No data currently remain for", adrs[x]
                states[x]= S_FIN
            if states[x] == S_FIN:
                print"ending"
                try: del inputMap[x]
                except KeyError: pass
                try: del outputMap[x]
                except KeyError: pass
                try: del states[x]
                except KeyError: pass
                try: ous.remove(x)
                except ValueError: pass
                try: ins.remove(x)
                except ValueError: pass
                x.send('!$!$!fin!$!$!')
                x.close
                break
finally:
    s.close(  )