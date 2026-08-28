# AI Cycling Coach

A personal web application for cyclists that combines workout tracking, training statistics, and AI-powered coaching.

The project is built with Python and FastAPI and uses a local LLM through Ollama. The main goal is to provide a simple environment where an athlete can store training data, review recent activity, and communicate with an AI coach using their personal profile and training history.

## Current Features

### Authentication
~~~~
- User registration
- User login and logout
- Password authentication
- Cookie-based authentication using JWT

### Athlete Profile

Users can create and manage their athlete profile.

The profile is used by the AI Coach as part of the context for generating coaching responses.

### Workout Import

Workout data can be imported from CSV files.

The import process:

- validates the uploaded file;
- calculates a SHA-256 hash;
- detects duplicate workouts;
- stores the uploaded file;
- parses the CSV data into a workout;
- saves the workout to the database.

Multiple files can be imported at the same time. Each file is processed independently, so an error in one file does not prevent the remaining files from being imported.

### Workout History

Users can view their previously imported workouts.

Workout data is associated with the authenticated user, so users only have access to their own training data.

### Statistics

The application provides a summary of workout data for a selected period.

Statistics are calculated from the user's stored workouts and can be used by the AI Coach as part of the training context.

### AI Coach

The application includes an AI Coach powered by a local LLM through Ollama.

The AI Coach receives several types of context before generating a response:

- athlete profile;
- workout summary for the last 7 days;
- previous chat history;
- system prompt;
- user prompt;
- current prompt.

This allows the AI Coach to provide recommendations based on the athlete's recent training activity rather than treating every message as an isolated conversation.

The athlete can use the AI Coach to discuss training, analyse recent activity, and ask for training recommendations or a proposed training plan.

Chat history is stored in the database and is available in subsequent conversations.

---

## Architecture

The project follows a layered architecture:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
Database
```

### Router

Routers are responsible for the HTTP layer:

- receiving requests;
- validating request parameters;
- working with FastAPI dependencies;
- calling services;
- returning HTTP responses and templates.

Routers do not access repositories directly.

### Service

Services contain application and business logic.

Examples:

- `UserService`
- `ProfileService`
- `WorkoutService`
- `StatisticsService`
- `ImportService`
- `CoachService`

Services coordinate operations between repositories and other application components.

For example, `ImportService` coordinates file validation, file storage, CSV parsing, and workout persistence.

### Repository

Repositories are responsible for database operations.

Examples:

- `UserRepository`
- `ProfileRepository`
- `WorkoutRepository`
- `ChatRepository`

Repositories encapsulate SQLModel session operations and database queries.

### LLM Provider

The LLM integration is separated behind a provider interface.

```text
CoachService
      ↓
LLMProvider
      ↓
OllamaProvider
      ↓
Ollama
```

This keeps the main application independent from a specific LLM implementation and allows another provider to be added later.

---

## Project Structure

```text
app/
├── core/
│   ├── config.py
│   ├── dependencies.py
│   ├── exceptions.py
│   └── templating.py
│
├── infrastructure/
│   └── llm/
│       ├── llm_protocol.py
│       └── ollama_provider.py
│
├── models/
│   └── models.py
│
├── repository/
│   ├── chat_repo.py
│   ├── profile_repo.py
│   ├── user_repo.py
│   └── workout_repo.py
│
├── routers/
│   ├── chat.py
│   ├── coach.py
│   ├── imports.py
│   ├── login.py
│   ├── profile.py
│   ├── register.py
│   ├── statistics.py
│   └── workout.py
│
├── schemas/
│   ├── profile.py
│   └── workoutDTO.py
│
├── services/
│   ├── coach_service.py
│   ├── file_service.py
│   ├── import_service.py
│   ├── parse_cvs.py
│   ├── profile_service.py
│   ├── security.py
│   ├── statistics_service.py
│   ├── stats_calculator.py
│   ├── user_service.py
│   └── workout_service.py
│
├── templates/
│
└── tests/
    ├── fixtures/
    └── test_*.py
```

---

## Tech Stack

### Backend

- Python
- FastAPI
- SQLModel
- SQLite

### Frontend

- HTML5
- Jinja2 templates
- JavaScript

### Data Processing

- pandas

### AI

- Ollama
- Local LLM
- Provider abstraction through `LLMProvider`

### Testing

- pytest
- pytest-asyncio

### Configuration

- pydantic-settings
- `.env` environment variables

---

## Configuration

The application uses environment variables for configuration.

Create a `.env` file in the project root.

At minimum, the application requires a secret key for authentication:

```env
SECRET_KEY=your-secret-key
```

The secret key is loaded through the application configuration and is used for JWT authentication.

Ollama must also be installed and running locally if you want to use the AI Coach.

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd mypet
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the `.env` file and configure the required environment variables.

Make sure Ollama is installed and running locally.

---

## Running the Application

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

---

## Running Tests

Run the complete test suite with:

```bash
pytest
```

The test suite covers the main application scenarios, including:

- authentication;
- user profiles;
- workout operations;
- statistics;
- AI Coach;
- CSV import;
- file handling.

The import tests also cover independent processing of multiple files, including the case where one file fails while other files are successfully imported.

---

## CSV Import

Workout files are imported through the application interface.

The import pipeline is designed so that each uploaded file is processed independently:

```text
CSV file
   ↓
File validation
   ↓
SHA-256 hash
   ↓
Duplicate check
   ↓
File storage
   ↓
CSV parsing
   ↓
Workout creation
   ↓
Database commit
```

If a file cannot be parsed or processed, its database changes are rolled back and the stored file is removed when necessary.

A successfully imported file remains stored locally.

---

## Current Development Status

The project is currently at the MVP stage.

The main application flow is implemented:

```text
Registration
     ↓
Login
     ↓
Athlete Profile
     ↓
Workout Import
     ↓
Workout History
     ↓
Statistics
     ↓
AI Coach
```

The current development focus has been on establishing a clear backend architecture and covering the main application scenarios with tests.

---

## Roadmap

### Short Term

- Update and improve the user interface.
- Improve the AI Coach prompts and coaching quality.
- Add workout data visualizations.
- Improve the project documentation and deployment configuration.

### Medium Term

- Add progress charts.
- Add distance and time visualizations.
- Add training intensity zones.
- Add support for running workouts.
- Add support for external LLM APIs.
- Migrate from SQLite to PostgreSQL.
- Add Docker configuration.
- Deploy the application to a remote server.

### Long Term

- Improve asynchronous processing where it provides a real benefit.
- Add integrations with external training platforms such as Strava or Intervals.icu.
- Expand the AI Coach with more advanced training analysis.

---

## Project Goal

AI Cycling Coach is both a personal project and a practical backend development project.

The main goal is to build a working application while developing a deeper understanding of:

- Python backend development;
- FastAPI;
- database design;
- layered architecture;
- dependency injection;
- testing;
- file processing;
- data analysis;
- LLM integration;
- application deployment.
