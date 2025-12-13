from pydantic import BaseModel
from typing import List


class ProblemRecommendation(BaseModel):
    id: int
    title: str
    difficulty: str
    tags: str


class ProblemWithProbability(BaseModel):
    id: int
    title: str
    difficulty: str
    tags: str
    pass_probability: float


class SubmissionRequest(BaseModel):
    user_id: int
    problem_id: int
    code: str
    time_spent_seconds: int = 0


class SubmissionResponse(BaseModel):
    success: bool
    status: str
    hint: str
    hint_given: bool
    pass_probability_on_this: float
    recommendations: List[ProblemRecommendation]
    explanation: str


class UserDifficultyPredictionsResponse(BaseModel):
    user_id: int
    problems: List[ProblemWithProbability]  # sorted by pass_probability (easiest first)
