# Weather Advisory Support Bot

A weather safety chatbot built with **LangGraph** that uses live weather data, location resolution, and configurable SOPs to provide traceable weather-based guidance.

## Application

**Live Application:** https://weather-advisory-support-bot-omdb.onrender.com


## Features

* Natural-language weather queries
* Live weather data using Open-Meteo
* Location resolution using Open-Meteo
* LangGraph-based workflow with conditional branching
* Configurable safety SOPs using YAML
* Activity-aware SOP matching
* LLM-based response generation using weather + SOP context
* Separate handling for weather/API failures
* Simple HTML chat frontend

## Architecture

```text
                         ┌───────────────┐
                         │     START     │
                         └───────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Understand Query     │
                    │         LLM            │
                    │                        │
                    │ Location + Activity    │
                    │ Intent + Time          │
                    └───────────┬────────────┘
                                │
                         Location found?
                         ┌──────┴──────┐
                        No             Yes
                        │               │
                        ▼               ▼
              ┌──────────────┐  ┌─────────────────┐
              │Weather Failed│  │Process Location │
              └──────┬───────┘  └────────┬────────┘
                     │                   │
                     │                   ▼
                     │          ┌─────────────────┐
                     │          │   Weather Tool  │
                     │          └────────┬────────┘
                     │                   │
                     │                   ▼
                     │          ┌─────────────────┐
                     │          │    SOP Engine   │
                     │          │                 │
                     │          │ Activity-based  │
                     │          │ safety matching │
                     │          └────────┬────────┘
                     │                   │
                     │                   ▼
                     │          ┌─────────────────┐
                     │          │  Response LLM   │
                     │          │                 │
                     │          │ Weather +       │
                     │          │ Activity + SOP  │
                     │          └────────┬────────┘
                     │                   │
                     └─────────┬─────────┘
                               ▼
                         ┌───────────────┐
                         │      END      │
                         └───────────────┘
```

### Workflow

1. **Query Understanding**
   The LLM extracts the location, activity, intent, and requested time from the user's query.

2. **Location Resolution**
   The location is converted into latitude and longitude.

3. **Weather Retrieval**
   The weather tool retrieves the relevant weather data from Open-Meteo.

4. **SOP Evaluation**
   The SOP engine evaluates configured safety rules against the weather and requested activity.

5. **Response Generation**
   The LLM receives the weather, activity, and matched SOP guidance and generates the final response.

SOPs act as **safety guidance and constraints**. The final response is generated using the SOP context together with the actual weather and user's activity.

## Project Structure

```text
backend/
├── data/
├── graph/
├── llm/
├── models/
├── services/
├── tools/
├── frontend/
├── main.py
├── pyproject.toml
└── uv.lock
```

## SOP Configuration

Safety policies are stored separately in:

```text
backend/data/sop.yaml
```

This keeps safety rules independent from the application logic, allowing policies to be updated without changing the LangGraph workflow.

Example:

```yaml
rules:
  - id: SOP-01
    category: outdoor_activity
    name: Strong Wind Outdoor Activity
    conditions:
      wind_speed_kmh:
        greater_than: 40
      activity:
        in: [cycling, running, hiking, walking]
    severity: high
    guidance: Avoid outdoor activities in strong winds.
```

## Setup

### Requirements

* Python 3.11+
* uv
* LLM API key

Install dependencies:

```bash
cd backend
uv sync
```

Create a `.env` file with the required API keys and configuration.

## Run

```bash
uv run uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Testing

The system is tested for:

* SOP rule service

## Design Principles

* **LLM:** Natural-language understanding and response generation
* **Weather Tool:** Live weather data
* **Location Tool:** Location-to-coordinate resolution
* **SOP Engine:** Deterministic safety-rule evaluation
* **LangGraph:** Workflow orchestration and error handling

The system keeps **weather retrieval and safety-rule evaluation deterministic**, while using the LLM for natural-language understanding and final response generation.

