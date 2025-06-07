
import os
import threading
import cv2
import numpy as np
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, wait
from keras import callbacks

from DRModel import DRModel
from Debug import *



class LoadDataset():

    def __init__(self, path:str):
        self.path = path
        Debug.log("DataLoader", f"Load dataset initialized, dataset path: {path}")

    def read(self, workers=6):
        dataque = Queue()
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
            executor = ThreadPoolExecutor(max_workers=workers)
            for filename in os.listdir(self.path):
                executor.submit(loadfunc, filename)
                Debug.log("DataLoader", f"Read file {filename}", type=1, end="\r")
            executor.shutdown(wait=True)
        Debug.log("DataLoader", "Load finished.")
        return list(dataque.queue)



class MyLoggingCallback(callbacks.Callback):
    def set_model(self, model):
        self.model = model

    def on_train_begin(self, logs=None):
        self.current_epoch = 0
        TrainModel.cEpoch = 0
        TrainModel.maxEpoch = self.params['epochs']
        TrainModel.maxBatch = self.params["steps"]

    def on_epoch_begin(self, epoch, logs=None):
        self.current_epoch = epoch
        TrainModel.cEpoch = epoch + 1
        Debug.log("Train", f"=== Epoch {epoch + 1} ===")

    def on_train_batch_end(self, batch, logs=None):
        TrainModel.cBatch = batch
        Debug.log("Train", f"[Epoch {self.current_epoch + 1}/{self.params['epochs']}] {batch / TrainModel.maxBatch * 100:.2f} %", end="\r")

    def on_epoch_end(self, epoch, logs=None):
        loss = logs.get('loss')
        acc = logs.get('categorical_accuracy')
        valloss = logs.get('val_loss')
        valacc = logs.get('val_categorical_accuracy')
        TrainModel.cLoss.append(loss)
        TrainModel.cAcc.append(acc)
        TrainModel.cvalLoss.append(valloss)
        TrainModel.cvalAcc.append(valacc)
        print("")
        Debug.log("Train", f"loss: {loss:.4f}, acc: {acc:.4f}, val_loss: {valloss:.4f}, val_acc: {valacc:.4f}", end="\n")



class TrainModel():

    isTraining = False
    
    cEpoch = 0
    maxEpoch = 0
    cBatch = 0
    maxBatch = 0
    cLoss = []
    cAcc = []
    cvalLoss = []
    cvalAcc = []

    def train(model:DRModel, datapath:str, args:dict):
        TrainModel.isTraining = True       
        TrainModel.cEpoch = 0
        TrainModel.maxEpoch = 0
        TrainModel.cBatch = 0
        TrainModel.maxBatch = 0
        TrainModel.cLoss = []
        TrainModel.cAcc = []
        TrainModel.cvalLoss = []
        TrainModel.cvalAcc = []
        args["callbacks"] = [MyLoggingCallback()]
        data = LoadDataset(datapath).read()
        Debug.log("Train", "Start training.")
        model.train(data, args)
        model.savemodel()
        Debug.log("Train", "Training finished.")
        time.sleep(5)
        TrainModel.isTraining = False