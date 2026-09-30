"""
Notification system for trade alerts.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict
import os
import pandas as pd

from utils.logger import setup_logger

logger = setup_logger(__name__)


class NotificationManager:
    """
    Manages notifications for trading events.

    Supports:
    - Desktop notifications
    - Email notifications
    - Log notifications
    """

    def __init__(
        self,
        email_enabled: bool = False,
        smtp_server: Optional[str] = None,
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        recipient_email: Optional[str] = None
    ):
        """
        Initialize notification manager.

        Args:
            email_enabled: Enable email notifications
            smtp_server: SMTP server address
            smtp_port: SMTP port
            smtp_username: SMTP username
            smtp_password: SMTP password
            recipient_email: Recipient email address
        """
        self.email_enabled = email_enabled
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.recipient_email = recipient_email

        logger.info(f"Notification manager initialized (email={'enabled' if email_enabled else 'disabled'})")

    def notify_trade_entry(self, trade: Dict):
        """
        Notify about trade entry.

        Args:
            trade: Trade dictionary with details
        """
        title = "🟢 Trade Entry"
        message = (
            f"Entered LONG position\n"
            f"Price: ${trade['price']:,.2f}\n"
            f"Quantity: {trade['quantity']:.6f} BTC\n"
            f"Cost: ${trade['cost']:,.2f}\n"
            f"Time: {trade['timestamp']}\n"
            f"Regime: {trade.get('regime', 'N/A')}\n"
            f"Conditions: {trade.get('conditions_met', 'N/A')}/8"
        )

        self._send_notification(title, message, trade)

    def notify_trade_exit(self, trade: Dict):
        """
        Notify about trade exit.

        Args:
            trade: Trade dictionary with details
        """
        pnl = trade.get('pnl', 0)
        pnl_pct = trade.get('pnl_pct', 0)

        emoji = "🟢" if pnl >= 0 else "🔴"
        title = f"{emoji} Trade Exit"

        message = (
            f"Exited position\n"
            f"Exit Price: ${trade['price']:,.2f}\n"
            f"Entry Price: ${trade.get('entry_price', 0):,.2f}\n"
            f"P&L: ${pnl:,.2f} ({pnl_pct:+.2f}%)\n"
            f"Hold Time: {trade.get('hold_time_hours', 0):.1f}h\n"
            f"Reason: {trade.get('reason', 'N/A')}\n"
            f"Time: {trade['timestamp']}"
        )

        self._send_notification(title, message, trade)

    def notify_alert(self, alert_type: str, message: str):
        """
        Send general alert.

        Args:
            alert_type: Type of alert (warning, info, error)
            message: Alert message
        """
        emoji_map = {
            'warning': '⚠️',
            'info': 'ℹ️',
            'error': '❌',
            'success': '✅'
        }

        emoji = emoji_map.get(alert_type, 'ℹ️')
        title = f"{emoji} {alert_type.upper()}"

        self._send_notification(title, message, None)

    def _send_notification(self, title: str, message: str, data: Optional[Dict]):
        """
        Send notification through all enabled channels.

        Args:
            title: Notification title
            message: Notification message
            data: Additional data
        """
        # Always log
        logger.info(f"{title}: {message}")

        # Send email if enabled
        if self.email_enabled and self.recipient_email:
            try:
                self._send_email(title, message)
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")

    def _send_email(self, subject: str, body: str):
        """
        Send email notification.

        Args:
            subject: Email subject
            body: Email body
        """
        if not all([self.smtp_server, self.smtp_username, self.smtp_password, self.recipient_email]):
            logger.warning("Email not configured, skipping email notification")
            return

        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.smtp_username
        msg['To'] = self.recipient_email
        msg['Subject'] = f"[HMM Trading] {subject}"

        # Add body
        msg.attach(MIMEText(body, 'plain'))

        # Send email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent: {subject}")

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise


class TradeJournal:
    """
    Trading journal for logging and analyzing trades.
    """

    def __init__(self, journal_path: str = "./data/trade_journal.csv"):
        """
        Initialize trade journal.

        Args:
            journal_path: Path to journal CSV file
        """
        self.journal_path = journal_path

        # Create directory if needed
        os.makedirs(os.path.dirname(journal_path), exist_ok=True)

        logger.info(f"Trade journal initialized: {journal_path}")

    def log_trade(self, trade: Dict):
        """
        Log trade to journal.

        Args:
            trade: Trade dictionary
        """
        import pandas as pd

        # Convert to DataFrame
        trade_df = pd.DataFrame([trade])

        # Append to CSV
        if os.path.exists(self.journal_path):
            # Append to existing
            existing = pd.read_csv(self.journal_path)
            combined = pd.concat([existing, trade_df], ignore_index=True)
            combined.to_csv(self.journal_path, index=False)
        else:
            # Create new
            trade_df.to_csv(self.journal_path, index=False)

        logger.info(f"Trade logged to journal: {trade['action']} @ {trade['timestamp']}")

    def get_journal(self) -> pd.DataFrame:
        """Get full trade journal."""
        import pandas as pd

        if os.path.exists(self.journal_path):
            return pd.read_csv(self.journal_path)
        else:
            return pd.DataFrame()

    def get_summary(self) -> Dict:
        """Get journal summary statistics."""
        journal = self.get_journal()

        if journal.empty:
            return {'total_trades': 0}

        # Calculate stats
        sells = journal[journal['action'] == 'SELL']

        if sells.empty:
            return {'total_trades': 0}

        summary = {
            'total_trades': len(sells),
            'total_pnl': sells['pnl'].sum() if 'pnl' in sells.columns else 0,
            'avg_pnl': sells['pnl'].mean() if 'pnl' in sells.columns else 0,
            'win_rate': (sells['pnl'] > 0).sum() / len(sells) * 100 if 'pnl' in sells.columns else 0,
            'avg_hold_time': sells['hold_time_hours'].mean() if 'hold_time_hours' in sells.columns else 0,
        }

        return summary
