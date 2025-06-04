from Debug import *
from keras import optimizers
from keras.utils import custom_object_scope
from blocks import conv
import keras
import random
import os
import numpy as np
import tensorflow as tf


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
        x, y = [], []
        for e in data:
            x.append(e["x"]), y.append(e["y"])
        x, y = np.array(x), np.array(y)
        split = int(len(x) * 0.7)
        traindataset = tf.data.Dataset.from_tensor_slices((x[:split], y[:split])) \
            .batch(trainopt["batch_size"]) \
            .prefetch(tf.data.AUTOTUNE)
        valdataset = tf.data.Dataset.from_tensor_slices((x[split:], y[split:])) \
            .batch(trainopt["batch_size"]) \
            .prefetch(tf.data.AUTOTUNE)
        for i in range(trainopt["epochs"]):
            with CostTime("Train"):
                res = self.model.fit(
                    traindataset,
                    epochs=1,
                    validation_data=valdataset,
                    verbose=2
                )
                Debug.log("Train", f"epoch {i+1}: "
                        f"categorical_accuracy: {res.history['categorical_accuracy'][0]:.4f}  "
                        f"val_categorical_accuracy: {res.history['val_categorical_accuracy'][0]:.4f}")
    
    def predict(self, x):
        return self.model.predict(x)
