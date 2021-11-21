import cbedata as cd
import socket
import time

HOST = ''  
PORT = 65432
print('Transponder is in SEND mode, reachable at port',PORT)

class FileTransmission:
    def __init__(self, params):
        #self.sbip = sendbackadr
        #self.sbtcpno = sendbackport
        self.id = cbedata.get_offline(params, 'newfile-identifier', 'val')
        self.fp = cbedata.get_offline(params, 'newfile-destfilepath', 'val')
        self.pktload = cbedata.get_offline(params, 'newfile-packetsize', 'val')
        try: self.cs = cbedata.get_offline(params, 'newfile-payloadchecksum', 'val')
        except: self.cs = None
        bufferfile = random.randint(10000000, 999999999)
        f = open(self.fp, 'w')
        f.close()

    def write(self, contents):
        f = open(self.fp, 'a')
        f.write(contents)
        f.close()
        print(f'{self.id} INFO: wrote to buffer, snippet: ',contents[0:25].replace('\n','\\n'))

items = {}


#wrapper for sending pkt, either Resp pkt or a Data pkt
def send(host, port, contents, block = False):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, int(port)))
        s.sendall( bytes(contents,'ASCII') )
        s.close()
        if not block:
            return None

    if block:
        print('Sync. Control handed off to send() function.')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 65431))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('SEND() INFO Connected by', addr)
                data = conn.recv(1024)
                return str(data)

def parse_resp(resp):
    #print(resp)
    #resp = str(resp).replace("b'","").replace("'", "") # debyte
    info = {}
    try:
        resp1 = resp.decode('ascii')
        resparr = resp1.split(' ', 2)
        info['origin'] = resp1[0]
        info['id'] = resparr[0][1:]
        info['type'] = resparr[1]
        info['c'] = resparr[2][1:-1]
    except:
        info = {'type': 'invalid', 'c': 'invalid', 'id': 'invalid', 'origin': 'I'}
    return info


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    hold = False
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        with conn:
            #print('Connected by', addr)
            # wait for incoming data
            data = conn.recv(60000)
            #print(data)
            try: res = parse_resp(data)
            except: res = {'type': None}
            if data:
                    #print(str(data))
                    #print(res)
                    pass
            #if res['type'] != 'OkRes' and hold:
                    #print(res['id'],'INFO: OkRes from remote on packet')
             #       #hold = False
                    pass
            #elif res['type'] == 'OkRes' and hold:
             #       print(res['id'],'INFO: OkRes from remote on packet')
              #      hold = False

            if res['type'] == 'ResDeny':
                    print('A transfer was denied by the remote. Here are the details:',data)
            if res['type'] == 'BadVerdict':
                    print('BadVerdict -- The transfer was rejected by the remote, details: ',data)
            if res['type'] == 'GoodVerdict':
                    print('GoodVerdict -- The transfer was accepted by the remote')
                    f = open('config.txt', 'r')
                    ccfg = f.read()
                    f.close()
                    if cd.get_offline(ccfg, 'application_config-endonsend', 'val') == '1':
                        exit()
            if res['type'] == 'ResAcc' and not hold:
                    #instruction given to hand a file over. files must be transmitted in serial order and cannot be done all at once
                    print(res['c'])
                    print('---------------------------------------------------------------')
                    print('File origin:',cd.get_offline(res['c'], 'newfile-origin', 'val') )
                    print('Handle:',cd.get_offline(res['c'], 'newfile-identifier', 'val') )
                    print('Pkt size:',cd.get_offline(res['c'], 'newfile-packetsize', 'val') )

                    #placeholder, encode in base 64 later
                    origin = cd.get_offline(res['c'], 'newfile-origin', 'val')
                    handle = cd.get_offline(res['c'], 'newfile-identifier', 'val')
                    size = int(cd.get_offline(res['c'], 'newfile-packetsize', 'val'))
                    
                    f = open(origin, 'r')
                    try: contents = f.read()
                    except:
                        contents = 'invalid'
                    contentsarray = [contents[i:i+size] for i in range(0, len(contents), size)]
                    ticker = 0
                    #broken up into chunks
                    f.close()

                    stopstop = False
                    alreadydone = 0

                    for i in contentsarray:
                        host = cd.get_offline(res['c'], 'newfile-host', 'val').split(':',1)
                        pktlen = len(i)
                        print(handle,ticker,f'INFO: transmitting ( {i[0:10]} len = {pktlen}) to remote @ {host}...'.replace('\n','\\n'))

                        notok = True
                        while notok:
                            try:
                                aaa = send(host[0], int(host[1]), f'S@{handle} Pkt ['+i+']', False) # get resp from remote
                                notok = False
                            except:
                                print(handle,ticker,f'WARN: error in transmitting pkt "{i[0:10]}" to remote.')
                                #input('Human operator: please resume transmission after fault by hitting <ENTER>.')
                                time.sleep(3)

                        #separate_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        #separate_send.connect((host[0], int(host[1])))
                        #separate_send.sendall(bytes(i,'ascii'))
                        # in some circumstances it may be appropriate to not wait for a response so you don't hand off control to
                        # a single handle for too long (keeping it open for multiple handles)
                        keepgo = True
                        while keepgo:
                            conn, addr = s.accept()
                            with conn:
                                data = conn.recv(1024)
                                ds = parse_resp(data)
                                #print(ds)
                                if data and ds['type'] == 'OkRes':
                                    keepgo = False
                                    alreadydone = alreadydone + pktlen
                                    print(handle,ticker,f'INFO: recieved OkRes confirmation, proceeding... (transmitted {alreadydone} bytes)')
                                elif data and ds['type'] == 'Stop':
                                    print(handle,ticker,f'STOP: remote requested to stop transmission of data, remarks:',ds['c'])
                                    stopstop = True
                                    break
        
                        
                        # change this to not wait for a response and just go
                        #if aaa != None:
                         #   if parse_resp(aaa)['type'] == 'OkRes': # doesn't work, we will not need a confirmation since TCP does that
                          #      print(ticker,'INFO: packet OK according to remote')
                           # elif parse_resp(aaa)['type'] == 'Stop':
                            #    print(ticker,'WARN: stop cmd issued by remote')
                             #   break

                        ticker = ticker + 1

                        if stopstop:
                            break

                    print(handle,ticker,'INFO: transmission of file is complete, a verdict should arrive soon.')
                    aaa = send(host[0], int(host[1]), f'S@{handle} Done [Done]', False)



            else: # type not known
                    #print(data) # just print data for debug
                    pass
