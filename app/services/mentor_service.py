import json
import anthropic
from app.config import OPENAI_API_KEY
from app.services.embedding_service import EmbeddingService


class MentorService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=OPENAI_API_KEY)
        self.embedding_service = EmbeddingService()

    def generate_hint(self, failure_type: str, failure_analysis: str, problem_title: str, problem_tags: str) -> str:
        prompt = f"""You are a competitive programming mentor. A student failed the problem "{problem_title}" (tags: {problem_tags}).

Failure type: {failure_type}
Analysis: {failure_analysis}

Generate a SHORT, NON-SPOILER mentor hint (max 2-3 sentences). Do NOT give code or solutions. Point them toward the right approach or concept to review.

Respond ONLY with valid JSON:
{{"hint": "your hint here"}}"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            result = json.loads(response.content[0].text)
            hint = result.get("hint", "")
            return hint[:300]
        except Exception:
            return "Review the problem requirements carefully and trace through a simple example step-by-step."

    def recommend_problems(self, failure_analysis: str, current_problem, is_accepted: bool, db, user_id: int) -> tuple:
        from app.models import Problem, PersonalizedDifficultyPrediction

        # Get all unsolved problems (those with predictions for this user)
        all_predictions = db.query(PersonalizedDifficultyPrediction).filter(
            PersonalizedDifficultyPrediction.user_id == user_id
        ).all()

        unsolved_problems = [p.problem for p in all_predictions]

        # Exclude current problem
        unsolved_problems = [p for p in unsolved_problems if p.id != current_problem.id]

        if not unsolved_problems:
            return ([], "No other unsolved problems available.")

        # Find 3 problems user is most likely to pass (sorted by pass_probability DESC)
        predictions_dict = {p.problem_id: p.pass_probability for p in all_predictions}

        recommended = sorted(
            unsolved_problems,
            key=lambda p: predictions_dict.get(p.id, 0),
            reverse=True
        )[:3]

        problem_titles = ", ".join([p.title for p in recommended])
        explanation = self._generate_recommendation_explanation(
            is_accepted,
            current_problem.title,
            problem_titles,
            current_problem.tags
        )

        return (recommended, explanation)

    def _generate_recommendation_explanation(self, is_accepted: bool, current_title: str, rec_titles: str,
                                             current_tags: str) -> str:
        context = "solved" if is_accepted else "struggled with"

        prompt = f"""You are a competitive programming mentor. A student {context} "{current_title}" (tags: {current_tags}).

Recommend these problems as next steps: {rec_titles}

Generate a brief explanation (EXACTLY 1 sentence, max 20 words) of WHY these problems help them improve. Focus on skills/concepts.

Respond ONLY with valid JSON:
{{"explanation": "your one sentence explanation"}}"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            result = json.loads(response.content[0].text)
            return result.get("explanation", "")[:150]
        except Exception:
            return "These problems help you strengthen relevant skills."