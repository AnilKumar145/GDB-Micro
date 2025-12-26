"""
Account Service - Helper Utilities

Helper functions for account operations.

Author: GDB Architecture Team
"""

from datetime import datetime
import random
import string


class AccountNumberGenerator:
    """Generates and validates account numbers."""
    
    MIN_ACCOUNT_NUMBER = 1000
    MAX_ACCOUNT_NUMBER = 9999999
    
    @staticmethod
    def is_valid_account_number(account_number: int) -> bool:
        """
        Validate account number format.
        
        Args:
            account_number: Account number to validate
            
        Returns:
            True if valid, False otherwise
        """
        return (
            isinstance(account_number, int) and
            AccountNumberGenerator.MIN_ACCOUNT_NUMBER <= account_number <= AccountNumberGenerator.MAX_ACCOUNT_NUMBER
        )


def mask_account_number(account_number: int) -> str:
    """
    Mask account number for display (show only last 4 digits).
    
    Args:
        account_number: Account number to mask
        
    Returns:
        Masked account number (e.g., "****1234")
    """
    account_str = str(account_number)
    if len(account_str) <= 4:
        return account_str
    
    masked = "*" * (len(account_str) - 4) + account_str[-4:]
    return masked


def format_currency(amount: float) -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string (e.g., "₹12,345.00")
    """
    return f"₹{amount:,.2f}"


def format_date(date_obj: datetime) -> str:
    """
    Format date for display.
    
    Args:
        date_obj: Date object to format
        
    Returns:
        Formatted date string (e.g., "2024-12-26")
    """
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d")


def format_datetime(date_obj: datetime) -> str:
    """
    Format datetime for display.
    
    Args:
        date_obj: DateTime object to format
        
    Returns:
        Formatted datetime string (e.g., "2024-12-26 14:30:45")
    """
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")
