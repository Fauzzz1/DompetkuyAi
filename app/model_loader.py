import joblib
import tensorflow as tf
from tensorflow.keras import layers


class FinancialLayer(layers.Layer):
    def __init__(self, units=32, **kwargs):
        super().__init__(**kwargs)
        self.units = units
        self.dense = layers.Dense(units, activation="relu")

    def call(self, inputs):
        return self.dense(inputs)

    def get_config(self):
        config = super().get_config()
        config.update({"units": self.units})
        return config


model = tf.keras.models.load_model(
    "models/dompetkuy_financial_status.keras",
    custom_objects={"FinancialLayer": FinancialLayer},
    compile=False
)

scaler = joblib.load("models/scaler.pkl")
feature_cols = joblib.load("models/feature_cols.pkl")