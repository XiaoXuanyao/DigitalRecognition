
from keras import layers
from blocks import model

from Debug import *



class DRModel(model.MyBaseModel):

    def __init__(self, name:str="DRModel_default"):
        self.name = name
        inpt = layers.Input(shape=(28, 28))
        x = layers.Reshape([28 * 28])(inpt)
        x = layers.Dense(units=512, activation="tanh")(x)
        x = layers.Dense(units=512, activation="tanh")(x)
        x = layers.Dense(units=10, activation="softmax")(x)
        super().__init__(inpt, x, {
            "loss": "categorical_crossentropy",
            "metrics": ["categorical_accuracy"]
        })
        Debug.log("DRModel", f"New model initialized, model name: {self.name}")
