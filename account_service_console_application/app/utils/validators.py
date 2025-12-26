"""
Account Service - Validation Utilities

Helper functions for account validation.

Author: GDB Architecture Team
"""

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

from app.exceptions.account_exceptions import (
    AgeRestrictionError,
    ValidationError,
    InvalidPinError
)


def validate_age(date_of_birth: str, min_age: int = 18) -> int:
    """
    Validate age from DOB.
    
    Args:
        date_of_birth: DOB in YYYY-MM-DD format
        min_age: Minimum required age (default 18)
        
    Returns:
        Age in years
        
    Raises:
        AgeRestrictionError: If age is less than min_age
        ValidationError: If DOB format is invalid
    """
    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        today = datetime.now().date()
        age = relativedelta(today, dob).years
        
        if age < min_age:
            raise AgeRestrictionError(age, min_age)
        
        return age
        
    except ValueError as e:
        raise ValidationError("date_of_birth", "Invalid date format. Use YYYY-MM-DD")


def validate_pin(pin: str) -> str:
    """
    Validate PIN format.
    
    Rules:
    - Must be 4-6 digits
    - Cannot be all same digits (1111, 2222, etc.)
    - Cannot be purely sequential consecutive digits (1234, 4321, etc.)
    
    Args:
        pin: PIN string
        
    Returns:
        Valid PIN
        
    Raises:
        InvalidPinError: If PIN is invalid
    """
    # Check length
    if not (4 <= len(pin) <= 6):
        raise InvalidPinError("PIN must be 4-6 digits")
    
    # Check if numeric
    if not pin.isdigit():
        raise InvalidPinError("PIN must contain only digits")
    
    # Check for all same digits
    if len(set(pin)) == 1:
        raise InvalidPinError("PIN cannot have all identical digits")
    
    # Check for purely sequential consecutive digits
    digits = [int(d) for d in pin]
    
    # Check ascending: 0123, 1234, 2345, etc.
    is_ascending_sequential = all(digits[i+1] - digits[i] == 1 for i in range(len(digits)-1))
    
    # Check descending: 3210, 4321, 5432, etc.
    is_descending_sequential = all(digits[i] - digits[i+1] == 1 for i in range(len(digits)-1))
    
    if is_ascending_sequential or is_descending_sequential:
        raise InvalidPinError("PIN cannot be purely sequential (like 1234 or 4321)")
    
    return pin


def validate_phone_number(phone: str, country: str = "IN") -> str:
    """
    Validate phone number.
    
    Args:
        phone: Phone number string
        country: Country code (default IN for India)
        
    Returns:
        Valid phone number
        
    Raises:
        ValidationError: If phone is invalid
    """
    # Check length (10-20 digits for India)
    if not (10 <= len(phone) <= 20):
        raise ValidationError("phone_no", f"Phone must be 10-20 digits, got {len(phone)}")
    
    # Check if numeric
    if not phone.isdigit():
        raise ValidationError("phone_no", "Phone must contain only digits")
    
    return phone


def validate_name(name: str) -> str:
    """
    Validate name.
    
    Args:
        name: Name string
        
    Returns:
        Valid name
        
    Raises:
        ValidationError: If name is invalid
    """
    if not name or len(name) < 1:
        raise ValidationError("name", "Name cannot be empty")
    
    if len(name) > 255:
        raise ValidationError("name", "Name must be 255 characters or less")
    
    return name


def validate_company_name(company_name: str) -> str:
    """
    Validate company name.
    
    Args:
        company_name: Company name string
        
    Returns:
        Valid company name
        
    Raises:
        ValidationError: If company name is invalid
    """
    if not company_name or len(company_name) < 1:
        raise ValidationError("company_name", "Company name cannot be empty")
    
    if len(company_name) > 255:
        raise ValidationError("company_name", "Company name must be 255 characters or less")
    
    return company_name


def validate_registration_number(registration_no: str) -> str:
    """
    Validate registration number.
    
    Args:
        registration_no: Registration number
        
    Returns:
        Valid registration number
        
    Raises:
        ValidationError: If registration number is invalid
    """
    if not registration_no or len(registration_no) < 1:
        raise ValidationError("registration_no", "Registration number cannot be empty")
    
    if len(registration_no) > 50:
        raise ValidationError("registration_no", "Registration number must be 50 characters or less")
    
    return registration_no


def validate_privilege(privilege: str) -> str:
    """
    Validate privilege level.
    
    Args:
        privilege: Privilege level (PREMIUM, GOLD, SILVER)
        
    Returns:
        Valid privilege level
        
    Raises:
        ValidationError: If privilege is invalid
    """
    valid_privileges = ["PREMIUM", "GOLD", "SILVER"]
    
    if privilege not in valid_privileges:
        raise ValidationError(
            "privilege",
            f"Invalid privilege '{privilege}'. Must be one of: {', '.join(valid_privileges)}"
        )
    
    return privilege


def validate_amount(amount: float) -> float:
    """
    Validate transaction amount.
    
    Args:
        amount: Amount to validate
        
    Returns:
        Valid amount
        
    Raises:
        ValidationError: If amount is invalid
    """
    if amount <= 0:
        raise ValidationError("amount", "Amount must be greater than 0")
    
    # Maximum transaction amount (₹10 lakhs)
    if amount > 1000000:
        raise ValidationError("amount", "Amount cannot exceed ₹10,00,000")
    
    return amount
