# TerraAgent Dependencies

This document lists all dependencies required for the TerraAgent application. These packages are already included in the Replit environment, but if you're deploying locally, ensure these dependencies are installed.

## Core Dependencies
- flask>=2.3.2
- flask-sqlalchemy>=3.1.1
- gunicorn>=21.2.0
- python-dotenv>=1.0.0
- psycopg2-binary>=2.9.6
- email-validator>=2.0.0
- sqlalchemy>=2.0.15

## NLP and AI
- langchain>=0.0.267
- langchain-core>=0.1.4
- langchain-community>=0.0.12
- langchain-openai>=0.0.3
- openai>=1.3.0

## Document Processing
- trafilatura>=1.6.1

## RAG and Database Connectivity
- langchain-sqlserver>=0.0.2

## Monitoring
- prometheus-client>=0.17.1

## UI Components
- chainlit>=0.7.700

## Installation

To install these dependencies, you can use pip:

```bash
pip install flask flask-sqlalchemy gunicorn python-dotenv psycopg2-binary email-validator sqlalchemy langchain langchain-core langchain-community langchain-openai openai trafilatura langchain-sqlserver prometheus-client chainlit
```

Or if deploying with the provided scripts, they will handle dependency installation automatically.