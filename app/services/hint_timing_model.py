import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
import numpy as np
import pickle


class HintTimingModel:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.model = None

    def build_model(self, input_dim: int):
        self.model = keras.Sequential([
            keras.layers.Dense(32, activation='relu', input_dim=input_dim),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])

        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )

    def train(self, X_train: np.ndarray, y_train: np.ndarray, epochs: int = 50, batch_size: int = 32):
        X_scaled = self.scaler.fit_transform(X_train)

        history = self.model.fit(
            X_scaled, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )

        return history

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.model is None:
            self.load()

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled, verbose=0)

    def save(self):
        self.model.save(self.model_path)
        scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

    def load(self):
        self.model = keras.models.load_model(self.model_path)
        scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
