import click
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Problem, User, UserProfile, PersonalizedDifficultyPrediction
from app.services.embedding_service import EmbeddingService
from app.services.data_generator import SyntheticDataGenerator
from app.services.personalized_difficulty_model import PersonalizedDifficultyModel
from app.services.hint_timing_model import HintTimingModel
from app.config import DIFFICULTY_MODEL_PATH, HINT_TIMING_MODEL_PATH, SYNTHETIC_DATA_PATH
from datetime import datetime
import os


@click.group()
def cli():
    """CP Mentor CLI"""
    pass


@cli.command()
def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)
    click.echo("✓ Database initialized")


@cli.command()
def embed_problems():
    """Compute embeddings for all problems"""
    db = SessionLocal()

    click.echo("Loading embedding model...")
    emb_service = EmbeddingService()

    problems = db.query(Problem).all()

    for i, problem in enumerate(problems, 1):
        text = f"{problem.title} {problem.tags} {problem.description or ''}"
        embedding = emb_service.embed_text(text)
        embedding_blob = emb_service.serialize_embedding(embedding)

        problem.embedding = embedding_blob
        db.add(problem)
        db.commit()

        click.echo(f"  ✓ Embedded ({i}/{len(problems)}): {problem.title}")

    db.close()
    click.echo("✓ All problems embedded!")


@cli.command()
@click.option('--n-users', default=100, help='Number of synthetic users')
@click.option('--n-problems', default=50, help='Number of problems')
@click.option('--n-submissions', default=2000, help='Number of submissions to generate')
def generate_data(n_users, n_problems, n_submissions):
    """Generate synthetic training data"""
    click.echo(f"Generating synthetic data ({n_submissions} submissions)...")

    generator = SyntheticDataGenerator()
    data = generator.generate_training_data(
        n_users=n_users,
        n_problems=n_problems,
        n_submissions=n_submissions
    )

    os.makedirs(os.path.dirname(SYNTHETIC_DATA_PATH), exist_ok=True)
    generator.save_synthetic_data(SYNTHETIC_DATA_PATH, data)

    click.echo(f"✓ Synthetic data saved to {SYNTHETIC_DATA_PATH}")


@cli.command()
def train_models():
    """Train ML models (difficulty & hint timing)"""
    click.echo("Loading synthetic data...")

    generator = SyntheticDataGenerator()
    if not os.path.exists(SYNTHETIC_DATA_PATH):
        click.echo("Synthetic data not found. Generating...")
        data = generator.generate_training_data()
        generator.save_synthetic_data(SYNTHETIC_DATA_PATH, data)
    else:
        data = generator.load_synthetic_data(SYNTHETIC_DATA_PATH)

    X_difficulty, y_difficulty, X_hint_timing, y_hint_timing = data

    click.echo("\n📊 Training Personalized Difficulty Model...")
    difficulty_model = PersonalizedDifficultyModel(DIFFICULTY_MODEL_PATH)
    difficulty_model.build_model(input_dim=X_difficulty.shape[1])

    history = difficulty_model.train(X_difficulty, y_difficulty, epochs=50, batch_size=32)
    difficulty_model.save()
    click.echo(f"✓ Difficulty model trained and saved to {DIFFICULTY_MODEL_PATH}")

    click.echo("\n⏰ Training Hint Timing Model...")
    hint_timing_model = HintTimingModel(HINT_TIMING_MODEL_PATH)
    hint_timing_model.build_model(input_dim=X_hint_timing.shape[1])

    history = hint_timing_model.train(X_hint_timing, y_hint_timing, epochs=50, batch_size=32)
    hint_timing_model.save()
    click.echo(f"✓ Hint timing model trained and saved to {HINT_TIMING_MODEL_PATH}")

    click.echo("\n✅ All models trained successfully!")


@cli.command()
@click.option('--user-id', default=1, help='User ID')
def init_user_predictions(user_id):
    """Initialize predictions for a user (compute for all problems)"""
    from app.routes import _recompute_all_predictions

    db = SessionLocal()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        click.echo(f"✗ User {user_id} not found")
        return

    # Create user profile if doesn't exist
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id, updated_at=datetime.now().isoformat())
        db.add(profile)
        db.commit()

    click.echo(f"Computing predictions for user {user_id}...")
    _recompute_all_predictions(user_id, db)

    db.close()
    click.echo("✓ Predictions initialized!")


@cli.command()
def seed_problems():
    """Add sample problems to database"""
    db = SessionLocal()

    from app.models import Problem, ProblemTest

    # Check if problems already exist
    existing = db.query(Problem).count()
    if existing > 0:
        click.echo(f"✓ Database already has {existing} problems")
        return

    problems_data = [
        {
            "title": "Two Sum",
            "difficulty": "easy",
            "tags": "array,hash",
            "description": "Find two numbers that add up to target",
            "tests": [
                {"input": "1 2 3 4 5\n7", "expected_output": "2 5"},
                {"input": "1 2 3\n5", "expected_output": "2 3"},
            ]
        },
        {
            "title": "Reverse String",
            "difficulty": "easy",
            "tags": "string",
            "description": "Reverse a given string",
            "tests": [
                {"input": "hello", "expected_output": "olleh"},
                {"input": "world", "expected_output": "dlrow"},
            ]
        },
    ]

    for p_data in problems_data:
        problem = Problem(
            title=p_data["title"],
            difficulty=p_data["difficulty"],
            tags=p_data["tags"],
            description=p_data["description"],
            embedding=b''
        )
        db.add(problem)
        db.flush()

        for test_data in p_data["tests"]:
            test = ProblemTest(
                problem_id=problem.id,
                input_data=test_data["input"],
                expected_output=test_data["expected_output"]
            )
            db.add(test)

        click.echo(f"  ✓ Added: {p_data['title']}")

    db.commit()
    db.close()
    click.echo("✓ Sample problems added!")



if __name__ == "__main__":
    cli()