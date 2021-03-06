import socket
from  threading import Thread ,Barrier
import sys
import os
from hashlib import sha256
from time import perf_counter_ns
from os import listdir
from os.path import isfile, join
from datetime import datetime
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
            i=0
            print('Servidor ON')
            self.tpc_server.listen()
            while True:

                if self.barrier.broken:
                    self.barrier.reset()
                client_tcp,addr = self.tpc_server.accept()
                client_thread = Thread(target = self.new_client,args=(client_tcp,self.udp_server,addr,self.barrier,i))
                i+=1
                client_thread.start()
        except Exception as e:
            print(e)
            
            
    def new_client(self,client_tcp,udp_server,addr,barrier,i):
        print('Recibi cliente')
        barrier.wait()
        time = 0
        same = ''
        packs = 0
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
                    #---- Empezamos comunicaci??n UDP ----#
                    tic = perf_counter_ns()
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
                    toc= perf_counter_ns()
                    time = toc - tic 
                    print(packs,'paquetes')
                    same = client_tcp.recv(self.BUFFER).decode()
                    print(same)
        except Exception as e:
            print(e)

        with open(f'logs/client{i}.txt','w') as cf:
            cf.write(f'{time}ns;{self.file_name};cliente{i},{same};{file_size};{packs}\n')

        client_tcp.close()

    def get_hash(self):
        security=''
        with open(self.file_name, 'rb') as f:
            sha= f.read()
            security = sha256(sha).hexdigest()
        return security
    def get_size(self):
        return os.path.getsize(self.file_name)

def joinLogs():
    mypath= 'logs/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print(onlyfiles)
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    with open (f'{dt_string}.txt','a+') as logmaster:
        logmaster.write('nombre_archivo;tam??o_archivo;nombre_cliente;entrega_exitosa;tiempo;num_bytes;paquetes\n')
        for client_log in onlyfiles:
            with open(f'logs/{client_log}','r') as f:
                logmaster.write(f.read())


if __name__ == '__main__':
    try :
        num_conections = int(input('Numero de conexiones simultaneas\n'))
        file_name = input('\n Escriba el nombre del archivo\n ejemplo: prueba.bin\n')
        server = serverUDP(num_conections,file_name)
        server.start()
    except KeyboardInterrupt as e:
        joinLogs()

