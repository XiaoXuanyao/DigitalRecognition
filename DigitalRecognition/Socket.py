
import queue
import threading
from socket import socket
from Debug import *



class Socket():

    def __init__(self, stype, host:str="127.0.0.1", port:int=25565):
        assert stype=="Server" or stype=="Client", "stype must be Server/Client"
        self.name = "Socket" + stype
        self.host = host
        self.port = port
        self.socket = socket()

    def start(self):
        Debug.log(self.name, f"start on {self.host}:{self.port}")
        
    def receive(self, soc:socket, log:bool=False, dsthost:str="Unknown"):
        from Respond import Respond
        mes_queue = queue.Queue()
        Respond(mes_queue, self, log, dsthost)
        
        def recv():
            while True:
                mes = b""
                while True:
                    buff = soc.recv(1024 * 32)
                    if buff == b'': break
                    mes += buff
                    if b"\r\n" in mes: break
                headers, middle, body = mes.partition(b"\r\n\r\n")
                clength = 0
                for line in headers.decode().splitlines():
                    if line.lower().startswith("content-length:"):
                        clength = int(line.split(":")[1].strip())
                while len(body) < clength:
                    if buff == b'': break
                    buff = soc.recv(1024 * 32)
                    body += buff
                
                if len(mes) == 0:
                    self.close(soc, dsthost)
                    return
                mes = headers + middle + b"data: " + body
                mes = mes.decode(errors="ignore")
                head = mes.split("\r\n")[0]
                if log: Debug.log(self.name, f"Receive: {head}")
                mes_queue.put(mes)

        recv_thread = threading.Thread(target=recv, args=[])
        recv_thread.start()

    def send(self, soc:socket, mes:str, log:bool=False, dsthost:str="Unknown"):
        soc.send(mes.encode())
        if log: Debug.log(self.name, f"Send to {dsthost}: {mes}")

    def sendb(self, soc:socket, mes:bytes, log:bool=False, dsthost:str="Unknown"):
        soc.send(mes)
        if log: Debug.log(self.name, f"Send to {dsthost}: --bytes--, len: {len(mes)}")
    
    def close(self, soc:socket, dsthost="UnKnown"):
        soc.close()
        Debug.log(self.name, f"Socket close: {dsthost}")
      


class SocketServer(Socket):

    def __init__(self, host:str="0.0.0.0", port:int=25565):
        super().__init__("Server", host, port)

    def start(self, log:bool=False):
        self.socket.bind((self.host, self.port))
        self.socket.listen(100)
        self.clients = { }
        super().start()
        while True:
            client, caddr = self.socket.accept()
            self.clients[caddr] = client
            self.receive(client, log, caddr)
            Debug.log(self.name, f"New connection accepted: {caddr}")
    
    def receive(self, soc:socket, log:bool, dsthost:str="Unknown"):
        super().receive(soc, log, dsthost)

    def send(self, mes:str, log:bool=False, dsthost=[]):
        if len(dsthost) == 0:
            for loc, soc in self.clients:
                super().send(soc, mes, log, loc)
        else:
            for loc in dsthost:
                super().send(self.clients[loc], mes, log, loc)

    def sendb(self, mes:str, log:bool=False, dsthost=[]):
        if len(dsthost) == 0:
            for loc, soc in self.clients:
                super().sendb(soc, mes, log, loc)
        else:
            for loc in dsthost:
                super().sendb(self.clients[loc], mes, log, loc)



class SocketClient(Socket):

    def __init__(self, host:str="127.0.0.1", port:int=25565):
        super().__init__("Client", host, port)

    def start(self, log:bool=False):
        self.socket.connect((self.host, self.port))
        super().start()
        self.receive(self.socket, log, self.host)
        Debug.log(self.name, f"Connection succeed: {self.host}")
        
    def receive(self, soc:socket, log:bool, dsthost:str="Unknown"):
        super().receive(soc, log, dsthost)

    def send(self, soc:socket, mes:str, log:bool=False):
        super().send(self.socket, mes, log, self.address)