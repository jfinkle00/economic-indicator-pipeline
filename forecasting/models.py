"""
Economic Indicator Forecasting Module
Implements ARIMA and Prophet models for time series forecasting
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False
    print("statsmodels not installed. ARIMA forecasting unavailable.")

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("prophet not installed. Prophet forecasting unavailable.")


class EconomicForecaster:
    """Forecast economic indicators using statistical models"""

    def __init__(self):
        """Initialize forecaster"""
        self.model = None
        self.model_type = None
        self.fitted = False
        self.last_date = None
        self.freq = None

    def check_stationarity(self, timeseries, significance_level=0.05):
        """
        Check if time series is stationary using Augmented Dickey-Fuller test

        Args:
            timeseries: Pandas Series with time series data
            significance_level: Significance level for test

        Returns:
            Boolean indicating if series is stationary
        """
        if not ARIMA_AVAILABLE:
            return None

        result = adfuller(timeseries.dropna())
        p_value = result[1]

        is_stationary = p_value < significance_level

        return {
            'is_stationary': is_stationary,
            'p_value': p_value,
            'adf_statistic': result[0],
            'critical_values': result[4]
        }

    def fit_arima(self, df, order=(1, 1, 1), seasonal_order=None):
        """
        Fit ARIMA model to time series data

        Args:
            df: DataFrame with 'observation_date' and 'value' columns
            order: ARIMA order (p, d, q)
            seasonal_order: Seasonal ARIMA order (P, D, Q, s) or None

        Returns:
            Fitted model
        """
        if not ARIMA_AVAILABLE:
            raise ImportError("statsmodels not installed. Install with: pip install statsmodels")

        # Prepare data
        df = df.sort_values('observation_date')
        df = df.set_index('observation_date')
        series = df['value'].dropna()

        # Store the last date and infer frequency for forecasting
        self.last_date = series.index[-1]
        self.freq = pd.infer_freq(series.index)

        # If frequency can't be inferred, try to determine from data
        if self.freq is None:
            date_diffs = series.index.to_series().diff().dropna()
            median_diff = date_diffs.median()

            if median_diff <= pd.Timedelta(days=1):
                self.freq = 'D'  # Daily
            elif median_diff <= pd.Timedelta(days=7):
                self.freq = 'W'  # Weekly
            elif median_diff <= pd.Timedelta(days=31):
                self.freq = 'MS'  # Month start
            elif median_diff <= pd.Timedelta(days=92):
                self.freq = 'QS'  # Quarter start
            else:
                self.freq = 'YS'  # Year start

        # Fit model
        if seasonal_order:
            from statsmodels.tsa.statespace.sarimax import SARIMAX
            self.model = SARIMAX(series, order=order, seasonal_order=seasonal_order)
        else:
            self.model = ARIMA(series, order=order)

        self.model = self.model.fit()
        self.model_type = 'ARIMA'
        self.fitted = True

        print(f"ARIMA{order} model fitted successfully")
        return self.model

    def fit_prophet(self, df, yearly_seasonality=True, weekly_seasonality=False):
        """
        Fit Prophet model to time series data

        Args:
            df: DataFrame with 'observation_date' and 'value' columns
            yearly_seasonality: Include yearly seasonality
            weekly_seasonality: Include weekly seasonality

        Returns:
            Fitted model
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("prophet not installed. Install with: pip install prophet")

        # Prepare data for Prophet (needs 'ds' and 'y' columns)
        prophet_df = df[['observation_date', 'value']].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df = prophet_df.dropna()

        # Fit model
        self.model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=False
        )
        self.model.fit(prophet_df)
        self.model_type = 'Prophet'
        self.fitted = True

        print("Prophet model fitted successfully")
        return self.model

    def forecast_arima(self, steps=12, alpha=0.05):
        """
        Generate forecast using fitted ARIMA model

        Args:
            steps: Number of periods to forecast
            alpha: Significance level for confidence intervals (default 0.05 for 95% CI)

        Returns:
            DataFrame with forecast, lower and upper bounds
        """
        if not self.fitted or self.model_type != 'ARIMA':
            raise ValueError("ARIMA model not fitted. Call fit_arima() first.")

        # Generate forecast
        forecast_result = self.model.forecast(steps=steps, alpha=alpha)

        # Get confidence intervals
        forecast_df = self.model.get_forecast(steps=steps, alpha=alpha).summary_frame()

        # Create forecast dates using stored last_date and freq
        last_date = self.last_date
        freq = self.freq

        # Calculate the appropriate start date based on frequency
        if freq == 'D':
            start_date = last_date + timedelta(days=1)
        elif freq in ['W', 'W-SUN']:
            start_date = last_date + timedelta(days=7)
        elif freq in ['MS', 'M']:
            start_date = last_date + pd.DateOffset(months=1)
        elif freq in ['QS', 'Q']:
            start_date = last_date + pd.DateOffset(months=3)
        elif freq in ['YS', 'Y']:
            start_date = last_date + pd.DateOffset(years=1)
        else:
            # Default to next day if unknown
            start_date = last_date + timedelta(days=1)

        forecast_dates = pd.date_range(
            start=start_date,
            periods=steps,
            freq=freq
        )

        result = pd.DataFrame({
            'date': forecast_dates,
            'forecast': forecast_df['mean'].values,
            'lower': forecast_df['mean_ci_lower'].values,
            'upper': forecast_df['mean_ci_upper'].values
        })

        return result

    def forecast_prophet(self, periods=12, freq='MS'):
        """
        Generate forecast using fitted Prophet model

        Args:
            periods: Number of periods to forecast
            freq: Frequency of forecast ('MS' for month start, 'D' for daily)

        Returns:
            DataFrame with forecast, lower and upper bounds
        """
        if not self.fitted or self.model_type != 'Prophet':
            raise ValueError("Prophet model not fitted. Call fit_prophet() first.")

        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods, freq=freq)

        # Generate forecast
        forecast = self.model.predict(future)

        # Extract forecast period only
        forecast_only = forecast.tail(periods)

        # Create result DataFrame
        result = pd.DataFrame({
            'date': forecast_only['ds'],
            'forecast': forecast_only['yhat'],
            'lower': forecast_only['yhat_lower'],
            'upper': forecast_only['yhat_upper']
        })

        return result

    def auto_arima(self, df, max_p=5, max_d=2, max_q=5):
        """
        Automatically select best ARIMA order using AIC

        Args:
            df: DataFrame with 'observation_date' and 'value' columns
            max_p: Maximum p value to test
            max_d: Maximum d value to test
            max_q: Maximum q value to test

        Returns:
            Best order and fitted model
        """
        if not ARIMA_AVAILABLE:
            raise ImportError("statsmodels not installed")

        # Prepare data
        df = df.sort_values('observation_date')
        df = df.set_index('observation_date')
        series = df['value'].dropna()

        # Store the last date and infer frequency for forecasting
        self.last_date = series.index[-1]
        self.freq = pd.infer_freq(series.index)

        # If frequency can't be inferred, try to determine from data
        if self.freq is None:
            date_diffs = series.index.to_series().diff().dropna()
            median_diff = date_diffs.median()

            if median_diff <= pd.Timedelta(days=1):
                self.freq = 'D'  # Daily
            elif median_diff <= pd.Timedelta(days=7):
                self.freq = 'W'  # Weekly
            elif median_diff <= pd.Timedelta(days=31):
                self.freq = 'MS'  # Month start
            elif median_diff <= pd.Timedelta(days=92):
                self.freq = 'QS'  # Quarter start
            else:
                self.freq = 'YS'  # Year start

        best_aic = np.inf
        best_order = None
        best_model = None

        print("Searching for best ARIMA order...")

        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    try:
                        model = ARIMA(series, order=(p, d, q))
                        fitted_model = model.fit()
                        aic = fitted_model.aic

                        if aic < best_aic:
                            best_aic = aic
                            best_order = (p, d, q)
                            best_model = fitted_model

                    except:
                        continue

        print(f"Best ARIMA order: {best_order} (AIC: {best_aic:.2f})")

        self.model = best_model
        self.model_type = 'ARIMA'
        self.fitted = True

        return best_order, best_model

    def calculate_mape(self, actual, forecast):
        """
        Calculate Mean Absolute Percentage Error

        Args:
            actual: Actual values
            forecast: Forecasted values

        Returns:
            MAPE percentage
        """
        actual = np.array(actual)
        forecast = np.array(forecast)

        # Remove zero values to avoid division by zero
        mask = actual != 0
        mape = np.mean(np.abs((actual[mask] - forecast[mask]) / actual[mask])) * 100

        return mape

    def backtest(self, df, train_size=0.8, steps=12):
        """
        Perform simple backtesting

        Args:
            df: DataFrame with 'observation_date' and 'value' columns
            train_size: Proportion of data for training
            steps: Number of steps to forecast

        Returns:
            Dictionary with metrics
        """
        if not self.fitted:
            raise ValueError("Model not fitted")

        # Split data
        split_idx = int(len(df) * train_size)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:split_idx+steps]

        # Refit model on train data
        if self.model_type == 'ARIMA':
            self.fit_arima(train_df)
            forecast_df = self.forecast_arima(steps=steps)
        elif self.model_type == 'Prophet':
            self.fit_prophet(train_df)
            forecast_df = self.forecast_prophet(periods=steps)

        # Calculate metrics
        actual = test_df['value'].values
        forecast = forecast_df['forecast'].values[:len(actual)]

        mape = self.calculate_mape(actual, forecast)
        mae = np.mean(np.abs(actual - forecast))
        rmse = np.sqrt(np.mean((actual - forecast)**2))

        return {
            'mape': mape,
            'mae': mae,
            'rmse': rmse,
            'actual': actual,
            'forecast': forecast
        }
