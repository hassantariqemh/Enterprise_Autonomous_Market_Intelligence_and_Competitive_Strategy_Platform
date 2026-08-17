from app.services import forecast_service


def run(company: str = None) -> dict:
    """
    Trend & Forecasting Agent.
    Forecasts competitor activity level for the next 3 months based on
    historical event frequency in the Knowledge Graph.
    """
    return forecast_service.forecast_activity(company=company, periods=3)