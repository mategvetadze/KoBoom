from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import User, Problem, Submission, UserProfile, PersonalizedDifficultyPrediction
from app.schemas import SubmissionRequest, SubmissionResponse, ProblemRecommendation, UserDifficultyPredictionsResponse, \
    ProblemWithProbability
from app.services.code_executor import CodeExecutor
from app.services.solution_analyzer import SolutionAnalyzer
from app.services.mentor_service import MentorService
from app.services.personalized_difficulty_model import PersonalizedDifficultyModel
from app.services.hint_timing_model import HintTimingModel
from app.config import DIFFICULTY_MODEL_PATH, HINT_TIMING_MODEL_PATH
import numpy as np

router = APIRouter()


def _create_difficulty_features(user_profile, problem) -> np.ndarray:
    """Create feature vector for difficulty model (problem + user features only)."""
    # Problem features: 6 tags (one-hot) + 1 difficulty = 7
    tags_list = [t.strip() for t in problem.tags.split(',')]
    all_tags = ['array', 'dp', 'graph', 'greedy', 'string', 'math']
    problem_tags = np.array([1.0 if tag in tags_list else 0.0 for tag in all_tags])

    difficulty_map = {'easy': 0, 'medium': 1, 'hard': 2}
    problem_difficulty = np.array([difficulty_map.get(problem.difficulty, 0)])

    # User features: success per tag (6) + avg_time + avg_edits = 8
    user_success_per_tag = np.array([0.5] * 6)  # default
    user_avg_time = 100.0
    user_avg_edits = 3.0

    if user_profile:
        user_avg_time = user_profile.avg_time_per_solve if user_profile.avg_time_per_solve > 0 else 100.0
        user_avg_edits = user_profile.avg_edits if user_profile.avg_edits > 0 else 3.0

    user_features = np.concatenate([user_success_per_tag, [user_avg_time, user_avg_edits]])

    # Combine: 7 + 8 = 15 features
    features = np.concatenate([problem_tags, problem_difficulty, user_features])
    return features


