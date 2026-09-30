"""
PDF report generation for trading performance.
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Optional
import os
import pandas as pd

from utils.logger import setup_logger

logger = setup_logger(__name__)


class ReportGenerator:
    """
    Generates professional PDF reports for trading performance.
    """

    def __init__(self):
        """Initialize report generator."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

        logger.info("Report generator initialized")

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Metric label
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey
        ))

        # Metric value
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        ))

    def generate_backtest_report(
        self,
        metrics: Dict,
        trades_df: pd.DataFrame,
        config: Dict,
        output_path: str = "./reports/backtest_report.pdf"
    ) -> str:
        """
        Generate comprehensive backtest report.

        Args:
            metrics: Performance metrics dictionary
            trades_df: DataFrame with trade history
            config: Strategy configuration
            output_path: Output PDF path

        Returns:
            Path to generated PDF
        """
        # Create directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []

        # Title page
        story.append(Paragraph("HMM Trading Strategy Report", self.styles['CustomTitle']))
        story.append(Paragraph(
            f"Backtest Report - {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.5*inch))

        # Executive summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        story.extend(self._create_summary_section(metrics))
        story.append(Spacer(1, 0.3*inch))

        # Performance metrics
        story.append(Paragraph("Performance Metrics", self.styles['SectionHeading']))
        story.extend(self._create_metrics_table(metrics))
        story.append(Spacer(1, 0.3*inch))

        # Trade statistics
        story.append(Paragraph("Trade Statistics", self.styles['SectionHeading']))
        story.extend(self._create_trade_stats(metrics, trades_df))
        story.append(Spacer(1, 0.3*inch))

        # Strategy configuration
        story.append(PageBreak())
        story.append(Paragraph("Strategy Configuration", self.styles['SectionHeading']))
        story.extend(self._create_config_table(config))
        story.append(Spacer(1, 0.3*inch))

        # Trade history
        if not trades_df.empty:
            story.append(Paragraph("Trade History", self.styles['SectionHeading']))
            story.extend(self._create_trade_history_table(trades_df))

        # Build PDF
        doc.build(story)

        logger.info(f"Report generated: {output_path}")
        return output_path

    def _create_summary_section(self, metrics: Dict) -> list:
        """Create executive summary section."""
        elements = []

        total_return = metrics.get('total_return_pct', 0)
        alpha = metrics.get('alpha_pct', 0)
        win_rate = metrics.get('win_rate_pct', 0)

        # Performance verdict
        if total_return > 0 and alpha > 0:
            verdict = "✓ Strategy outperformed buy & hold"
            verdict_color = colors.green
        elif total_return > 0:
            verdict = "~ Strategy profitable but underperformed buy & hold"
            verdict_color = colors.orange
        else:
            verdict = "✗ Strategy lost money"
            verdict_color = colors.red

        summary_text = f"""
        <b>Overall Performance:</b> {verdict}<br/>
        <br/>
        The strategy achieved a total return of <b>{total_return:.2f}%</b> compared to
        buy & hold return of <b>{metrics.get('buy_hold_return_pct', 0):.2f}%</b>,
        resulting in an alpha of <b>{alpha:.2f}%</b>.<br/>
        <br/>
        <b>{metrics.get('num_trades', 0)}</b> trades were executed with a win rate of <b>{win_rate:.1f}%</b>.
        Maximum drawdown was <b>{metrics.get('max_drawdown_pct', 0):.2f}%</b>.
        """

        elements.append(Paragraph(summary_text, self.styles['Normal']))

        return elements

    def _create_metrics_table(self, metrics: Dict) -> list:
        """Create metrics table."""
        elements = []

        # Prepare data
        data = [
            ['Metric', 'Value'],
            ['Total Return', f"{metrics.get('total_return_pct', 0):.2f}%"],
            ['Buy & Hold Return', f"{metrics.get('buy_hold_return_pct', 0):.2f}%"],
            ['Alpha (Excess Return)', f"{metrics.get('alpha_pct', 0):.2f}%"],
            ['Sharpe Ratio', f"{metrics.get('sharpe_ratio', 0):.2f}"],
            ['Max Drawdown', f"{metrics.get('max_drawdown_pct', 0):.2f}%"],
            ['Win Rate', f"{metrics.get('win_rate_pct', 0):.1f}%"],
            ['Profit Factor', f"{metrics.get('profit_factor', 0):.2f}"],
            ['Number of Trades', f"{metrics.get('num_trades', 0)}"],
            ['Initial Capital', f"${metrics.get('initial_capital', 0):,.2f}"],
            ['Final Capital', f"${metrics.get('final_capital', 0):,.2f}"],
        ]

        # Create table
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f6')]),
        ]))

        elements.append(table)

        return elements

    def _create_trade_stats(self, metrics: Dict, trades_df: pd.DataFrame) -> list:
        """Create trade statistics section."""
        elements = []

        if trades_df.empty:
            elements.append(Paragraph("No trades executed.", self.styles['Normal']))
            return elements

        # Filter to sell trades only
        sells = trades_df[trades_df['action'] == 'SELL']

        if sells.empty:
            elements.append(Paragraph("No completed trades.", self.styles['Normal']))
            return elements

        data = [
            ['Statistic', 'Value'],
            ['Average Win', f"${metrics.get('avg_win', 0):.2f}"],
            ['Average Loss', f"${metrics.get('avg_loss', 0):.2f}"],
            ['Largest Win', f"${sells['pnl'].max():.2f}" if 'pnl' in sells.columns else "N/A"],
            ['Largest Loss', f"${sells['pnl'].min():.2f}" if 'pnl' in sells.columns else "N/A"],
            ['Avg Hold Time', f"{sells['hold_time_hours'].mean():.1f}h" if 'hold_time_hours' in sells.columns else "N/A"],
            ['Total Winning Trades', f"{(sells['pnl'] > 0).sum()}" if 'pnl' in sells.columns else "N/A"],
            ['Total Losing Trades', f"{(sells['pnl'] <= 0).sum()}" if 'pnl' in sells.columns else "N/A"],
        ]

        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f6')]),
        ]))

        elements.append(table)

        return elements

    def _create_config_table(self, config: Dict) -> list:
        """Create configuration table."""
        elements = []

        data = [
            ['Parameter', 'Value'],
            ['RSI Threshold', f"{config.get('rsi_threshold', 90)}"],
            ['Momentum Threshold', f"{config.get('momentum_threshold', 0.01)*100:.1f}%"],
            ['Volatility Threshold', f"{config.get('volatility_threshold', 0.06)*100:.1f}%"],
            ['ADX Threshold', f"{config.get('adx_threshold', 25)}"],
            ['Short EMA', f"{config.get('ema_short', 50)}"],
            ['Long EMA', f"{config.get('ema_long', 200)}"],
            ['Required Conditions', f"{config.get('required_conditions', 7)}/8"],
            ['Cooldown Period', f"{config.get('cooldown_hours', 48)}h"],
            ['Leverage', f"{config.get('leverage', 2.5)}x"],
            ['Stop Loss', f"{config.get('stop_loss_pct', -0.05)*100:.1f}%"],
            ['Take Profit', f"{config.get('take_profit_pct', 0.15)*100:.1f}%"],
            ['Commission Rate', f"{config.get('commission_rate', 0.001)*100:.3f}%"],
        ]

        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f6')]),
        ]))

        elements.append(table)

        return elements

    def _create_trade_history_table(self, trades_df: pd.DataFrame) -> list:
        """Create trade history table."""
        elements = []

        # Limit to last 20 trades for PDF
        recent_trades = trades_df.tail(20)

        # Prepare data
        data = [['Date', 'Action', 'Price', 'P&L', 'Return']]

        for _, trade in recent_trades.iterrows():
            date = str(trade.get('timestamp', ''))[:16]  # Truncate timestamp
            action = trade.get('action', '')
            price = f"${trade.get('price', 0):,.2f}"

            if action == 'SELL':
                pnl = f"${trade.get('pnl', 0):,.2f}"
                ret = f"{trade.get('pnl_pct', 0):+.2f}%"
            else:
                pnl = '-'
                ret = '-'

            data.append([date, action, price, pnl, ret])

        table = Table(data, colWidths=[1.5*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f2f6')]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(
            f"Showing last {len(recent_trades)} of {len(trades_df)} total trades.",
            self.styles['Normal']
        ))

        return elements
