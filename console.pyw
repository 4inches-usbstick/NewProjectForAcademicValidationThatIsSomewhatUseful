import tkinter as tk
import hashlib, random, os

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
    import socket, time, cbedata
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
    
def recvend_cacllback(tf, part = 'endonsend'):
    import cbedata
    f = open('config.txt', 'r')
    c = f.read()
    f.close()
    current = cbedata.get_offline(c, f'application_config-{part}', 'val')
    newc = c.replace(f'{part}=={current}', f'{part}=={str(tf)}')
    
    f = open('config.txt', 'w')
    f.write(newc)
    f.close()




tk.Label().grid(row=8) # blank space    and transmit button 
txbt = tk.Button(text ="Generate request", command = transmit, bg = 'green', fg = 'white')
txbt.grid(row=9)

txbt01 = tk.Button(text ="Load request from disk", command = lambda: loadfromdisk(T.get(1.0, tk.END).replace('\n','')), bg = 'green', fg = 'white')
txbt01.grid(row=9, column=1)

txbt1 = tk.Button(text ="[!] TRANSMIT", command = opensocket, bg = 'yellow', fg = 'black')
txbt1.grid(row=9, column=2)

txbt101 = tk.Button(text ="Save request info to disk", command = savetodisk, bg = 'purple', fg = 'white')
txbt101.grid(row=9, column=3)


T.grid(row=10, column = 4)

greetingrecv = tk.Label(text="Receive a File")
greetingrecv.config(font=("", 24))
greetingrecv.grid(row=11,column=0)

txbt1012 = tk.Button(text = "Begin", command = lambda: os.system('start takeuploadedfile.py'), bg = 'green', fg = 'white')
txbt1012.grid(row=12, column=0)

tk.Label(text="[Close listen window to stop ALL transfers]").grid(row=13)

greetingrecvfg = tk.Label(text="Cfg Adjust")
greetingrecvfg.config(font=("", 24))
greetingrecvfg.grid(row=11,column=1)

tk.Label(text="Exit on OKVerdict option").grid(row=12, column=1)

recvend = tk.Button(text = "Exit on OKVerdict", command = lambda: recvend_cacllback(1), bg = 'green', fg = 'white')
recvend.grid(row=12,column=2)

recvend1 = tk.Button(text = "No exit on OKVerdict", command = lambda: recvend_cacllback(0), bg = 'red', fg = 'white')
recvend1.grid(row=12,column=3)

tk.Label(text="Sender port").grid(row=13, column=1)
tk.Label(text="Recvr port").grid(row=14, column=1)

sendset = tk.Entry()
sendset.grid(row=13,column=2)

rsendset1 = tk.Entry()
rsendset1.grid(row=14,column=2)

ss = tk.Button(text = "Set sender port", command = lambda: recvend_cacllback(sendset.get(),part='sendport'), bg = 'gray', fg = 'white')
ss.grid(row=13,column=3)

rss = tk.Button(text = "Set recv port", command = lambda: recvend_cacllback(rsendset1.get(),part='takeport'), bg = 'gray', fg = 'white')
rss.grid(row=14,column=3)
root.mainloop()
