
import os
import shutil
import threading

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

from Debug import *
from Socket import *
from DRModel import DRModel
from Train import TrainModel
from Service import Service



Debug.log("Main", "Server start.")
os.makedirs("../ProgramDataset/users", exist_ok=True)
os.makedirs("../ProgramDataset/tmp", exist_ok=True)
shutil.rmtree("../ProgramDataset/tmp")

model = DRModel()
try:
    model.readmodel()
except:
    TrainModel.train(model, "../datasets/mnist", {
        "epochs": 100,
        "batch_size": 32
        })
Service.model = model

def serverfunc():
    server = SocketServer("0.0.0.0", 25565)
    server.start(log=True)

serverthread = threading.Thread(target=serverfunc, args=[])
serverthread.start()

while True:
    time.sleep(1)