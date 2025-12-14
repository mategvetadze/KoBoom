# KoBoom
KoBoom - AI-Powered Competitive Programming Mentor
An intelligent coding practice platform that provides personalized problem recommendations, real-time hints, and adaptive difficulty predictions using machine learning.
Features
🎯 Personalized Difficulty Prediction

ML model predicts your success probability on each problem
Adapts based on your submission history and performance
Problems ranked by difficulty (easiest first)

💡 Smart Hint System

Context-aware hints based on failure type
Timing model determines when hints are most helpful
Non-spoiler guidance that promotes learning

📊 Intelligent Recommendations

Semantic similarity matching using embeddings
Recommends problems that strengthen specific skills
Adapts to whether you solved or struggled with current problem

🔍 Code Analysis

Automatic test execution with multiple test cases
Detailed failure classification (syntax, runtime, TLE, wrong answer)
Solution comparison to identify logic gaps

🎨 Modern UI

Clean, responsive interface with dark/light themes
Real-time problem filtering and search
Interactive code editor with multiple language support
Visual verdict modals with actionable feedback

Tech Stack
Backend:

FastAPI (Python web framework)
SQLAlchemy (ORM)
TensorFlow/Keras (ML models)
Sentence Transformers (embeddings)
Anthropic Claude (hint generation)

Frontend:

Vanilla JavaScript
CSS with custom design system
No framework dependencies

Machine Learning:

Personalized difficulty prediction model
Hint timing optimization model
Problem embedding for similarity matching

Installation
Prerequisites

Python 3.8+
pip

Setup

Clone the repository

bashgit clone <repository-url>
cd cp-mentor

Install dependencies

bashpip install -r requirements.txt

Configure environment
Create a .env file:

envOPENAI_API_KEY=your_anthropic_api_key_here

Initialize database

bashpython -m app.cli init-db

Seed sample problems

bashpython -m app.cli seed-problems

Generate embeddings

bashpython -m app.cli embed-problems

Generate training data and train models

bashpython -m app.cli generate-data --n-users 100 --n-problems 50 --n-submissions 2000
python -m app.cli train-models

Initialize user predictions

bashpython -m app.cli init-user-predictions --user-id 1
Running the Application
Start the FastAPI server:
bashuvicorn app.main:app --reload
Visit http://localhost:8000 in your browser.
CLI Commands
CommandDescriptioninit-dbInitialize database schemaseed-problemsAdd sample problemsembed-problemsCompute embeddings for all problemsgenerate-dataGenerate synthetic training datatrain-modelsTrain ML models (difficulty & hint timing)init-user-predictionsCompute predictions for a user
API Endpoints
Problems

GET /api/problems - List all problems
GET /api/problems/{id} - Get problem details
GET /api/user/{id}/difficulty-predictions - Get personalized difficulty predictions

Submissions

POST /api/mentor/submit/ - Submit solution and get feedback

Architecture
Machine Learning Pipeline

Feature Engineering

Problem features: tags (one-hot), difficulty level
User features: success rate per tag, avg solve time, avg edits
Context features: time spent, number of edits


Difficulty Model

Input: Problem features + User features (15 dimensions)
Output: Pass probability (0-1)
Architecture: Dense layers with dropout


Hint Timing Model

Input: Time spent + Edit count (2 dimensions)
Output: Hint necessity probability (0-1)
Architecture: Dense layers with dropout



Recommendation System

Semantic Matching: Uses sentence transformers to find problems similar to failed areas
Difficulty Filtering: Prioritizes problems user is most likely to pass
Diversity: Ensures varied problem types and skills

Database Schema

users: User accounts
problems: Problem catalog with embeddings
problem_tests: Test cases for each problem
submissions: User submission history
user_profiles: Aggregated user statistics
personalized_difficulty_predictions: ML predictions per user-problem pair

Project Structure
├── app/
│   ├── cli.py                    # CLI commands
│   ├── config.py                 # Configuration
│   ├── database.py               # Database setup
│   ├── main.py                   # FastAPI app
│   ├── models.py                 # SQLAlchemy models
│   ├── routes.py                 # API endpoints
│   ├── schemas.py                # Pydantic schemas
│   └── services/
│       ├── code_executor.py      # Code execution & testing
│       ├── data_generator.py     # Synthetic data generation
│       ├── embedding_service.py  # Problem embeddings
│       ├── hint_timing_model.py  # ML hint timing
│       ├── mentor_service.py     # AI mentor logic
│       ├── personalized_difficulty_model.py  # ML difficulty
│       └── solution_analyzer.py  # Code comparison
├── static/
│   ├── home.html                 # Problem list page
│   ├── problem.html              # Problem solving page
│   ├── index.js                  # Home page logic
│   ├── problem.js                # Problem page logic
│   ├── style.css                 # Home page styles
│   └── problem.css               # Problem page styles
└── requirements.txt
Contributing

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
