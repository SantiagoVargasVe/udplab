import socket
from  threading import Thread
import sys
import os


class serverUDP():
    

    def __init__(self,num_conections,file):
        self.TCP_PORT = 7000 
        self.UDP_PORT = 7001
        self.BUFFER = 2048
        self.TCP= (socket.gethostbyname(socket.gethostname()),self.TCP_PORT)
        self.UDP= (socket.gethostbyname(socket.gethostname()),self.UDP_PORT)

        self.tpc_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.udp_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.tpc_server.bind(self.TCP)
        self.udp_server.bind(self.UDP)

    def start(self):
        try:

            self.tpc_server.listen()
            while True:
                client_tcp,addr = self.server_tcp.accept()
                client_thread = Thread(target = self.new_client,args=(client_tcp,udp_server,addr))
        except Exception as e:
            print(e)
            
            
    def new_client(client_tcp,udp_server,addr):
        try:
            msg = client_tcp.recv(self.BUFFER).decode()
            if msg=='hello':
                
        except Exception as e:
            print(e)



if __name__ == '__main__':
    num_conections = int(input('Numero de conexiones simultaneas\n'))
    file_name = input('\n Escriba el nombre del archivo\n ejemplo: prueba.bin\n')
    server = serverUDP(num_conections,file_name)
    server.start()
