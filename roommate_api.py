from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(title="Roommate Matcher API")

class StudentProfile(BaseModel):
    student_id: str
    first_name: str
    last_name: str
    sleep_schedule: float  
    cleanliness: float     
    social_battery: float  
    study_env: float

class RoommateRequest(BaseModel):
    target_student: StudentProfile
    student_pool: List[StudentProfile]

@app.post("/calculate-roommates")
async def calculate_roommates(req: RoommateRequest):
    if not req.student_pool:
        return {"status": "success", "matches": [], "message": "No potential roommates in the pool."}

    target_df = pd.DataFrame([req.target_student.model_dump()])
    pool_df = pd.DataFrame([s.model_dump() for s in req.student_pool])
    features = ['sleep_schedule', 'cleanliness', 'social_battery', 'study_env']
    target_vector = target_df[features].values
    pool_vectors = pool_df[features].values

    similarities = cosine_similarity(target_vector, pool_vectors)[0]
    
    pool_df['match_score'] = (similarities * 100).round(1)
    
    top_5 = pool_df.sort_values(by='match_score', ascending=False).head(5)

    return {
        "status": "success",
        "matches": top_5[['student_id', 'first_name', 'last_name', 'match_score']].to_dict(orient='records')
    }