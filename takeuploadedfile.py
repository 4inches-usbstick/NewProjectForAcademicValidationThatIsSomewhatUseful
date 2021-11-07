import socket
import time, random
import cbedata
import hashlib

PORT = 1711
print('Transponder is in RECV mode, reachable at port',PORT)

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

def send(host, port, contents, block = False):
    print('Sending response...')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, int(port)))
        s.sendall( bytes(contents,'ASCII') )
        s.close()
        if not block:
             return None

class RedirectError:
    def __init__(self, a = None, b = None, c = None):
        pass
    def connect(self, a = None, b = None, c = None):
        pass
    def sendall(self, a = None, b = None, c = None):
        pass

class FileTransmission:
    def __init__(self, params):
        #self.sbip = sendbackadr
        #self.sbtcpno = sendbackport
        self.id = cbedata.get_offline(params, 'newfile-identifier', 'val')
        self.fp = cbedata.get_offline(params, 'newfile-destfilepath', 'val')
        self.fireback = cbedata.get_offline(params, 'newfile-sender', 'val')
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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('', PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        #print(addr)
        with conn:
            #print('Connected by', addr)
            data = conn.recv(60000)
            if data:
                #print(data[0:25])
                ds = parse_resp(data)
                identifier = ds['id']
                echoback = ds['c'][0:10]

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sa:
                    try: address = items[ds['id'][1:]].fireback.split(':')
                    except:
                        try:
                            address = cbedata.get_offline(data.decode('ascii'), 'newfile-sender', 'val').split(':')
                            print(address)
                        except:
                            address = ['127.0.0.1',1]
                            print('WARNING: address fell back to localhost:01')

                        
                    
                    try: sa.connect((address[0],int(address[1])))
                    except: sa = RedirectError()
                    #time.sleep(random.randint(0,2)) # test to see if the sender is patient or fails to confirm
                   # r = random.randint(0,10) test to see if sender will shut up when instructed to
                    #print(items, identifier)
                    if ds['type'] == 'Pkt':
                        try:
                            items[identifier[1:]].write(ds['c'])
                            sa.sendall(bytes('R'+f'{identifier} OkRes [{echoback}]','ascii'))
                            #print(f'{identifier} Wrote')
                        except:
                            sa.sendall( bytes('R'+f'{identifier} Stop [Invalid Identifier]','ascii'))
                        
                    #R@0x23A4 OkRes [ZmFzaWRvZn]

                    if data.startswith(b'::newrequest'):
                        ide = str(cbedata.get_offline(data.decode('ascii'), 'newfile-identifier', 'val'))
                        items[ide] = FileTransmission(data.decode('ascii') )
                        dd = data.decode('ascii')
                        #creates a file
                        inp = input(f'Someone is waiting to transfer a file. The details are as follows:\n-----\n{dd}\n-----\nAccept? [Y/N] ')
                        #inp = 'Y'
                        if inp == 'Y':
                            sa.sendall(bytes(f'R@{ide} ResAcc [{dd}]', 'ascii'))
                        else:
                            sa.sendall(bytes(f'R@{ide} ResDeny [User halted operation.]', 'ascii'))

                    if ds['type'] == 'Done':
                        ide = ds['id']
                        try: theircs = items[identifier[1:]].cs
                        except:
                            sa.sendall( bytes('R'+f'{identifier} BadVerdict [Invalid Identifier]','ascii'))
                            theircs = 'Invalid identifier.'

                        try:
                            f = open(items[identifier[1:]].fp, 'rb')
                            contents = f.read()
                            f.close()
                        except:
                            contents = 'invalid'
                            
                        try: currentcs = hashlib.sha256(contents).hexdigest()
                        except: currentcs = 'invalid input or other exception on handling'
                        print(f'{ide} INFO: Calculated SHA256 =',currentcs)
                        print(f'{ide} INFO: Preflight SHA256 =',theircs)
                        print(f'{ide} INFO: Equality =',currentcs==theircs)
                        print(f'{ide} INFO: b64 size =',len(contents),'bytes')
                        sss = input('Accept this file? [Y/N] ')

                        if sss == 'Y':
                            sa.sendall( bytes('R'+f'{identifier} GoodVerdict []','ascii'))
                            print('OK! sent verdict.')
                        else:
                            sa.sendall( bytes('R'+f'{identifier} BadVerdict [User rejected file]','ascii'))
                            print('OK! sent verdict.')

                        if ds['type'] == 'Stop' or ds['type'] == 'Error':
                            print('WARN/STOP/NOTICE: Sender issued an error message, details:',data)
