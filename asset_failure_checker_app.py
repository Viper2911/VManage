import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Hostel Asset Health Check", layout="centered")

@st.cache_resource
def load_model():
    try:
        model = joblib.load('hostel_maintenance_model.pkl')
        model_columns = ['age_months', 'days_since_service', 'floor_level', 'usage_load', 
                         'asset_type_Geyser', 'asset_type_Water Cooler']
        return model, model_columns
    except:
        st.error("Model not found.")
        return None, None

model, model_columns = load_model()

st.title("Warden's Maintenance Watchdog")

if model is not None:
    with st.form("maintenance_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            asset_type = st.selectbox("Asset Type", ["AC", "Geyser", "Water Cooler"])
            age_months = st.slider("Age (Months)", 1, 84, 24)
            floor_level = st.slider("Floor", 1, 16, 1)

        with col2:
            days_since_service = st.number_input("Days Since Service", 0, 365, 30)
        
        submit = st.form_submit_button("Check Health", type="primary")

    if submit:
        usage_load = 108 if asset_type == "AC" else 5
        
        input_data = pd.DataFrame([{
            "age_months": age_months,
            "days_since_service": days_since_service,
            "floor_level": floor_level,
            "usage_load": usage_load,
            "asset_type_Geyser": 1 if asset_type == "Geyser" else 0,
            "asset_type_Water Cooler": 1 if asset_type == "Water Cooler" else 0
        }])

        input_data = input_data.reindex(columns=model_columns, fill_value=0)

        prob = model.predict_proba(input_data)[0][1]
        prob_pct = round(prob * 100, 2)

        st.markdown("---")
        
        if prob > 0.75:
            st.error(f"CRITICAL: {prob_pct}% Risk")
            st.warning("Action Required.")
        elif prob > 0.40:
            st.warning(f"MODERATE: {prob_pct}% Risk")
        else:
            st.success(f"STABLE: {prob_pct}% Risk")

        st.progress(prob)