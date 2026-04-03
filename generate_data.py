import pandas as pd
import numpy as np
import random

num_students=500

archetypes={
    "The Quiet Coder": {"mean": [4.5,3.0,1.5,1.5], "std": 0.5},
    "The Social Butterfly": {"mean": [2.5,2.0,4.5,4.0], "std": 0.6},
    "The Disciplined Topper": {"mean": [1.5,4.5,2.0,1.0], "std": 0.4},
    "The Chill All- Rounder": {"mean": [3.0,3.0,3.0,3.0], "std": 0.7}
}

first_names=["Aadil","Gaurav","Aditya","Dharani","Rahul","Pranay","Sudharshan","Karan","Aryan","Rohan"]
last_names=["Hasan","Singh","Jha","Patel","Verma","Kumar","Gupta","Rao","Das","Sharma"]

bed_options=[2,3,4,6]
ac_options=[1,0]
data=[]

for i in range(num_students):
    archetype_name=random.choice(list(archetypes.keys()))
    params=archetypes[archetype_name]

    scores=np.clip(np.random.normal(params["mean"],params["std"]),1,5).round(1)

    student={
        "student_id": f"STU_{1000+i}",
        "first_name": random.choice(first_names),
        "last_name": random.choice(last_names),
        "bed_preference": random.choice(bed_options),
        "ac_preference": random.choice(ac_options),
        "sleep_schedule": scores[0],
        "cleanliness": scores[1],
        "social_battery": scores[2],
        "study_env": scores[3]
    }
    data.append(student)

df=pd.DataFrame(data)
df.to_csv('hostel_students.csv',index=False)