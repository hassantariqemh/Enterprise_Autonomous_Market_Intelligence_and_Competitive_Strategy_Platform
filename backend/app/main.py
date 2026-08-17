from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import competitors, strategy, forecast, swot, dashboard, scenario, strategy_advisor, network_analysis

app = FastAPI(
    title="Autonomous Market Intelligence Platform",
    description="AI platform for competitor intelligence, trend forecasting, and strategic recommendations",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(competitors.router, prefix="/api/competitors", tags=["Competitors"])
app.include_router(strategy.router, prefix="/api/strategy", tags=["Strategy"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecasting"])
app.include_router(swot.router, prefix="/api", tags=["SWOT"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(scenario.router, prefix="/api", tags=["Scenario Simulation"])
app.include_router(strategy_advisor.router, prefix="/api", tags=["Strategy Advisor"])
app.include_router(network_analysis.router, prefix="/api", tags=["Network Analysis"])

@app.get("/")
def root():
    return {"status": "running", "service": "Market Intelligence Platform"}