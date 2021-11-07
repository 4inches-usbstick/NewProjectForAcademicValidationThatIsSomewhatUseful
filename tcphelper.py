import socket

def send(host, port, contents, block = False):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, int(port)))
        s.sendall( bytes(contents,'ASCII') )
        if not block:
            return None
        if block:
            print('Sync. Control handed off to send() function.')
            data = s.recv(1024)
            return str(data)
            
while True:
    s = input()
    print(send('127.0.0.1', '1711', s, False))