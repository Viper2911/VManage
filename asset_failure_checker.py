import pandas as pd
import numpy as np
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

print("Generating Full Hostel Infrastructure Dataset")
data = []
asset_types = ["AC", "Geyser", "Water Cooler"]
ac_working_hrs=108

for _ in range(2000):
    asset=random.choice(asset_types)
    age_months=random.randint(1,84)
    days_since_service=random.randint(1,365)
    floor_level=random.randint(1,16)

    if asset=="AC":
        usage_load=ac_working_hrs
        thermal_multiplier=1+(floor_level/20)
        risk_score=(age_months*0.4)+(days_since_service*0.2)+(usage_load*0.1*thermal_multiplier)

    elif asset=="Geyser":
        usage_load=random.randint(1,10)
        risk_score=(age_months*0.3)+(days_since_service*0.3)+(usage_load*5)

    elif asset=="Water Cooler":
        usage_load=random.randint(1,10)
        risk_score=(age_months*0.25)+(days_since_service*0.4)+(usage_load*4)

    will_fail = 1 if (risk_score + random.randint(-10, 10)) > 90 else 0

    data.append({
        "asset_type": asset,
        "age_months": age_months,
        "days_since_service": days_since_service,
        "floor_level": floor_level,
        "usage_load": usage_load,
        "will_fail": will_fail  
    })

df=pd.DataFrame(data)
df=pd.get_dummies(df,columns=['asset_type'],drop_first=True)

X=df.drop('will_fail',axis=1)
y=df['will_fail']

X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)

model=RandomForestClassifier(n_estimators=1000,random_state=42)
model.fit(X,y)
y_pred=model.predict(X_test)

accuracy=accuracy_score(y_test,y_pred)

print("Model Performance Report")
print(f"Overall Accuracy Score: {accuracy * 100:.2f}%")
print("\nDetailed Breakdown:")
print(classification_report(y_test, y_pred, target_names=['Stable (0)', 'Failing (1)']))
