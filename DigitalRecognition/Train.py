
import os
import threading
import cv2
import numpy as np
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from DRModel import DRModel
from Debug import *



class LoadDataset():

    def __init__(self, path:str):
        self.path = path
        Debug.log("DataLoader", f"Load dataset initialized, dataset path: {path}")

    def read(self):
        dataque = Queue()
        data = []
        def loadfunc(filename):
            label = [0] * 10
            label[int(filename.split(".")[0].split("_")[-1])] = 1
            with open(self.path + "/" + filename, "rb") as f:
                imgbuf = f.read()
            img = cv2.imdecode(np.frombuffer(imgbuf, np.uint8), cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img = cv2.resize(img, (28, 28))
            dataque.put({
                "x": img,
                "y": label,
                "w": 1
                })
        with CostTime("DataLoader"):
            with ThreadPoolExecutor(max_workers=4) as executor:
                for filename in os.listdir(self.path):
                    executor.submit(loadfunc, filename)
                    Debug.log("DataLoader", f"Read files {filename}", type=1, end="\b\r")
        while not dataque.empty():
            data.append(dataque.get())
            Debug.log("DataLoader", f"processing... ({len(data)})", type=1, end="\b\r")
        Debug.log("DataLoader", "Load finished.")
        return data



class TrainModel():

    def train(model:DRModel, datapath:str, args:dict):
        data = LoadDataset(datapath).read()
        Debug.log("Train", "Start training.")
        model.train(data, args)
        model.savemodel()
        Debug.log("Train", "Start finished.")