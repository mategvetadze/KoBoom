from sqlalchemy import Column, Integer, String, Text, LargeBinary, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(String)

    submissions = relationship("Submission", back_populates="user")
    user_profiles = relationship("UserProfile", back_populates="user", uselist=False)
    predictions = relationship("PersonalizedDifficultyPrediction", back_populates="user")


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    difficulty = Column(String)
    tags = Column(String)
    description = Column(Text, nullable=True)
    embedding = Column(LargeBinary)
    correct_solution = Column(Text, nullable=True)

    tests = relationship("ProblemTest", back_populates="problem")
    submissions = relationship("Submission", back_populates="problem")
    predictions = relationship("PersonalizedDifficultyPrediction", back_populates="problem")


class ProblemTest(Base):
    __tablename__ = "problem_tests"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"))
    input_data = Column(Text)
    expected_output = Column(Text)

    problem = relationship("Problem", back_populates="tests")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_id = Column(Integer, ForeignKey("problems.id"))
    code = Column(Text)
    status = Column(String)
    failure_analysis = Column(Text, nullable=True)
    hint_given = Column(Integer, default=0)
    time_spent_seconds = Column(Integer)
    created_at = Column(String)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    total_solved = Column(Integer, default=0)
    total_attempts = Column(Integer, default=0)
    avg_time_per_solve = Column(Float, default=0.0)
    avg_edits = Column(Float, default=0.0)
    updated_at = Column(String)

    user = relationship("User", back_populates="user_profiles")


class PersonalizedDifficultyPrediction(Base):
    __tablename__ = "personalized_difficulty_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), index=True)
    pass_probability = Column(Float)  # 0.0 to 1.0 (probability of PASSING, not failing)
    created_at = Column(String)
    updated_at = Column(String)

    user = relationship("User", back_populates="predictions")
    problem = relationship("Problem", back_populates="predictions")