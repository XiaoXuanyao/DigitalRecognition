from keras import optimizers
from keras.utils import custom_object_scope
from blocks import conv
import keras
import random
import os
import numpy as np


custom_objects = {
    "Conv2D": conv.Conv2D,
    "DSConv2D": conv.DSConv2D,
    "BottleNeck": conv.BottleNeck
}


class MyBaseModel:

    def __init__(self, inpt, x, initopt):
        self.model = keras.Model(inputs=inpt, outputs=x)
        self.model.compile(
            optimizers.Adam(learning_rate=0.0001),
            loss=initopt["loss"],
            metrics=initopt["metrics"],
            weighted_metrics=[]
        )
        self.model.build(input)
        os.makedirs("runs/models", exist_ok=True)
        with open(f'runs/models/{self.name}Summary.txt', 'w') as f:
            self.model.summary(print_fn=lambda x: f.write(x + '\n'))
        
    def savemodel(self, name=None):
        name = self.name if name is None else name
        self.model.save(f"runs/models/{name}.h5")
    
    def readmodel(self, name=None):
        name = self.name if name is None else name
        with custom_object_scope(custom_objects):
            self.model = keras.models.load_model(f"runs/models/{name}.h5")
    
    def train(self, data, trainopt):
        random.shuffle(data)
        x, y, w = [], [], []
        for e in data:
            x.append(e["x"]), y.append(e["y"]), w.append(e["w"])
        x, y, w = np.array(x), np.array(y), np.array(w)
        for i in range(trainopt["epochs"]):
            res = self.model.fit(
                x=x, y=y,
                sample_weight=w,
                epochs=1,
                batch_size=trainopt["batch_size"],
                validation_split=0.3,
                verbose=0
            )
            print(f"epoch {i+1}: "
                  f"categorical_accuracy: {res.history['categorical_accuracy'][0]:.4f}  "
                  f"val_categorical_accuracy: {res.history['val_categorical_accuracy'][0]:.4f}")
    
    def predict(self, x):
        return self.model.predict(x)
