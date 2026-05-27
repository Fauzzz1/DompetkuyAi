import joblib
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.utils import register_keras_serializable

@register_keras_serializable(package="Custom")
class FinancialLayer(layers.Layer):
    def __init__(self, units=32, **kwargs):
        super().__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.dense = layers.Dense(self.units, activation="relu")
        self.dense.build(input_shape)
        super().build(input_shape)

    def call(self, inputs):
        return self.dense(inputs)

    def get_config(self):
        config = super().get_config()
        config.update({"units": self.units})
        return config

model = tf.keras.models.load_model(
    "models/dompetkuy_model.keras",
    custom_objects={"FinancialLayer": FinancialLayer},
    compile=False
)

scaler = joblib.load("models/scaler.pkl")
feature_cols = joblib.load("models/feature_cols.pkl")