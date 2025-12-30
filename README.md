# AI Cycling Coach — Workout Logging and Analysis System

A personal assistant for amateur athletes designed for result analysis, training planning, and physical fitness improvement using local neural networks.

## Project Goal
[cite_start]To develop a program for logging and advanced statistics of cycling workouts with performance reviews and fitness improvement planning[cite: 1, 2]. [cite_start]The system allows users to log current sessions and schedule workouts for the sporting year[cite: 3].

## Key Features
* [cite_start]**Workout Management**: Ability to enter, correct, or delete activity data[cite: 11].
* [cite_start]**Planning**: Creation of training plans, setting goals, and scheduling upcoming sessions[cite: 3, 20, 21].
* [cite_start]**AI Analysis**: Implementation of a local neural network acting as a personal coach for comprehensive workout reviews and providing actionable advice[cite: 25, 26].
* [cite_start]**Statistics**: Displaying data such as activity type, duration, effort levels, and long-term data accumulation[cite: 4].
* [cite_start]**Data Handling**: Importing data via CSV files with future plans for integration with services like Strava or Intervals.icu[cite: 28].

## Tech Stack
* **Backend**: Python (FastAPI).
* **Frontend**: HTML5, Jinja2, JavaScript.
* [cite_start]**Database**: SQL (SQLite) for local data storage on the user's PC[cite: 29].
* [cite_start]**AI Engine**: Support for local neural networks to ensure data privacy.

## Roadmap

### Short-term Goals
* Optimization of AI agent interaction: faster processing of message history.
* Improvement of the system AI prompt for better coaching quality.
* [cite_start]Implementation of a minimal and concise UI design.
* Localization: full translation of the interface into English.
* Visualization of accumulated data using charts.

### Medium-term Goals
* Advanced Visualization: creating progress charts and power/HR intensity zones.
* Feature Expansion: adding support for running activities.
* AI Flexibility: implementing connections to external LLMs via API.
* Deployment: moving the application to a remote server.

## Installation Instructions

1. Clone the repository to your local machine.
2. Install the necessary dependencies:
   `pip install -r requirements.txt`
3. Ensure you have an environment for running local LLMs (e.g., Ollama) installed and active.
4. Start the development server:
   `uvicorn app.main:app --reload`
5. Open your browser and navigate to: `http://127.0.0.1:8000`
