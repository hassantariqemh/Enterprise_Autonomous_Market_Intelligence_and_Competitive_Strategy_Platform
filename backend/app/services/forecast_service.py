import pandas as pd
from prophet import Prophet
from app.utils.neo4j_connection import db


def get_event_timeseries(company: str = None):
    """
    Builds a monthly event-count time series from the Knowledge Graph.
    If a company is given, restricts to that company's events;
    otherwise aggregates events across all competitors.
    """
    if company:
        query = """
        MATCH (c:Company {name: $company})-[:INVOLVED_IN]->(e:Event)
        RETURN e.date AS date
        """
        params = {"company": company}
    else:
        query = "MATCH (e:Event) RETURN e.date AS date"
        params = {}

    rows = db.run_query(query, params)
    dates = [str(r["date"]) for r in rows if r["date"] is not None]

    if not dates:
        return None

    df = pd.DataFrame({"date": pd.to_datetime(dates)})
    df["ds"] = df["date"].dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby("ds").size().reset_index(name="y")
    return monthly


def forecast_activity(company: str = None, periods: int = 3):
    """
    Forecasts competitor activity (event frequency) for the next N months
    using Prophet. Returns None if there is not enough data to fit a model.
    """
    monthly = get_event_timeseries(company)

    if monthly is None or len(monthly) < 2:
        return {
            "status": "insufficient_data",
            "message": "Not enough historical event data to generate a forecast. "
                       "This is expected at prototype scale; a production system "
                       "with continuous data collection would have enough history.",
        }

    model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
    model.fit(monthly)

    future = model.make_future_dataframe(periods=periods, freq="MS")
    forecast = model.predict(future)

    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)
    return {
        "status": "ok",
        "company": company or "all_competitors",
        "history_months": len(monthly),
        "forecast": [
            {
                "month": row.ds.strftime("%Y-%m"),
                "predicted_activity": round(row.yhat, 2),
                "lower_bound": round(row.yhat_lower, 2),
                "upper_bound": round(row.yhat_upper, 2),
            }
            for row in result.itertuples()
        ],
    }