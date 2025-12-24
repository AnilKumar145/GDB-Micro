"""
Enums for Transaction Service

Defines all enumeration types for:
- Transaction types (WITHDRAW, DEPOSIT, TRANSFER)
- Transaction status (PENDING, SUCCESS, FAILED, REVERSED)
- Transfer modes (NEFT, RTGS, IMPS, INTERNAL, UPI, CHEQUE)
- Account privilege levels (PREMIUM, GOLD, SILVER, BASIC)
"""

from enum import Enum


class TransactionType(str, Enum):
    """Types of transactions."""
    WITHDRAW = "WITHDRAW"
    DEPOSIT = "DEPOSIT"
    TRANSFER = "TRANSFER"


class TransactionStatus(str, Enum):
    """Status of a transaction."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class TransferMode(str, Enum):
    """Transfer modes (banking standards)."""
    NEFT = "NEFT"       # National Electronic Funds Transfer
    RTGS = "RTGS"       # Real Time Gross Settlement
    IMPS = "IMPS"       # Immediate Payment Service
    INTERNAL = "INTERNAL"  # Internal bank transfer
    UPI = "UPI"         # Unified Payments Interface
    CHEQUE = "CHEQUE"   # Cheque payment


class PrivilegeLevel(str, Enum):
    """Account privilege levels (determines transfer limits)."""
    PREMIUM = "PREMIUM"    # ₹100,000/day, 50 txns
    GOLD = "GOLD"          # ₹50,000/day, 30 txns
    SILVER = "SILVER"      # ₹25,000/day, 20 txns
    BASIC = "BASIC"        # ₹10,000/day, 5 txns


class UserRole(str, Enum):
    """User roles for RBAC."""
    CUSTOMER = "CUSTOMER"
    TELLER = "TELLER"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"
