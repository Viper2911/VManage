import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os

st.set_page_config(page_title="Hostel Matchmaker", layout="centered")

@st.cache_data
def load_data():
    file_path = 'hostel_students.csv'
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error("hostel_students.csv not found. Please run your data generation script first.")
        return None

df = load_data()

def get_best_matches(target_student_id, dataframe):
    target_student = dataframe[dataframe['student_id'] == target_student_id].iloc[0]
    target_bed_type = target_student['bed_preference']
    target_ac_type = target_student['ac_preference']
    
    filtered_df = dataframe[
        (dataframe['bed_preference'] == target_bed_type) & 
        (dataframe['ac_preference'] == target_ac_type) & 
        (dataframe['student_id'] != target_student_id)
    ].copy()

    if filtered_df.empty:
        return None

    features = ['sleep_schedule', 'cleanliness', 'social_battery', 'study_env']
    target_vector = target_student[features].values.reshape(1, -1)
    comparison_vectors = filtered_df[features].values

    similarities = cosine_similarity(target_vector, comparison_vectors)[0]
    
    filtered_df['match_score'] = (similarities * 100).round(1)
    best_matches = filtered_df.sort_values(by='match_score', ascending=False)
    
    return best_matches

if df is not None:
    st.title("Smart Hostel Roommate Finder")
    st.write("Find your perfect roommate based on lifestyle compatibility.")

    st.markdown("---")

    student_ids = df['student_id'].tolist()
    selected_id = st.selectbox("Select your Student ID to log in:", student_ids)

    if st.button("Find My Roommates", type="primary"):
        target_student = df[df['student_id'] == selected_id].iloc[0]
        full_name = f"{target_student['first_name']} {target_student['last_name']}"
        ac_text = "AC" if target_student['ac_preference'] == 1 else "Non-AC"
        
        st.success(f"Logged in as {full_name}")
        st.info(f"Your Requirements: {target_student['bed_preference']}-Bed Room, {ac_text}")
        
        st.subheader("Your Top Matches")
        
        with st.spinner('Calculating compatibility...'):
            matches = get_best_matches(selected_id, df)
            
            if matches is None:
                st.warning("No matches found for your exact room requirements.")
            else:
                display_df = matches[['first_name', 'last_name', 'match_score', 'sleep_schedule', 'cleanliness', 'social_battery', 'study_env']].head(10)
                
                st.dataframe(
                    display_df,
                    column_config={
                        "first_name": "First Name",
                        "last_name": "Last Name",
                        "match_score": st.column_config.ProgressColumn(
                            "Match %",
                            format="%f%%",
                            min_value=0,
                            max_value=100,
                        ),
                        "sleep_schedule": "Sleep",
                        "cleanliness": "Clean",
                        "social_battery": "Social",
                        "study_env": "Study"
                    },
                    hide_index=True,
                    use_container_width=True
                )