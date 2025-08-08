
import joblib
from app.config import MODEL_PATH

model = joblib.load(MODEL_PATH)

def predict(features_df):
    features = features_df[["open", "high", "low", "close", "volume", "EMA20", "RSI"]]
    return model.predict(features)[0]
