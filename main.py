from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from data import WORKOUTS_DB
import uvicorn

app = FastAPI(
    title="Workout API",
    description="RESTful API providing access to structured home, gym, cardio, and mobility workouts.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allows requests from any origin (e.g., localhost, Webflow, Vercel, Flutter Web)
    allow_credentials=True,
    allow_methods=["*"],        # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],        # Allows all HTTP headers
)

class WorkoutItem(BaseModel):
    id: int
    name: str
    category: str
    sub_category: str
    muscle_group: str
    secondary_muscles: List[str]
    equipment: str
    equipment_required: bool
    difficulty: str
    exercise_type: str
    movement_type: str
    is_compound: bool
    instructions: str
    recommended_sets: int
    recommended_reps: str

class WorkoutCreate(BaseModel):
    name: str
    category: str
    sub_category: str
    muscle_group: str
    secondary_muscles: List[str] = []
    equipment: str
    equipment_required: bool = False
    difficulty: str
    exercise_type: str
    movement_type: str
    is_compound: bool = True
    instructions: str
    recommended_sets: int
    recommended_reps: str

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Workout API is up and running!",
        "total_workouts": len(WORKOUTS_DB)
    }

@app.get("/api/v1/workouts", response_model=List[WorkoutItem])
def get_workouts(
    category: Optional[str] = Query(None, description="Filter by category (e.g. home, gym, cardio, mobility)"),
    sub_category: Optional[str] = Query(None, description="Filter by sub_category (e.g. no_equipment, dumbbell, barbell, cable)"),
    muscle_group: Optional[str] = Query(None, description="Filter by primary muscle (e.g. chest, quadriceps, glutes, back)"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level (beginner, intermediate, advanced)"),
    movement_type: Optional[str] = Query(None, description="Filter by movement (push, pull, squat, hinge, lunge)"),
    equipment_required: Optional[bool] = Query(None, description="Filter by whether equipment is required (true/false)"),
    is_compound: Optional[bool] = Query(None, description="Filter by compound vs isolation exercise (true/false)")
):
    results = WORKOUTS_DB

    if category:
        results = [w for w in results if w["category"].lower() == category.lower()]
    if sub_category:
        results = [w for w in results if w["sub_category"].lower() == sub_category.lower()]
    if muscle_group:
        results = [w for w in results if w["muscle_group"].lower() == muscle_group.lower()]
    if difficulty:
        results = [w for w in results if w["difficulty"].lower() == difficulty.lower()]
    if movement_type:
        results = [w for w in results if w["movement_type"].lower() == movement_type.lower()]
    if equipment_required is not None:
        results = [w for w in results if w["equipment_required"] == equipment_required]
    if is_compound is not None:
        results = [w for w in results if w["is_compound"] == is_compound]

    return results

@app.get("/api/v1/workouts/{workout_id}", response_model=WorkoutItem)
def get_workout_by_id(workout_id: int):
    workout = next((w for w in WORKOUTS_DB if w["id"] == workout_id), None)
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

@app.get("/api/v1/meta/categories")
def get_categories():
    categories = sorted(list({w["category"] for w in WORKOUTS_DB}))
    sub_categories = sorted(list({w["sub_category"] for w in WORKOUTS_DB}))
    return {
        "categories": categories,
        "sub_categories": sub_categories
    }

@app.get("/api/v1/meta/muscles")
def get_muscles():
    primary_muscles = sorted(list({w["muscle_group"] for w in WORKOUTS_DB}))
    return {"muscle_groups": primary_muscles}

@app.post("/api/v1/workouts", response_model=WorkoutItem, status_code=201)
def create_workout(workout: WorkoutCreate):
    new_id = max([w["id"] for w in WORKOUTS_DB], default=0) + 1
    new_item = {"id": new_id, **workout.model_dump()}
    WORKOUTS_DB.append(new_item)
    return new_item

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)