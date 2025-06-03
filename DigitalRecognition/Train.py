
import os
import threading
import cv2
import keras
from queue import Queue

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
            img = cv2.imread(self.path + "/" + filename)
            img = cv2.resize(img, (28, 28))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img = img.reshape((28, 28))
            dataque.put({
                "x": img,
                "y": label,
                "w": 1
                })
        with CostTime("DataLoader"):
            for filename in os.listdir(self.path):
                # loadfunc(filename)
                loadthread = threading.Thread(target=loadfunc, args=[filename])
                loadthread.start()
                Debug.log("DataLoader", f"Read files {filename}", type=1, end="\b\r")
        while not dataque.empty():
            data.append(dataque.get())
            Debug.log("DataLoader", f"processing... ({len(data)})", type=1, end="\b\r")
        Debug.log("DataLoader", "Load finished.")
        return data



class TrainModel():

    def train(model:DRModel, datapath:str, args:dict):
        Debug.log("Train", "Start training.")
        data = LoadDataset(datapath).read()
        model.train(data, args)
        model.savemodel()
        Debug.log("Train", "Start finished.")