import tkinter as tk
import hashlib
import random

def readb(obj):
    return obj.get()
    
root = tk.Tk()
root.title('Console')

greeting = tk.Label(text="Send a File")
greeting.config(font=("", 24))
greeting.grid(row=0,column=0)

#target ip
remoteip = tk.Label(text="Target IP address")
remoteip_box = tk.Entry()

remoteip.grid(row=1,column=0)
remoteip_box.grid(row=1,column=1)

#target port
remoteport = tk.Label(text="Target TCP port #")
remoteport_box = tk.Entry()

remoteport.grid(row=1,column=2)
remoteport_box.grid(row=1,column=3)

#src file
src = tk.Label(text="Source filepath")
src_box = tk.Entry()
src.grid(row=3,column=0)
src_box.grid(row=3,column=1)

#self ip
self = tk.Label(text="Self IP address")
self_box = tk.Entry()
self.grid(row=4,column=0)
self_box.grid(row=4,column=1)

#self ip
selfport = tk.Label(text="Self TCP port #")
selfport_box = tk.Entry()
selfport.grid(row=4,column=2)
selfport_box.grid(row=4,column=3)

#target file
destiny = tk.Label(text="Destination filepath")
destiny_box = tk.Entry()

destiny.grid(row=6,column=0)
destiny_box.grid(row=6,column=1)

#target file
pkt = tk.Label(text="Packet size (int)")
pkt_box = tk.Entry()

pkt.grid(row=7,column=0)
pkt_box.grid(row=7,column=1)

tk.Label(text = 'Request body to send:').grid(row=10, column=3)
T = tk.Text(root, height=10, width=70) # init, use grid manager later

def transmit():
    try:
        target = readb(remoteip_box) + ':' + readb(remoteport_box)
        selfip = readb(self_box) + ':' + readb(selfport_box)
        destfp = readb(destiny_box)
        srcfp = readb(src_box)
        pktsize = int(readb(pkt_box) )

        f = open(srcfp, 'rb')
        c = f.read()
        f.close()

        pf256 = hashlib.sha256(c).hexdigest().upper()

        print(f"""
Transfer Information
Remote server: {target}
Return address: {selfip}
Filepath: local:{srcfp} -> remote:{destfp}
Checksum SHA256: {pf256}
Packet size: {pktsize} bytes
""")

        f = open('template.txt','r')
        template = f.read()
        f.close()

        req = template.replace('{checksum}', str(pf256)).replace('{remote}', target).replace('{self}', selfip).replace('{pktbytes}', str(pktsize)).replace('{destiny}', destfp).replace('{source}', srcfp).replace('{id}', str(random.randint(10000,99999)))
        T.delete(1.0, 'end')
        T.insert(1.0, req)
        

    except Exception as e:
        T.delete(1.0, 'end')
        T.insert(1.0, 'Encountered exception on generating request body, exception: '+str(e))
        
def tcp_send(host, port, contents, block = False):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, int(port)))
        s.sendall( bytes(contents,'ASCII') )
        s.close()
        if not block:
            return None

def opensocket():
    import os, socket, time, cbedata
    os.system('start senduploadedfile.py')
    time.sleep(1)
    contents = T.get(1.0, tk.END)
    ip = cbedata.get_offline(contents, 'newfile-host', 'val').split(':')[0]
    tcpn = cbedata.get_offline(contents, 'newfile-host', 'val').split(':')[1]

    print(f'Opening TCP connection to {ip}:{tcpn}')
    
    tcp_send(ip, int(tcpn), contents, block = False)
    
def loadfromdisk(path):
    f = open(path, 'r')
    T.delete(1.0, 'end')
    T.insert(1.0, f.read())
    f.close()
    
def savetodisk():
    import cbedata
    c = T.get(1.0, tk.END).replace('\n','')
    dest = cbedata.get_offline(c, 'newfile-host', 'val').split(':')[0]
    srcfp = cbedata.get_offline(c, 'newfile-origin', 'val').replace(':', '')
    fn = srcfp + ',to,' + dest
    f = open(fn, 'w')
    f.write(c)
    f.close()
    T.delete(1.0, 'end')
    T.insert(1.0, f'Saved request body to file {fn}')
    
        

tk.Label().grid(row=8) # blank space    and transmit button 
txbt = tk.Button(text ="Press to generate request", command = transmit, bg = 'green', fg = 'white')
txbt.grid(row=9)

txbt01 = tk.Button(text ="Press to load request from disk", command = lambda: loadfromdisk(T.get(1.0, tk.END).replace('\n','')), bg = 'green', fg = 'white')
txbt01.grid(row=9, column=1)

txbt1 = tk.Button(text ="Press to TRANSMIT request", command = opensocket, bg = 'yellow', fg = 'black')
txbt1.grid(row=9, column=2)

txbt101 = tk.Button(text ="Press to save request for later", command = savetodisk, bg = 'purple', fg = 'white')
txbt101.grid(row=9, column=3)


T.grid(row=10, column = 4)





root.mainloop()
