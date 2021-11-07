import tkinter as tk
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
pkt = tk.Label(text="Packet size (advised <= 900)")
pkt_box = tk.Entry()

pkt.grid(row=7,column=0)
pkt_box.grid(row=7,column=1)



root.mainloop()
