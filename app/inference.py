import numpy as np

from app.model_loader import model, scaler, feature_cols


status_map = {
    0: "good",
    1: "tip",
    2: "warning",
    3: "alert"
}


def predict_model(features):
    for col in feature_cols:
        if col not in features.columns:
            features[col] = 0

    X = features[feature_cols]
    X_scaled = scaler.transform(X)

    pred = model.predict(X_scaled, verbose=0)

    label = int(np.argmax(pred, axis=1)[0])
    confidence = float(np.max(pred))

    return status_map[label], confidence