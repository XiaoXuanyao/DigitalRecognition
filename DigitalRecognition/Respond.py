
import queue
import threading
import time
import enum
import os

import Socket
from Debug import *
from Service import Service



class RespondType(enum.Enum):

    FILE = 1,
    DATA = 2,
    SERVICE = 3,



class Respond():

    def __init__(self, que:queue.Queue, soc:Socket.SocketServer, log:bool, dsthost:str):
        self.que = que
        self.socket = soc
        self.dsthost = dsthost
        self.log = log

        def getmes():
            while True:
                while not self.que.empty():
                    mes = self.que.get()
                    self.analyze(mes)
                time.sleep(0.1)

        getmesthread = threading.Thread(target=getmes, args=[])
        getmesthread.start()

    def analyze(self, mes:str):
        lines = mes.split("\r\n")
        httpmes = {
            "head": {
                "protocal": lines[0].split(" ")[0],
                "path": lines[0].split(" ")[1],
                "version": lines[0].split(" ")[2]
                }
            }
        for line in lines[1:]:
            if len(line.split(":")) < 2: continue
            tag = line.split(":")[0]
            val = line.split(tag + ":")[1]
            httpmes[tag] = val[1:] if val[0:1] == " " else val
        rtype = ""
        if httpmes["head"]["path"][0:2] == "/?": rtype = RespondType.SERVICE
        elif httpmes["head"]["path"][0:1] == "/": rtype = RespondType.FILE
        elif httpmes["head"]["path"][0:1] == ":": rtype = RespondType.DATA
        else: return
        self.respond(rtype, httpmes)

    def genrespmes(respmes: dict):
        res = ""
        res += respmes["head"]["version"] + " " + respmes["head"]["statu"]
        res += "Content-Type: text/html; charset=utf-8\r\n"
        res += f"Content-Length: {len(respmes['data'])}\r\n"
        res += "Connection: close\r\n"
        res += "\r\n"
        res = res.encode() + respmes["data"]
        return res

    def checkfile(path:str):
        if path == "/":
            return "../DigitalRecognitionWebsites/index.html"
        elif path == "/favicon.ico":
            return "../DigitalRecognitionWebsites/favicon.png"
        elif path[1:] in os.listdir("../DigitalRecognitionWebsites") and path[1:] != "admin.html":
            return f"../DigitalRecognitionWebsites/{path}"
        Debug.log("Respond", f"Resources could not found: {path}")
        if path[-4:] == "html":
            return "../DigitalRecognitionWebsites/error.html"
        else:
            return "../DigitalRecognitionWebsites/space.txt"

    def respond(self, rtype:RespondType, httpmes:dict):

        respmes = {
            "head": {
                "version": httpmes["head"]["version"],
                "statu" : "OK 200"
                }
            }

        if rtype == RespondType.FILE:
            with open(Respond.checkfile(httpmes["head"]["path"]), "rb") as f:
                respmes["data"] = f.read()
        
        elif rtype == RespondType.SERVICE:
            Service.checkservice(httpmes, respmes)
    
        self.socket.sendb(Respond.genrespmes(respmes), self.log, [self.dsthost])