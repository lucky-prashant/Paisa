
from flask import Blueprint, render_template, request
from app.config import PAIRS, LOG_FILE
from app.data_handler import update_and_prepare
from app.model_handler import predict
import pandas as pd
from datetime import datetime
import os

routes = Blueprint('routes', __name__)

@routes.route('/', methods=['GET', 'POST'])
def index():
    predictions = []
    if request.method == 'POST':
        for pair in PAIRS:
            try:
                latest = update_and_prepare(pair)
                if latest is None:
                    predictions.append((pair, "No new data"))
                    continue
                result = predict(latest)
                direction = "CALL (⬆️)" if result == 1 else "PUT (⬇️)"
                predictions.append((pair, direction))
                log_prediction(pair, direction)
            except Exception as e:
                predictions.append((pair, f"Error: {str(e)}"))
    return render_template("index.html", predictions=predictions)

def log_prediction(pair, result):
    time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    log_df = pd.DataFrame([[time, pair, result]], columns=["timestamp", "pair", "prediction"])
    log_df.to_csv(LOG_FILE, mode='a', index=False, header=not os.path.exists(LOG_FILE))
