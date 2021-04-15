import socket
from  threading import Thread ,Barrier
import sys
import os
from hashlib import sha256

class serverUDP():
    

    def __init__(self,num_conections,file_name):
        self.TCP_PORT = 7000 
        self.UDP_PORT = 7001
        self.BUFFER = 2048
        self.barrier= Barrier(num_conections)
        self.TCP= (socket.gethostbyname(socket.gethostname()),self.TCP_PORT)
        self.UDP= (socket.gethostbyname(socket.gethostname()),self.UDP_PORT)
        self.file_name= file_name
        self.tpc_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.udp_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.tpc_server.bind(self.TCP)
        self.udp_server.bind(self.UDP)

    def start(self):
        try:
            print('Servidor ON')
            self.tpc_server.listen()
            while True:

                if self.barrier.broken:
                    self.barrier.reset()
                client_tcp,addr = self.tpc_server.accept()
                client_thread = Thread(target = self.new_client,args=(client_tcp,self.udp_server,addr,self.barrier))
                client_thread.start()
        except Exception as e:
            print(e)
            
            
    def new_client(self,client_tcp,udp_server,addr,barrier):
        print('Recibi cliente')
        barrier.wait()
        print('Supere barrera')
        try:
            msg = client_tcp.recv(self.BUFFER).decode()
            print('recibo mensaje')
            print(msg)
            if msg=='hello':
                file_size= f"{self.get_size()}"
                file_hash= self.get_hash()
                client_tcp.sendall(f'{self.file_name.encode()};{file_size};{file_hash}'.encode())
                confirm = client_tcp.recv(self.BUFFER).decode()
                if confirm == 'confirm':
                    print("Tamos activos")
                    #---- Empezamos comunicación UDP ----#
                    hello_udp,addr_client = udp_server.recvfrom(self.BUFFER)
                    print(hello_udp.decode(),'recibi UDP')
                    with open(self.file_name,'rb') as f:
                        info= f.read(self.BUFFER)
                        packs= 1
                        while info:
                            udp_server.sendto(info,addr_client)
                            info = f.read(self.BUFFER)
                            packs+=1
                    print('Terminamos de mandar paquetes :-)')
                    print(packs,'paquetes')
                    same = client_tcp.recv(self.BUFFER).decode()
                    print(same)
        except Exception as e:
            print(e)
        client_tcp.close()

    def get_hash(self):
        security=''
        with open(self.file_name, 'rb') as f:
            sha= f.read()
            security = sha256(sha).hexdigest()
        return security
    def get_size(self):
        return os.path.getsize(self.file_name)


if __name__ == '__main__':
    num_conections = int(input('Numero de conexiones simultaneas\n'))
    file_name = input('\n Escriba el nombre del archivo\n ejemplo: prueba.bin\n')
    server = serverUDP(num_conections,file_name)
    server.start()
