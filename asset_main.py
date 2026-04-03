from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI(title="Predictive Maintenance API")

try:
    model = joblib.load('hostel_maintenance_model.pkl')
    model_columns = ['age_months', 'days_since_service', 'floor_level', 'usage_load', 'asset_type_Geyser', 'asset_type_Water Cooler']
    print("Maintenance Model Loaded!")
except Exception as e:
    print(f" Error: Model file not found. Run your training script first. {e}")

class MaintenanceInput(BaseModel):
    asset_id: str
    asset_type: str
    age_months: int
    days_since_service: int
    floor_level: int

@app.post("/predict-failure")
async def predict_maintenance(data: MaintenanceInput):
    usage_load=108 if data.asset_type=="AC" else 5
    is_geyser=1 if data.asset_type=="Geyser" else 0
    is_cooler=1 if data.asset_type=="Water Cooler" else 0

    input_df = pd.DataFrame([{
        "age_months": data.age_months,
        "days_since_service": data.days_since_service,
        "floor_level": data.floor_level,
        "usage_load": usage_load,
        "asset_type_Geyser": is_geyser,
        "asset_type_Water Cooler": is_cooler
    }])

    input_df=input_df.reindex(columns=model_columns,fill_value=0)

    prob=model.predict_proba(input_df)[0][1]
    prob_percentage=round(float(prob)*100,2)

    alert_required=True if prob>0.75 else False

    return{
        "asset_type": data.asset_type,
        "probability_score": prob_percentage,
        "alert_required": alert_required
    }