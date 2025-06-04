
from unittest import result
import cv2
import json
import base64
import numpy as np

from DRModel import DRModel
from Encryption import Encryption
from Socket import *
from Debug import *

class Service():

    model:DRModel = None
    training:bool = False

    def checkservice(httpmes:dict, respmes:dict):
        if httpmes.get("sname", None) == None:
            Service.unknownservice(respmes)
        elif httpmes["sname"] == "register":
            Service.register(httpmes, respmes)
        elif httpmes["sname"] == "login":
            Service.login(httpmes, respmes)
        elif httpmes["sname"] == "uploadimg/train":
            Service.uploadimage("train", httpmes, respmes)
        elif httpmes["sname"] == "uploadimg/test":
            Service.uploadimage("test", httpmes, respmes)
        elif httpmes["sname"] == "train":
            Service.train(httpmes, respmes)
        elif httpmes["sname"] == "test":
            Service.test(httpmes, respmes)
        else:
            Service.unknownservice()

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
            res = "Result: OK"
        respmes["data"] = res.encode()
    
    def login(httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        username = Encryption.sha256(data["username"])
        password = Encryption.sha256(data["password"])
        if os.path.exists(f"../ProgramDataset/users/{username}.txt"):
            with open(f"../ProgramDataset/users/{username}.txt") as f:
                ctn = f.readlines()[0][:-1]
            if ctn == password: res = "Result: OK"
            else: res = "Result: Password error"
        else: res = "Result: Username not exist"
        respmes["data"] = res.encode()

    def uploadimage(stype:str, httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        imgfolder = data.get("imgfolder", "ProgramDataset/tmp/images")
        filename = data["filename"]
        imgdata = base64.b64decode(data["imgdata"])
        if stype == "train" and os.path.exists(f"../{imgfolder}/{filename}"):
            res = "Result: Image already exist"
        else:
            os.makedirs(f"../{imgfolder}", exist_ok=True)
            with open(f"../{imgfolder}/{filename}", "wb") as f:
                f.write(imgdata)
            res = "Result: OK"
        respmes["data"] = res.encode()

    def train(httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        epochs = data.get("epochs", 100)
        batch_size = data.get("batch_size", 128)
        def trainfunc():
            Service.training = True
            Service.model.Train(Service.model, "../datasets/mnist", {
                "epochs": epochs,
                "batch_size": batch_size
                })
            Service.training = False

        trainthread = threading.Thread(target=trainfunc, args=[])
        trainthread.start()

    def test(httpmes:str, respmes:dict):
        data = json.loads(httpmes["data"])
        imgfolder = data.get("imgfolder", "ProgramDataset/tmp/images")
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

    def unknownservice(respmes:dict):
        Debug.log("Service", "Unknown service requested")
        respmes["data"] = "".encode()