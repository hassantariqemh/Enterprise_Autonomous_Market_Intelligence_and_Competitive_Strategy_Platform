"""
Forecasts future price trend for a product using Prophet, based on
historical (synthetic, demo-scale) monthly price data.
Run with: python scripts/forecast_price_trend.py
"""
import pandas as pd
from prophet import Prophet

# Synthetic monthly price history for Redmi Note 14 (demo-scale data,
# reflecting the known 10% price cut around April 2025)
data = {
    "ds": [
        "2024-08-01", "2024-09-01", "2024-10-01", "2024-11-01",
        "2024-12-01", "2025-01-01", "2025-02-01", "2025-03-01",
        "2025-04-01", "2025-05-01", "2025-06-01", "2025-07-01",
    ],
    "y": [
        279, 279, 275, 270,
        265, 249, 249, 245,
        224, 220, 218, 215,
    ],
}

df = pd.DataFrame(data)
df["ds"] = pd.to_datetime(df["ds"])

model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
model.fit(df)

future = model.make_future_dataframe(periods=3, freq="MS")
forecast = model.predict(future)

result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(3)
print("\nForecasted Redmi Note 14 price for next 3 months:")
print(result.to_string(index=False))