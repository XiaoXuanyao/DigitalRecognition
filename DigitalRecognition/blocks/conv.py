from keras import activations
from keras import layers
from keras import models
import tensorflow as tf


class Conv2D(models.Model):

    def __init__(self, c, k=3, s=1, p='same', act='gelu'):
        super().__init__()
        self.c, self.k, self.s, self.p = c, k, s, p
        self.conv = layers.Conv2D(c, k, s, p, data_format="channels_first")
        self.bn = layers.BatchNormalization(axis=1)
        self.act = layers.Activation(act)
    
    def call(self, x, training=None, mask=None):
        x = self.conv(x, training=training)
        x = self.bn(x, training=training)
        return self.act(x)

    def get_config(self):
        config = super(Conv2D, self).get_config()
        config.update({
            'c': self.c,
            'k': self.k,
            's': self.s,
            'p': self.p
        })
        return config


class DSConv2D(models.Model):

    def __init__(self, c, k=3, s=1, p='same'):
        super().__init__()
        self.c, self.k, self.s, self.p, self.g = c, k, s, p
        self.conv1 = Conv2D(c, k, s, p)
        self.conv2 = Conv2D(c, 1, 1, p)

    def call(self, x, training=None, mask=None):
        x = self.conv1(x, training=training)
        x = self.conv2(x, training=training)
        return x

    def get_config(self):
        config = super(DSConv2D, self).get_config()
        config.update({
            'c': self.c,
            'k': self.k,
            's': self.s,
            'p': self.p
        })
        return config


class BottleNeck(models.Model):

    def __init__(self, c, k=3, s=1, p='same'):
        super().__init__()
        self.c, self.k, self.s, self.p = c, k, s, p
        self.conv1 = Conv2D(c, 1, 1, p)
        self.conv2 = Conv2D(c, k, s, p)
        self.conv3 = Conv2D(c, 1, 1, p)
        self.conv4 = Conv2D(c, 3, s, p)

    def call(self, x, training=None, mask=None):
        x1 = self.conv1(x, training=training)
        x1 = self.conv2(x1, training=training)
        x1 = self.conv3(x1, training=training)
        x2 = self.conv4(x, training=training)
        return (x1 + x2) / 2

    def get_config(self):
        config = super(BottleNeck, self).get_config()
        config.update({
            'c': self.c,
            'k': self.k,
            's': self.s,
            'p': self.p
        })
        return config