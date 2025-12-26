"""
Console UI - Output Formatter

Handles formatting and colored output for console.

Author: GDB Architecture Team
"""

import sys
from typing import Any, Optional


class Colors:
    """ANSI color codes."""
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Reset
    RESET = '\033[0m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'


class Formatter:
    """Handles console output formatting."""
    
    def __init__(self, enable_colors: bool = True):
        """
        Initialize formatter.
        
        Args:
            enable_colors: Whether to use colors in output
        """
        self.enable_colors = enable_colors and sys.stdout.isatty()
    
    def _apply_color(self, text: str, color: str) -> str:
        """Apply color code to text."""
        if not self.enable_colors:
            return text
        return f"{color}{text}{Colors.RESET}"
    
    # Color methods
    def success(self, text: str) -> str:
        """Format success message (green)."""
        return self._apply_color(text, Colors.GREEN)
    
    def error(self, text: str) -> str:
        """Format error message (red)."""
        return self._apply_color(text, Colors.RED)
    
    def warning(self, text: str) -> str:
        """Format warning message (yellow)."""
        return self._apply_color(text, Colors.YELLOW)
    
    def info(self, text: str) -> str:
        """Format info message (blue)."""
        return self._apply_color(text, Colors.BLUE)
    
    def header(self, text: str) -> str:
        """Format header (bold cyan)."""
        return self._apply_color(f"\n{text}\n{'=' * len(text)}\n", Colors.CYAN + Colors.BOLD)
    
    def subheader(self, text: str) -> str:
        """Format subheader (bold blue)."""
        return self._apply_color(f"\n{text}\n{'-' * len(text)}\n", Colors.BLUE + Colors.BOLD)
    
    def divider(self, char: str = "=", width: int = 80) -> str:
        """Create divider line."""
        return self._apply_color(char * width, Colors.DIM)
    
    # Data formatting methods
    def account_details(self, account: Any) -> str:
        """Format account details for display."""
        from app.utils.helpers import format_currency, format_datetime
        
        lines = [
            f"Account Number: {account.account_number}",
            f"Account Type:   {account.account_type}",
            f"Name:           {account.name}",
            f"Privilege:      {account.privilege}",
            f"Balance:        {format_currency(account.balance)}",
            f"Active:         {'Yes' if account.is_active else 'No'}",
            f"Opened:         {format_datetime(account.activated_date)}",
        ]
        
        if account.closed_date:
            lines.append(f"Closed:         {format_datetime(account.closed_date)}")
        
        return "\n".join(lines)
    
    def account_list(self, accounts: list) -> str:
        """Format list of accounts for display."""
        from app.utils.helpers import format_currency
        
        if not accounts:
            return self.warning("No accounts found")
        
        header = f"{'Acc No':<10} {'Type':<10} {'Name':<25} {'Balance':<15} {'Status':<10}"
        lines = [self.info(header)]
        lines.append(self.divider("-", 70))
        
        for acc in accounts:
            status = "Active" if acc.is_active else "Inactive"
            line = f"{acc.account_number:<10} {acc.account_type:<10} {acc.name:<25} {format_currency(acc.balance):>15} {status:<10}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def transaction_receipt(self, account_number: int, amount: float, transaction_type: str, balance: float) -> str:
        """Format transaction receipt."""
        from app.utils.helpers import format_currency, mask_account_number
        
        lines = [
            self.subheader("TRANSACTION RECEIPT"),
            f"Account:        {mask_account_number(account_number)} ({account_number})",
            f"Type:           {transaction_type.upper()}",
            f"Amount:         {format_currency(amount)}",
            f"New Balance:    {format_currency(balance)}",
            f"Status:         {self.success('SUCCESS')}",
        ]
        
        return "\n".join(lines)


# Global formatter instance
formatter = Formatter()
