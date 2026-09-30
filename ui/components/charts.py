"""
Plotly chart components for the dashboard.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


def create_candlestick_chart(
    data: pd.DataFrame,
    regime_states: np.ndarray,
    bull_state: int,
    bear_state: int,
    trades: List[Dict] = None,
    height: int = 600
) -> go.Figure:
    """
    Create interactive candlestick chart with regime highlighting.

    Args:
        data: DataFrame with OHLCV data and indicators
        regime_states: Array of HMM states
        bull_state: Bull regime state number
        bear_state: Bear regime state number
        trades: List of trade dictionaries
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price & Regime', 'Volume'),
        row_heights=[0.7, 0.3]
    )

    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='BTC-USD',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )

    # Add regime background colors
    if len(regime_states) == len(data):
        for i in range(1, len(data)):
            regime = regime_states[i]

            if regime == bull_state:
                color = 'rgba(0, 255, 0, 0.1)'
            elif regime == bear_state:
                color = 'rgba(255, 0, 0, 0.1)'
            else:
                color = 'rgba(128, 128, 128, 0.05)'

            fig.add_vrect(
                x0=data.index[i-1],
                x1=data.index[i],
                fillcolor=color,
                layer="below",
                line_width=0,
                row=1, col=1
            )

    # Add EMAs
    if 'EMA_50' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['EMA_50'],
                name='EMA 50',
                line=dict(color='blue', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )

    if 'EMA_200' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['EMA_200'],
                name='EMA 200',
                line=dict(color='orange', width=1),
                opacity=0.7
            ),
            row=1, col=1
        )

    # Add trade markers
    if trades:
        buys = [t for t in trades if t['action'] == 'BUY']
        sells = [t for t in trades if t['action'] == 'SELL']

        if buys:
            buy_times = [t['timestamp'] for t in buys]
            buy_prices = [t['price'] for t in buys]
            fig.add_trace(
                go.Scatter(
                    x=buy_times,
                    y=buy_prices,
                    mode='markers',
                    name='Buy',
                    marker=dict(
                        symbol='triangle-up',
                        size=12,
                        color='green',
                        line=dict(color='darkgreen', width=1)
                    )
                ),
                row=1, col=1
            )

        if sells:
            sell_times = [t['timestamp'] for t in sells]
            sell_prices = [t['price'] for t in sells]
            fig.add_trace(
                go.Scatter(
                    x=sell_times,
                    y=sell_prices,
                    mode='markers',
                    name='Sell',
                    marker=dict(
                        symbol='triangle-down',
                        size=12,
                        color='red',
                        line=dict(color='darkred', width=1)
                    )
                ),
                row=1, col=1
            )

    # Add volume bars
    colors = ['red' if close < open else 'green'
              for close, open in zip(data['Close'], data['Open'])]

    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.5
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_layout(
        title='BTC-USD Price with Regime Detection',
        xaxis_rangeslider_visible=False,
        height=height,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig


def create_portfolio_chart(
    portfolio_history: pd.DataFrame,
    metrics: Dict,
    height: int = 400
) -> go.Figure:
    """
    Create portfolio value chart.

    Args:
        portfolio_history: DataFrame with portfolio values
        metrics: Performance metrics dictionary
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Portfolio value line
    fig.add_trace(
        go.Scatter(
            x=portfolio_history.index,
            y=portfolio_history['portfolio_value'],
            name='Portfolio Value',
            line=dict(color='blue', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 100, 255, 0.1)'
        )
    )

    # Add initial capital line
    initial_capital = metrics.get('initial_capital', 10000)
    fig.add_hline(
        y=initial_capital,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Initial: ${initial_capital:,.0f}",
        annotation_position="right"
    )

    # Update layout
    fig.update_layout(
        title='Portfolio Value Over Time',
        xaxis_title='Date',
        yaxis_title='Value (USD)',
        height=height,
        hovermode='x unified'
    )

    return fig


def create_conditions_chart(
    conditions: Dict,
    height: int = 300
) -> go.Figure:
    """
    Create bar chart showing condition status.

    Args:
        conditions: Dictionary of condition name -> met status
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    names = list(conditions.keys())
    values = [1 if v else 0 for v in conditions.values()]
    colors = ['green' if v else 'red' for v in conditions.values()]

    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=values,
            marker_color=colors,
            text=['✓' if v else '✗' for v in conditions.values()],
            textposition='auto'
        )
    ])

    fig.update_layout(
        title='Trading Conditions Status',
        xaxis_title='Condition',
        yaxis_title='Met',
        height=height,
        showlegend=False,
        yaxis=dict(tickvals=[0, 1], ticktext=['NO', 'YES'])
    )

    return fig


def create_drawdown_chart(
    portfolio_history: pd.DataFrame,
    height: int = 300
) -> go.Figure:
    """
    Create drawdown chart.

    Args:
        portfolio_history: DataFrame with portfolio values
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    portfolio_values = portfolio_history['portfolio_value']
    cumulative_max = portfolio_values.cummax()
    drawdown = (portfolio_values - cumulative_max) / cumulative_max * 100

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=drawdown.index,
            y=drawdown,
            name='Drawdown',
            line=dict(color='red', width=2),
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.2)'
        )
    )

    fig.update_layout(
        title='Portfolio Drawdown',
        xaxis_title='Date',
        yaxis_title='Drawdown (%)',
        height=height,
        hovermode='x unified'
    )

    return fig


def create_returns_distribution(
    trades_df: pd.DataFrame,
    height: int = 300
) -> go.Figure:
    """
    Create histogram of trade returns.

    Args:
        trades_df: DataFrame with trade records
        height: Chart height in pixels

    Returns:
        Plotly figure
    """
    if 'return_pct' not in trades_df.columns:
        # Return empty figure
        fig = go.Figure()
        fig.update_layout(
            title='Trade Returns Distribution',
            height=height,
            annotations=[{
                'text': 'No trade data available',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'showarrow': False
            }]
        )
        return fig

    returns = trades_df[trades_df['action'] == 'SELL']['return_pct'] * 100

    fig = go.Figure(data=[
        go.Histogram(
            x=returns,
            nbinsx=20,
            marker_color='blue',
            opacity=0.7
        )
    ])

    fig.update_layout(
        title='Trade Returns Distribution',
        xaxis_title='Return (%)',
        yaxis_title='Frequency',
        height=height
    )

    return fig
