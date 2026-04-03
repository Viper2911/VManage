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
async def calculate_roommates(req: RoommateRequest)