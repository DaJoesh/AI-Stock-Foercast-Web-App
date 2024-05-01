import React, { useState } from "react";

const Forecast: React.FC = () => {
  const [startDate, setStartDate] = useState<string>("");
  const [tickerName, setTickerName] = useState<string>("");
  const [forecastValue, setForecastValue] = useState<number | null>(null);

  const handleForecast = async () => {
    try {
      const response = await fetch("http://54.151.57.130:5000/api/forecast", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          startDate: startDate,
          ticker: tickerName,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setForecastValue(data.forecastValue);
      } else {
        throw new Error(
          `Forecast request failed with status ${response.status}`
        );
      }
    } catch (error) {
      console.error("Error occurred:", error);
    }
  };

  return (
    <div className="forecast-container">
      <h1>Stock Forecast AI</h1>
      <div className="mb-3">
        <label htmlFor="startDate" className="form-label">
          Start Date
        </label>
        <input
          type="date"
          className="form-control"
          id="startDate"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
      </div>
      <div className="mb-3">
        <label htmlFor="tickerName" className="form-label">
          Ticker Name
        </label>
        <input
          type="text"
          className="form-control"
          id="tickerName"
          value={tickerName}
          onChange={(e) => setTickerName(e.target.value)}
        />
      </div>
      <button
        type="button"
        className="btn btn-primary"
        onClick={handleForecast}
      >
        Get Forecast
      </button>
      <div className="mt-3">
        <label htmlFor="forecastValue" className="form-label">
          Forecasted Value
        </label>
        <input
          type="text"
          className="form-control"
          id="forecastValue"
          value={forecastValue !== null ? forecastValue.toFixed(2) : ""}
          readOnly
        />
      </div>
    </div>
  );
};

export default Forecast;
