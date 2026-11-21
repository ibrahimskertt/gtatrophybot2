# GTA VI Trophy Forecast

This program forecasts GTA VI trophy earning rates one week out, providing five quantiles per trophy. It predicts how quickly players are likely to earn each trophy based on historical data.

## Model

The forecast is built on a per‑trophy trend of the logit of the earning rate against the natural logarithm of (1 + hours since release). We fit this trend using weighted least squares on the case history, then shrink the slope 65 % toward a tier prior (platinum 0.55, gold 0.75, silver 0.90, bronze 1.00). Saturation damping is applied as rates approach 50 % and caps are added for rare trophies. The spread is a combination of a 0.5 × √(horizon‑days) random walk and the residuals from the fit.

## Files

- `main.py` – the entry point that runs the forecast.
- `model.py` – contains the mathematical implementation of the forecasting logic.

## Validation

The practice histories are the flat pre‑refresh launch page. Practice validates the format and runtime of the data, but not the accuracy of the predictions.
