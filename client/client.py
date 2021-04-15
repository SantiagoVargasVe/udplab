import socket
import os
from os import listdir
from os.path import isfile, join
from hashlib import sha256
from threading import Thread, Barrier
from time import perf_counter_ns
from datetime import datetime

def joinLogs():
    mypath= 'logs/'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print(onlyfiles)
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    with open (f'{dt_string}.txt','a+') as logmaster:
        logmaster.write('nombre_archivo;tamño_archivo;nombre_cliente;entrega_exitosa;tiempo;num_bytes;paquetes\n')
        for client_log in onlyfiles:
            with open(f'logs/{client_log}','r') as f:
                logmaster.write(f.read())



def create_client(number_clients,addr,b,i):
    tcp_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_server.connect((addr,7000))
    udp_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0)
    addr_server = (addr,7001)
    print('Conexiones creadas')
    tcp_server.sendall(b'hello')
    print('Mande hello')
    meta= tcp_server.recv(2048).decode()
    print(meta)
    tcp_server.sendall(b'confirm')
    meta_file = meta.split(';')
    full_name = meta_file[0]
    file_size = int(meta_file[1])
    hash_server = meta_file[2]
    name = full_name.replace('\'','').split('.')
    firt_name= name[0][1:]
    security = ''
    ext = f'.{name[1]}'
    file_name =f'cliente{i}-Prueba-{number_clients}{ext}'
    udp_server.settimeout(2)
    timed_out=False
    #Iniciamos UDP#
    tic = perf_counter_ns()
    udp_server.sendto(b'hello',addr_server)
    end = 0
    packs = 0
    with open(f'archivosRecibidos/{file_name}','wb') as f:
        
        end= file_size
        print (end)
        while end>0:
            try:
                chunck = int(min(end,2048))
                info = udp_server.recv(chunck)
                f.write(info)
                packs+=1
                end -= len(info)

            except (socket.timeout):
                timed_out = True
                break
    toc = perf_counter_ns()

    time = toc - tic
    if timed_out:
        time -= 2000000000
    with open(f'archivosRecibidos/{file_name}','rb') as j:
        sha = j.read()
        security = sha256(sha).hexdigest()
        
    if security == hash_server :
        print('coincidimos')
        tcp_server.sendall(b'NO')
    else:
        tcp_server.sendall(b'SI')
        print('paila sotcio')

    with open (f'logs/client-{i}.txt','w') as n:
        n.write(f'{file_name};{file_size};client{i},{security == hash_server};{time};{file_size-end};{packs}\n')
    tcp_server.close()
    b.wait()



if __name__ == '__main__':
    number_clients = int(input("Cuantos clientes"))
    b = Barrier (number_clients+1)
    addr = socket.gethostbyname(socket.gethostname())
    for i in range(0,number_clients):
        Thread(target=create_client,args=(number_clients,addr,b,i)).start()
    
    b.wait()
    joinLogs()