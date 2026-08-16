# Enterprise Autonomous Market Intelligence & Competitive Strategy Platform
# **Author:** Muhammad Hassan Tariq

## 1. Project Overview

This project is an AI-powered market intelligence platform. The platform automatically collects competitor and market data from live public sources, processes it using natural language processing, and stores it in a structured knowledge graph.

Using this data, the platform generates AI-driven strategic insights, including SWOT analysis, pricing and product strategy recommendations, forecasted market trends, and simulated business scenarios. All insights are supported by evidence and a confidence score, and are presented through an Executive Dashboard.

## 2. Project Objective

The platform is designed to reduce the time and effort required for manual competitor analysis by automatically collecting market data, structuring it into a knowledge graph, and using AI to generate strategic recommendations and forecasts, all presented through a single Executive Dashboard.

## 3. Key Features

- Automated collection of live market data from multiple public sources
- Knowledge graph linking companies, products, and market events
- Natural language processing for company detection and sentiment analysis
- Semantic search over collected articles and reviews
- Time-series forecasting of competitor activity
- AI-generated SWOT analysis for each tracked company
- AI-generated strategic recommendations covering pricing, product roadmap, and partnerships
- Scenario simulation for hypothetical market events
- Conversational AI assistant for market-related questions
- Executive Dashboard summarizing all insights in one interface
- Caching layer for improved response performance
- Automated, scheduled data updates with no manual intervention required

## 4. Technology Stack

**Backend:** Python, FastAPI, PostgreSQL, Neo4j, Redis (Memurai)

**Artificial Intelligence:** LangGraph, LangChain, Groq (OpenAI GPT-OSS 120B), ChromaDB, Sentence Transformers, Prophet, spaCy, TextBlob, NetworkX

**Frontend:** HTML, CSS, JavaScript (Chart.js)

## 5. Project Structure
market-intel-platform/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   ├── agents/
│   │   ├── services/
│   │   └── utils/
│   └── .env.example
├── docs/
├── scripts/
├── frontend/
│   └── dashboard.html

- backend/ - FastAPI backend application
- app/main.py - Application entry point and route registration
- routes/ - API endpoint definitions
- agents/ - AI agent logic
- services/ - Business logic for different modules
- utils/ - Database connection and utility functions
- .env.example - Environment configuration template
- docs/ - Project documentation
- scripts/ - Data setup and live data ingestion scripts
- frontend/ - Frontend dashboard
- dashboard.html - Executive Dashboard interface

## 6. System Requirements

- Windows 10 or 11
- Python 3.11 or a compatible 3.x version
- Minimum 8 GB RAM (16 GB recommended)
- At least 10 GB of free disk space
- A stable internet connection, required for live data collection and AI processing

## 7. Quick Installation
Create a virtual environment
Activate the virtual environment
Install project dependencies from requirements.txt
Configure the .env file with database and API credentials
Full installation instructions, including database setup and troubleshooting, are provided in the Deployment and Installation Guide.

## 8. Quick Start

1. Start PostgreSQL, Neo4j, and Redis (Memurai).
2. From the backend directory, run:
uvicorn app.main:app --reload --port 8000
3. Open `frontend/dashboard.html` in a web browser to view the Executive Dashboard.

## 9. Data Sources

The platform collects live data from the following six sources:

- News Articles
- Industry Publications
- Public Report Coverage
- Customer Reviews
- Financial Reports (official SEC filings, covering only companies registered with the U.S. SEC)
- Patent Records

Data collection runs automatically on a scheduled basis.

## 10. Project Limitations

The platform tracks ten competitor companies and one product category, rather than the full enterprise-scale dataset. This scope was chosen to ensure the complete system architecture could be developed and tested.

Three data source was not implemented: company websites, product catalogs, and social media. Company websites and product catalogs vary in structure across companies and do not offer a shared public interface, which would require a separate solution to be built and maintained for each company individually. Social media integration was not implemented because paid access is required for reliable use, and an alternative platform restricted automated access during testing.

## 11. Documentation

- Deployment and Installation Guide
- Complete Technical Report
- System Architecture Diagram
