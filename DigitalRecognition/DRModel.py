
from keras import layers, losses, metrics, optimizers
from blocks import model, conv

from Debug import *



class DRModel(model.MyBaseModel):

    def __init__(self, name:str="DRModel_default", learning_rate=0.0001):
        self.name = name
        inpt = layers.Input(shape=(28, 28))
        # x = layers.Reshape([28 * 28])(inpt)
        # x = layers.Dense(units=512, activation="tanh")(x)
        # x = layers.Dense(units=512, activation="tanh")(x)
        x = layers.Reshape([1, 28, 28])(inpt)
        x = conv.Conv2D(c=16, k=3, s=2, p='same', act='leaky_relu')(x)
        x = layers.AveragePooling2D(pool_size=2, strides=2, padding='same', data_format="channels_first")(x)
        x = conv.Conv2D(c=32, k=3, s=2, p='same', act='leaky_relu')(x)
        x = layers.AveragePooling2D(pool_size=2, strides=2, padding='same', data_format="channels_first")(x)
        x = layers.Flatten(data_format="channels_first")(x)
        x = layers.Dense(units=10, activation="softmax")(x)
        super().__init__(inpt, x, {
            "optimizer":  optimizers.Adam(learning_rate=learning_rate),
            "loss": losses.categorical_crossentropy,
            "metrics": [metrics.categorical_accuracy],
        })
        Debug.log("DRModel", f"New model initialized, model name: {self.name}")
