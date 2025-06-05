from fastapi import FastAPI
import joblib
import pandas as pd
from pydantic import BaseModel
import mlflow
import os 
from dotenv import load_dotenv
import prophet



class ProphetOccupationRequest(BaseModel):
    """
    Request model for Prophet consultation.
    """
    start_date: str
    end_date: str    
    cap : float = 1.0  # Optional, default to 1.0
    floor : float = 0.0  # Optional, default to 0.0

# Load environment variables from .env file

# MLFLOW_URI should be set in the .env file that is in the root of the project
load_dotenv()
MLFLOW_URI=os.getenv("MLFLOW_TRACKING_URI")


app = FastAPI()

# On windows, you may need to use the localhost instead of 127.0.0.1
mlflow.set_tracking_uri(str(MLFLOW_URI))



@app.post("/predict/{model_name}")
def predict(data: ProphetOccupationRequest, model_name:str):
    model = mlflow.pyfunc.load_model(f"models:/{model_name}/2") 
    # model = joblib.load("../models/prophet_model.pkl")

    start_date = pd.to_datetime(data.start_date)
    end_date = pd.to_datetime(data.end_date)
    
    
    future_dates = pd.date_range(start=start_date, end=end_date, freq='D')


    df = pd.DataFrame({
        'ds': future_dates,
        'cap': [data.cap] * len(future_dates),  # Assuming cap is a constant for all dates
        'floor': [data.floor] * len(future_dates)  # Assuming floor is a constant for all dates
    })
    
    forecast = model.predict(df)
    result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    return (result.to_dict(orient='records'))




