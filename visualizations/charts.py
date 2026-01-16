"""
Economic Indicator Visualization Module
Generates charts and plots for economic data analysis
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import os

class EconomicCharts:
    """Generate various charts for economic indicators"""

    def __init__(self, output_dir='outputs/charts'):
        """
        Initialize chart generator

        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')

    def plot_time_series(self, df, indicator_name, title=None, save=True):
        """
        Create a time series plot for an indicator

        Args:
            df: DataFrame with 'observation_date' and 'value' columns
            indicator_name: Name of the indicator
            title: Optional custom title
            save: Whether to save the plot

        Returns:
            Path to saved plot or None
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(df['observation_date'], df['value'],
                linewidth=2, color='#2E86AB', label=indicator_name)

        # Formatting
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax.set_title(title or f'{indicator_name} Over Time',
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        if save:
            filename = f"{indicator_name.lower().replace(' ', '_')}_timeseries.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved: {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            return None

    def plot_multiple_indicators(self, data_dict, title="Economic Indicators Dashboard", save=True):
        """
        Create a multi-panel plot for multiple indicators

        Args:
            data_dict: Dictionary {indicator_name: df} with DataFrames
            title: Dashboard title
            save: Whether to save the plot

        Returns:
            Path to saved plot or None
        """
        n_indicators = len(data_dict)
        fig, axes = plt.subplots(n_indicators, 1, figsize=(14, 4*n_indicators))

        if n_indicators == 1:
            axes = [axes]

        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

        for idx, (indicator_name, df) in enumerate(data_dict.items()):
            ax = axes[idx]
            ax.plot(df['observation_date'], df['value'],
                   linewidth=2, color=colors[idx % len(colors)], label=indicator_name)

            ax.set_ylabel('Value', fontsize=10, fontweight='bold')
            ax.set_title(indicator_name, fontsize=12, fontweight='bold', loc='left')
            ax.legend(loc='upper right', fontsize=9)
            ax.grid(True, alpha=0.3)

            # Format dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        axes[-1].set_xlabel('Date', fontsize=12, fontweight='bold')
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()

        if save:
            filepath = os.path.join(self.output_dir, 'multi_indicator_dashboard.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved: {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            return None

    def plot_correlation_heatmap(self, correlation_matrix, save=True):
        """
        Create a correlation heatmap

        Args:
            correlation_matrix: Pandas DataFrame with correlations
            save: Whether to save the plot

        Returns:
            Path to saved plot or None
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        im = ax.imshow(correlation_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)

        # Set ticks
        ax.set_xticks(np.arange(len(correlation_matrix.columns)))
        ax.set_yticks(np.arange(len(correlation_matrix.index)))
        ax.set_xticklabels(correlation_matrix.columns)
        ax.set_yticklabels(correlation_matrix.index)

        # Rotate labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add correlation values
        for i in range(len(correlation_matrix.index)):
            for j in range(len(correlation_matrix.columns)):
                text = ax.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black", fontsize=10)

        ax.set_title("Economic Indicator Correlations", fontsize=14, fontweight='bold', pad=20)
        fig.colorbar(im, ax=ax, label='Correlation Coefficient')
        plt.tight_layout()

        if save:
            filepath = os.path.join(self.output_dir, 'correlation_heatmap.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved: {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            return None

    def plot_interactive_dashboard(self, data_dict, save=True):
        """
        Create an interactive Plotly dashboard

        Args:
            data_dict: Dictionary {indicator_name: df} with DataFrames
            save: Whether to save as HTML

        Returns:
            Path to saved HTML or None
        """
        n_indicators = len(data_dict)

        # Create subplots
        fig = make_subplots(
            rows=n_indicators, cols=1,
            subplot_titles=list(data_dict.keys()),
            vertical_spacing=0.08,
            row_heights=[1]*n_indicators
        )

        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

        for idx, (indicator_name, df) in enumerate(data_dict.items(), 1):
            fig.add_trace(
                go.Scatter(
                    x=df['observation_date'],
                    y=df['value'],
                    mode='lines',
                    name=indicator_name,
                    line=dict(color=colors[(idx-1) % len(colors)], width=2),
                    hovertemplate='<b>Date</b>: %{x}<br><b>Value</b>: %{y:.2f}<extra></extra>'
                ),
                row=idx, col=1
            )

        # Update layout
        fig.update_layout(
            title_text="Economic Indicators Interactive Dashboard",
            title_font_size=20,
            height=300*n_indicators,
            showlegend=True,
            hovermode='x unified'
        )

        # Update axes
        for idx in range(1, n_indicators + 1):
            fig.update_xaxes(title_text="Date", row=idx, col=1)
            fig.update_yaxes(title_text="Value", row=idx, col=1)

        if save:
            filepath = os.path.join(self.output_dir, 'interactive_dashboard.html')
            fig.write_html(filepath)
            print(f"Saved: {filepath}")
            return filepath
        else:
            fig.show()
            return None

    def plot_trend_with_forecast(self, historical_df, forecast_df, indicator_name, save=True):
        """
        Plot historical data with forecast

        Args:
            historical_df: DataFrame with historical data
            forecast_df: DataFrame with forecast (must have 'date', 'forecast', 'lower', 'upper')
            indicator_name: Name of the indicator
            save: Whether to save the plot

        Returns:
            Path to saved plot or None
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        # Plot historical data
        ax.plot(historical_df['observation_date'], historical_df['value'],
               linewidth=2, color='#2E86AB', label='Historical')

        # Plot forecast
        ax.plot(forecast_df['date'], forecast_df['forecast'],
               linewidth=2, color='#F18F01', linestyle='--', label='Forecast')

        # Plot confidence interval
        ax.fill_between(forecast_df['date'],
                        forecast_df['lower'],
                        forecast_df['upper'],
                        alpha=0.3, color='#F18F01', label='95% Confidence Interval')

        # Formatting
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax.set_title(f'{indicator_name} - Historical & Forecast',
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10, loc='best')
        ax.grid(True, alpha=0.3)

        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        if save:
            filename = f"{indicator_name.lower().replace(' ', '_')}_forecast.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved: {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            return None

    def plot_yoy_change(self, df, indicator_name, save=True):
        """
        Plot year-over-year percentage change

        Args:
            df: DataFrame with 'observation_date' and 'yoy_pct_change' columns
            indicator_name: Name of the indicator
            save: Whether to save the plot

        Returns:
            Path to saved plot or None
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Color bars based on positive/negative
        colors = ['#6A994E' if x > 0 else '#C73E1D' for x in df['yoy_pct_change']]

        ax.bar(df['observation_date'], df['yoy_pct_change'],
              color=colors, alpha=0.7, width=20)

        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        # Formatting
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Year-over-Year Change (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{indicator_name} - Year-over-Year Percentage Change',
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='y')

        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()

        if save:
            filename = f"{indicator_name.lower().replace(' ', '_')}_yoy_change.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"Saved: {filepath}")
            plt.close()
            return filepath
        else:
            plt.show()
            return None
