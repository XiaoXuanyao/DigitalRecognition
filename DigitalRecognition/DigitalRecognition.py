
import time
import os
import threading

from Debug import *
from Socket import *
from DRModel import DRModel
from Train import TrainModel
from Service import Service



Debug.log("Main", "Server start.")
os.makedirs("../ProgramDataset/users", exist_ok=True)

model = DRModel()
try:
    model.readmodel()
except:
    TrainModel.train(model, "../datasets/mnist", {
                    "epochs": 100,
                    "batch_size": 128
                    })
Service.model = model

def serverfunc():
    server = SocketServer("0.0.0.0", 25565)
    server.start(log=True)

serverthread = threading.Thread(target=serverfunc, args=[])
serverthread.start()

while True:
    time.sleep(1)