import numpy as np
import pickle
from typing import Tuple


class SyntheticDataGenerator:
    @staticmethod
    def generate_training_data(n_users: int = 100, n_problems: int = 50, n_submissions: int = 2000) -> Tuple:
        np.random.seed(42)

        n_tags = 6
        n_user_features = 8  # 6 tags + avg_time + avg_edits
        n_context_features = 0  # NOT used in batch prediction
        n_problem_features = 7  # 6 tags + difficulty

        X_difficulty = []
        y_difficulty = []
        X_hint_timing = []
        y_hint_timing = []

        for _ in range(n_submissions):
            user_success_per_tag = np.random.uniform(0.3, 0.9, n_tags)
            user_avg_time = np.random.uniform(30, 300)
            user_avg_edits = np.random.uniform(2, 10)

            user_features = np.concatenate([user_success_per_tag, [user_avg_time, user_avg_edits]])

            problem_tags = np.random.binomial(1, 0.4, n_tags)
            problem_difficulty = np.random.choice([0, 1, 2])

            problem_features = np.concatenate([problem_tags, [problem_difficulty]])

            time_spent = np.random.uniform(10, 600)
            edits = np.random.poisson(5)

            # For difficulty model: combine problem + user features only
            X_diff = np.concatenate([problem_features, user_features])
            X_difficulty.append(X_diff)

            user_skill = np.mean(user_success_per_tag)
            problem_hardness = problem_difficulty / 2.0

            pass_prob = user_skill * (1 - 0.3 * problem_hardness)
            pass_prob += np.random.normal(0, 0.1)
            pass_prob = np.clip(pass_prob, 0, 1)

            y_diff = 1 if pass_prob > 0.5 else 0
            y_difficulty.append(y_diff)

            # For hint timing: context features only
            X_hint = np.array([time_spent, edits])
            X_hint_timing.append(X_hint)

            hint_needed = 1 if (time_spent > 200 and edits < 5) else 0
            y_hint_timing.append(hint_needed)

        X_difficulty = np.array(X_difficulty)
        y_difficulty = np.array(y_difficulty)
        X_hint_timing = np.array(X_hint_timing)
        y_hint_timing = np.array(y_hint_timing)

        return X_difficulty, y_difficulty, X_hint_timing, y_hint_timing

    @staticmethod
    def save_synthetic_data(path: str, data: Tuple):
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def load_synthetic_data(path: str) -> Tuple:
        with open(path, 'rb') as f:
            return pickle.load(f)