
from unittest import result
import cv2
import json
import base64
import numpy as np
import shutil

from DRModel import DRModel
from Encryption import Encryption
from Socket import *
from Debug import *
from Train import TrainModel

class Service():

    model:DRModel = None

    def checkservice(httpmes:dict, respmes:dict):
        if httpmes.get("sname", None) == None:
            Service.unknownservice(respmes)
        elif httpmes["sname"] == "register":
            Service.register(httpmes, respmes)
        elif httpmes["sname"] == "modifyusername":
            Service.modifyusername(httpmes, respmes)
        elif httpmes["sname"] == "login":
            Service.login(httpmes, respmes)
        elif httpmes["sname"] == "removeuser":
            Service.removeuser(httpmes, respmes)
        elif httpmes["sname"] == "uploadimg/train":
            Service.uploadimage("train", httpmes, respmes)
        elif httpmes["sname"] == "uploadimg/test":
            Service.uploadimage("test", httpmes, respmes)
        elif httpmes["sname"] == "clearimg/train":
            Service.clearimage("train", httpmes, respmes)
        elif httpmes["sname"] == "train":
            Service.train(httpmes, respmes)
        elif httpmes["sname"] == "getstatu/train":
            Service.getstatu("train", httpmes, respmes)
        elif httpmes["sname"] == "test":
            Service.test(httpmes, respmes)
        elif httpmes["sname"] == "checkadmin":
            Service.checkadmin(httpmes, respmes)
        elif httpmes["sname"] == "getadminpage":
            Service.getadminpage(httpmes, respmes)
        elif httpmes["sname"] == "getusermes":
            Service.getusermes(httpmes, respmes)
        else:
            Service.unknownservice(respmes)
    
    def readusermes(username:str):
        res = None
        if os.path.exists(f"../ProgramDataset/usersmes/{username}.txt"):
            res = { }
            with open(f"../ProgramDataset/usersmes/{username}.txt") as f:
                lines = f.readlines()
                res["lastlogin"] = lines[0].strip()
                res["visitcnt"] = int(lines[1].strip())
                res["trylogincnt"] = int(lines[2].strip())
        return res
    
    def writeusermes(username:str, usermes:dict):
        if not os.path.exists("../ProgramDataset/usersmes"):
            os.makedirs("../ProgramDataset/usersmes")
        with open(f"../ProgramDataset/usersmes/{username}.txt", "w") as f:
            f.writelines([
                usermes["lastlogin"] + "\n",
                str(usermes["visitcnt"]) + "\n",
                str(usermes["trylogincnt"]) + "\n"
            ])

    def register(httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        username = Encryption.sha256(data["username"])
        password = Encryption.sha256(data["password"])
        phone = Encryption.sha256(data["phone"])
        if os.path.exists(f"../ProgramDataset/users/{username}.txt"):
            res = "Result: User already exist"
        else:
            with open(f"../ProgramDataset/users/{username}.txt", "w") as f:
                f.writelines([password, "\n", phone, "\n"])
            usermes = {
                "lastlogin": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "visitcnt": 0,
                "trylogincnt": 0
                }
            Service.writeusermes(username, usermes)
            res = "Result: OK"
        respmes["data"] = res.encode()
    
    def modifyusername(httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        username = Encryption.sha256(data["username"])
        newusername = Encryption.sha256(data["newusername"])
        src = f"../ProgramDataset/users/{username}.txt"
        dst = f"../ProgramDataset/users/{newusername}.txt"
        if os.path.exists(src):
            if not os.path.exists(dst):
                shutil.move(src, dst)
                res = "Result: OK"
            else:
                res = "Result: Username exists"
        else: res = "Result: User not exist"
        respmes["data"] = res.encode()
    
    def login(httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        username = Encryption.sha256(data["username"])
        password = Encryption.sha256(data["password"])
        if os.path.exists(f"../ProgramDataset/users/{username}.txt"):
            with open(f"../ProgramDataset/users/{username}.txt") as f:
                ctn = f.readlines()[0][:-1]
            usermes = Service.readusermes(username)
            if ctn == password:
                res = "Result: OK"
                usermes["lastlogin"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                usermes["visitcnt"] += 1
            else:
                res = "Result: Password error"
                usermes["trylogincnt"] += 1
            Service.writeusermes(username, usermes)
        else: res = "Result: Username not exist"
        respmes["data"] = res.encode()
    
    def removeuser(httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        username = Encryption.sha256(data["username"])
        if os.path.exists(f"../ProgramDataset/users/{username}.txt"):
            os.remove(f"../ProgramDataset/users/{username}.txt")
            res = "Result: OK"
        else: res = "Result: User not exist"
        respmes["data"] = res.encode()

    def uploadimage(stype:str, httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        imgfolder = data.get("imgfolder", f"ProgramDataset/tmp/images/{stype}")
        for oneimg in data["data"]:
            filename = oneimg["filename"]
            imgdata = base64.b64decode(oneimg["imgdata"])
            os.makedirs(f"../{imgfolder}", exist_ok=True)
            with open(f"../{imgfolder}/{filename}", "wb") as f:
                f.write(imgdata)
        res = { "Result": "OK", "Cnt": len(data["data"]) }
        res = json.dumps(res)
        respmes["data"] = res.encode()

    def clearimage(stype:str, httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        imgfolder:str = data.get("imgfolder", f"tmp/images/{stype}")
        if len(imgfolder) > 4 and imgfolder[:4] == "tmp/":
            if os.path.exists("../ProgramDataset/" + imgfolder):
                shutil.rmtree("../ProgramDataset/" + imgfolder)
                res = "Result: OK"
            else:
                res = "Result: Permission denied"
        else:
            res = "Result: Permission denied"
        respmes["data"] = res.encode()

    def train(httpmes:str, respmes:dict):
        if TrainModel.isTraining:
            res = "Result: Another training task is running."
        else:
            data = json.loads(httpmes["data"])
            epochs = data.get("epochs", 100)
            batchsize = data.get("batchsize", 128)
            learningrate = data.get("learningrate", 0.001)
            model = DRModel(learning_rate=learningrate)
            def trainfunc():
                TrainModel.train(model, "../ProgramDataset/tmp/images/train", {
                    "epochs": epochs,
                    "batch_size": batchsize,
                    })
                Service.model = model
            trainthread = threading.Thread(target=trainfunc, args=[])
            trainthread.start()
            res = "Result: OK"
        respmes["data"] = res.encode()
    
    def getstatu(stype:str, httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        if stype == "train":
            if not TrainModel.isTraining:
                res = { "Result" : "Training not started" }
            else:
                res = {
                    "Result": "OK",
                    "Data": {
                        "cEpoch": TrainModel.cEpoch,
                        "maxEpoch": TrainModel.maxEpoch,
                        "cBatch": TrainModel.cBatch,
                        "maxBatch": TrainModel.maxBatch,
                        "cLoss": TrainModel.cLoss,
                        "cAcc": TrainModel.cAcc,
                        "cvalLoss": TrainModel.cvalLoss,
                        "cvalAcc": TrainModel.cvalAcc
                    },
                    "Statu": TrainModel.statu
                }
        else:
            res = { "Result" : "No such statu" }
        res = json.dumps(res)
        respmes["data"] = res.encode()

    def test(httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        imgfolder = data.get("imgfolder", "ProgramDataset/tmp/images/test")
        filename = data["filename"]
        img = cv2.imread(f"../{imgfolder}/{filename}")
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = cv2.resize(img, (28, 28))
        img = np.reshape(img, (1, 28, 28))
        valres = Service.model.predict(img)[0]
        res = json.dumps({
            "Result": "OK",
            "Cfds": valres.tolist()
            })
        respmes["data"] = res.encode()

    def checkadmin(httpmes:dict, respmes:dict):
        data = json.loads(httpmes["data"])
        username = Encryption.sha256(data["username"])
        os.makedirs("../ProgramDataset", exist_ok=True)
        if os.path.exists("../ProgramDataset/admin.txt"):
            with open("../ProgramDataset/admin.txt") as f:
                for line in f.readlines():
                    if line.strip() == username:
                        res = "Result: OK"
                        break
                else:
                    res = "Result: Not admin"
        else:
            res = "Result: Not admin"
        respmes["data"] = res.encode()
    
    def getadminpage(httpmes:dict, respmes:dict):
        tmp = { }
        Service.checkadmin(httpmes, tmp)
        if tmp["data"].decode() != "Result: OK":
            respmes["data"] = b"<!DOCTYPE html><html><body><h1>Permission denied</h1></body></html>"
        elif os.path.exists("../DigitalRecognitionWebsites/admin.html"):
            with open("../DigitalRecognitionWebsites/admin.html", "rb") as f:
                respmes["data"] = f.read()
        else:
            respmes["data"] = b"<!DOCTYPE html><html><body><h1>Admin page not found</h1></body></html>"

    def getusermes(httpmes:dict, respmes:dict):
        Service.checkadmin(httpmes, respmes)
        if respmes["data"].decode() != "Result: OK":
            res = { "Result": "Permission denied" }
        else:
            data = [ ]
            for username in os.listdir("../ProgramDataset/users"):
                data.append(Service.readusermes(username[:-4]))
            res = {
                "Result": "OK",
                "Data": data
                }
        res = json.dumps(res)
        respmes["data"] = res.encode()

    def unknownservice(respmes:dict):
        Debug.log("Service", "Unknown service requested")
        respmes["data"] = "".encode()