def _recompute_all_predictions(user_id: int, db: Session):
    """Recompute pass probabilities for ALL problems for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return

    user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    all_problems = db.query(Problem).all()

    difficulty_model = PersonalizedDifficultyModel(DIFFICULTY_MODEL_PATH)

    for problem in all_problems:
        features = _create_difficulty_features(user_profile, problem)
        pass_prob = float(difficulty_model.predict(features.reshape(1, -1))[0][0])

        prediction = db.query(PersonalizedDifficultyPrediction).filter(
            PersonalizedDifficultyPrediction.user_id == user_id,
            PersonalizedDifficultyPrediction.problem_id == problem.id
        ).first()

        if not prediction:
            prediction = PersonalizedDifficultyPrediction(
                user_id=user_id,
                problem_id=problem.id,
                pass_probability=pass_prob,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            db.add(prediction)
        else:
            prediction.pass_probability = pass_prob
            prediction.updated_at = datetime.now().isoformat()
            db.add(prediction)

    db.commit()


@router.post("/api/mentor/submit/", response_model=SubmissionResponse)
def submit_solution(request: SubmissionRequest, db: Session = Depends(get_db)):
    """Submit code and get feedback."""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        problem = db.query(Problem).filter(Problem.id == request.problem_id).first()
        if not problem:
            raise HTTPException(status_code=400, detail="Problem not found")

        tests = [(t.input_data, t.expected_output) for t in problem.tests]

        executor = CodeExecutor()
        status, failure_analysis = executor.classify_failure(request.code, tests)

        submission = Submission(
            user_id=request.user_id,
            problem_id=request.problem_id,
            code=request.code,
            status=status,
            failure_analysis=failure_analysis,
            time_spent_seconds=request.time_spent_seconds,
            created_at=datetime.now().isoformat()
        )
        db.add(submission)
        db.commit()

        is_accepted = (status == "accepted")

        # Update user profile
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if not user_profile:
            user_profile = UserProfile(user_id=user.id, updated_at=datetime.now().isoformat())
            db.add(user_profile)

        user_profile.total_attempts += 1
        if is_accepted:
            user_profile.total_solved += 1
            if request.time_spent_seconds > 0:
                current_avg = user_profile.avg_time_per_solve * (user_profile.total_solved - 1)
                user_profile.avg_time_per_solve = (current_avg + request.time_spent_seconds) / user_profile.total_solved

        # Update avg_edits
        if not is_accepted:
            current_edits = user_profile.avg_edits * (user_profile.total_attempts - 1)
            user_profile.avg_edits = (current_edits + np.random.poisson(3)) / user_profile.total_attempts

        user_profile.updated_at = datetime.now().isoformat()
        db.add(user_profile)
        db.commit()

        # Recompute ALL predictions
        _recompute_all_predictions(user.id, db)

        # If accepted, delete the prediction row for this problem (they solved it)
        if is_accepted:
            db.query(PersonalizedDifficultyPrediction).filter(
                PersonalizedDifficultyPrediction.user_id == user.id,
                PersonalizedDifficultyPrediction.problem_id == problem.id
            ).delete()
            db.commit()

        # Get current pass probability on this problem (before deletion if accepted)
        if is_accepted:
            pass_prob_on_this = 1.0  # They passed it
        else:
            prediction = db.query(PersonalizedDifficultyPrediction).filter(
                PersonalizedDifficultyPrediction.user_id == user.id,
                PersonalizedDifficultyPrediction.problem_id == problem.id
            ).first()
            pass_prob_on_this = prediction.pass_probability if prediction else 0.5

        # Hint logic
        hint = ""
        hint_given = False

        if not is_accepted and status != "syntax":
            if problem.correct_solution:
                analyzer = SolutionAnalyzer()
                detailed_analysis = analyzer.analyze_mistake(request.code, problem.correct_solution, status)
                failure_for_embedding = detailed_analysis
            else:
                failure_for_embedding = failure_analysis

            # Predict if hint should be given
            hint_timing_model = HintTimingModel(HINT_TIMING_MODEL_PATH)
            hint_features = np.array([[float(request.time_spent_seconds), np.random.poisson(3)]])
            hint_prob = float(hint_timing_model.predict(hint_features)[0][0])

            if hint_prob > 0.5:
                mentor = MentorService()
                hint = mentor.generate_hint(
                    failure_type=status,
                    failure_analysis=failure_for_embedding,
                    problem_title=problem.title,
                    problem_tags=problem.tags
                )
                hint_given = True
                submission.hint_given = 1
                db.add(submission)
                db.commit()

        # Get recommendations (3 problems user is most likely to pass)
        mentor = MentorService()
        rec_problems, explanation = mentor.recommend_problems(
            failure_analysis=failure_analysis,
            current_problem=problem,
            is_accepted=is_accepted,
            db=db,
            user_id=user.id
        )

        rec_response = [
            ProblemRecommendation(
                id=p.id,
                title=p.title,
                difficulty=p.difficulty,
                tags=p.tags
            )
            for p in rec_problems
        ]

        return SubmissionResponse(
            success=True,
            status=status,
            hint=hint,
            hint_given=hint_given,
            pass_probability_on_this=pass_prob_on_this,
            recommendations=rec_response,
            explanation=explanation
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/user/{user_id}/difficulty-predictions", response_model=UserDifficultyPredictionsResponse)
def get_user_difficulty_predictions(user_id: int, db: Session = Depends(get_db)):
    """Get all problems with pass probabilities for a user, sorted by probability (easiest first)."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="User not found")

        predictions = db.query(PersonalizedDifficultyPrediction).filter(
            PersonalizedDifficultyPrediction.user_id == user_id
        ).all()

        if not predictions:
            raise HTTPException(status_code=400,
                                detail="No predictions found. Train models and submit solutions first.")

        # Sort by pass_probability descending (easiest first)
        problems_with_probs = [
            ProblemWithProbability(
                id=p.problem.id,
                title=p.problem.title,
                difficulty=p.problem.difficulty,
                tags=p.problem.tags,
                pass_probability=round(p.pass_probability, 3)
            )
            for p in sorted(predictions, key=lambda x: x.pass_probability, reverse=True)
        ]

        return UserDifficultyPredictionsResponse(
            user_id=user_id,
            problems=problems_with_probs
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
