"""
Console UI - Menu System

Interactive console menu for account operations.

Author: GDB Architecture Team
"""

import logging
from datetime import datetime
from typing import Optional

from app.services.account_service import AccountService
from app.models.account import (
    SavingsAccountCreate,
    CurrentAccountCreate,
    AccountUpdate,
)
from app.exceptions.account_exceptions import AccountException
from ui.formatter import formatter

logger = logging.getLogger(__name__)


class Menu:
    """Interactive console menu system."""
    
    def __init__(self):
        """Initialize menu."""
        self.service = AccountService()
    
    def clear_screen(self) -> None:
        """Clear console screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self) -> None:
        """Print application header."""
        print(formatter.header("GLOBAL DIGITAL BANK - ACCOUNT SERVICE CONSOLE"))
        print("Version 1.0.0 | Account Management System (No Authentication)\n")
    
    def get_input(self, prompt: str, input_type: type = str, allow_empty: bool = False) -> any:
        """
        Get user input with type conversion.
        
        Args:
            prompt: Input prompt
            input_type: Expected type (str, int, float)
            allow_empty: Whether empty input is allowed
            
        Returns:
            User input converted to specified type
        """
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                
                if not value:
                    if allow_empty:
                        return None
                    print(formatter.warning("⚠️ Input cannot be empty"))
                    continue
                
                if input_type == int:
                    return int(value)
                elif input_type == float:
                    return float(value)
                else:
                    return value
                    
            except ValueError:
                print(formatter.error(f"❌ Invalid input. Please enter a valid {input_type.__name__}"))
    
    def get_yes_no(self, prompt: str) -> bool:
        """Get yes/no input."""
        while True:
            response = input(f"{prompt} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print(formatter.warning("⚠️ Please enter 'y' or 'n'"))
    
    def pause(self) -> None:
        """Pause and wait for user input."""
        input(formatter.info("\nPress Enter to continue..."))
    
    # Main menu
    def show_main_menu(self) -> str:
        """Display main menu and get selection."""
        print(formatter.subheader("MAIN MENU"))
        print("""
1. Create Account
2. Account Operations
3. Account Management
4. PIN Management
5. Reports & Search
6. Exit
        """)
        return self.get_input("Select option", input_type=int)
    
    # ===== CREATE ACCOUNT =====
    def show_create_account_menu(self) -> None:
        """Create account menu."""
        while True:
            print(formatter.subheader("CREATE ACCOUNT"))
            print("""
1. Create Savings Account
2. Create Current Account
3. Back to Main Menu
            """)
            choice = self.get_input("Select option", input_type=int)
            
            if choice == 1:
                self.create_savings_account()
            elif choice == 2:
                self.create_current_account()
            elif choice == 3:
                break
            else:
                print(formatter.warning("⚠️ Invalid option"))
    
    def create_savings_account(self) -> None:
        """Create a savings account."""
        try:
            print(formatter.subheader("CREATE SAVINGS ACCOUNT"))
            
            # Get inputs
            name = self.get_input("Account Holder Name")
            dob = self.get_input("Date of Birth (YYYY-MM-DD)")
            gender = self.get_input("Gender (Male/Female/Others)")
            phone_no = self.get_input("Phone Number (10-20 digits)")
            pin = self.get_input("PIN (4-6 digits)")
            
            print("\nPrivilege Levels: PREMIUM, GOLD, SILVER")
            privilege = self.get_input("Privilege Level", allow_empty=True) or "SILVER"
            
            # Create account
            account = SavingsAccountCreate(
                name=name,
                pin=pin,
                date_of_birth=dob,
                gender=gender,
                phone_no=phone_no,
                privilege=privilege
            )
            
            account_number = self.service.create_savings_account(account)
            print(formatter.success(f"\n✅ Savings account created successfully!"))
            print(formatter.success(f"Account Number: {account_number}\n"))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    def create_current_account(self) -> None:
        """Create a current account."""
        try:
            print(formatter.subheader("CREATE CURRENT ACCOUNT"))
            
            # Get inputs
            name = self.get_input("Account Holder Name")
            company_name = self.get_input("Company Name")
            registration_no = self.get_input("Company Registration Number")
            website = self.get_input("Website (optional)", allow_empty=True)
            pin = self.get_input("PIN (4-6 digits)")
            
            print("\nPrivilege Levels: PREMIUM, GOLD, SILVER")
            privilege = self.get_input("Privilege Level", allow_empty=True) or "SILVER"
            
            # Create account
            account = CurrentAccountCreate(
                name=name,
                pin=pin,
                company_name=company_name,
                registration_no=registration_no,
                website=website,
                privilege=privilege
            )
            
            account_number = self.service.create_current_account(account)
            print(formatter.success(f"\n✅ Current account created successfully!"))
            print(formatter.success(f"Account Number: {account_number}\n"))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    # ===== ACCOUNT OPERATIONS =====
    def show_operations_menu(self) -> None:
        """Account operations menu."""
        while True:
            print(formatter.subheader("ACCOUNT OPERATIONS"))
            print("""
1. View Account Details
2. Check Balance
3. Debit Account (Withdrawal)
4. Credit Account (Deposit)
5. Update Account
6. Back to Main Menu
            """)
            choice = self.get_input("Select option", input_type=int)
            
            if choice == 1:
                self.view_account_details()
            elif choice == 2:
                self.check_balance()
            elif choice == 3:
                self.debit_account()
            elif choice == 4:
                self.credit_account()
            elif choice == 5:
                self.update_account()
            elif choice == 6:
                break
            else:
                print(formatter.warning("⚠️ Invalid option"))
    
    def view_account_details(self) -> None:
        """View account details."""
        try:
            print(formatter.subheader("VIEW ACCOUNT DETAILS"))
            account_number = self.get_input("Enter Account Number", input_type=int)
            
            account = self.service.get_account_details(account_number)
            print("\n" + formatter.account_details(account) + "\n")
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    def check_balance(self) -> None:
        """Check account balance."""
        try:
            print(formatter.subheader("CHECK BALANCE"))
            account_number = self.get_input("Enter Account Number", input_type=int)
            
            balance = self.service.get_balance(account_number)
            from app.utils.helpers import format_currency
            
            print(formatter.success(f"\nAccount {account_number} Balance: {format_currency(balance)}\n"))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    def debit_account(self) -> None:
        """Debit account."""
        try:
            print(formatter.subheader("DEBIT ACCOUNT"))
            account_number = self.get_input("Enter Account Number", input_type=int)
            amount = self.get_input("Enter Amount", input_type=float)
            
            # Verify PIN
            pin = self.get_input("Enter PIN")
            self.service.verify_pin(account_number, pin)
            
            # Debit
            self.service.debit_account(account_number, amount, "Withdrawal")
            
            # Get new balance
            balance = self.service.get_balance(account_number)
            print(formatter.transaction_receipt(account_number, amount, "Debit", balance))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    def credit_account(self) -> None:
        """Credit account."""
        try:
            print(formatter.subheader("CREDIT ACCOUNT"))
            account_number = self.get_input("Enter Account Number", input_type=int)
            amount = self.get_input("Enter Amount", input_type=float)
            
            # Credit
            self.service.credit_account(account_number, amount, "Deposit")
            
            # Get new balance
            balance = self.service.get_balance(account_number)
            print(formatter.transaction_receipt(account_number, amount, "Credit", balance))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    def update_account(self) -> None:
        """Update account details."""
        try:
            print(formatter.subheader("UPDATE ACCOUNT"))
            account_number = self.get_input("Enter Account Number", input_type=int)
            
            # Show current details
            account = self.service.get_account_details(account_number)
            print("\nCurrent Details:")
            print(formatter.account_details(account))
            
            print("\nLeave field blank to skip update\n")
            
            name = self.get_input("New Name", allow_empty=True)
            
            print("Privilege Levels: PREMIUM, GOLD, SILVER")
            privilege = self.get_input("New Privilege Level", allow_empty=True)
            
            phone_no = self.get_input("New Phone Number", allow_empty=True)
            website = self.get_input("New Website", allow_empty=True)
            
            update = AccountUpdate(
                name=name,
                privilege=privilege,
                phone_no=phone_no,
                website=website
            )
            
            self.service.update_account(account_number, update)
            print(formatter.success(f"\n✅ Account {account_number} updated successfully!\n"))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    # ===== ACCOUNT MANAGEMENT =====
    def show_management_menu(self) -> None:
        """Account management menu."""
        while True:
            print(formatter.subheader("ACCOUNT MANAGEMENT"))
            print("""
1. Activate Account
2. Inactivate Account
3. Close Account
4. Back to Main Menu
            """)
            choice = self.get_input("Select option", input_type=int)
            
            if choice == 1:
                self.activate_account()
            elif choice == 2:
                self.inactivate_account()
            elif choice == 3:
                self.close_account()
            elif choice == 4:
                break
            else:
                print(formatter.warning("⚠️ Invalid option"))
    
    def activate_account(self) -> None:
        """Activate account."""
        try:
            print(formatter.subheader("ACTIVATE ACCOUNT"))
            account_number = self.get_input("Enter Account Number", input_type=int)
            
            if self.get_yes_no(f"Are you sure you want to activate account {account_number}?"):
                self.service.activate_account(account_number)
                print(formatter.success(f"\n✅ Account {account_number} activated successfully!\n"))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    def inactivate_account(self) -> None:
        """Inactivate account."""
        try:
            print(formatter.subheader("INACTIVATE ACCOUNT"))
            account_number = self.get_input("Enter Account Number", input_type=int)
            
            if self.get_yes_no(f"Are you sure you want to inactivate account {account_number}?"):
                self.service.inactivate_account(account_number)
                print(formatter.success(f"\n✅ Account {account_number} inactivated successfully!\n"))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    def close_account(self) -> None:
        """Close account."""
        try:
            print(formatter.subheader("CLOSE ACCOUNT"))
            account_number = self.get_input("Enter Account Number", input_type=int)
            
            # Show balance
            account = self.service.get_account_details(account_number)
            from app.utils.helpers import format_currency
            print(f"\nCurrent Balance: {format_currency(account.balance)}")
            
            if self.get_yes_no(f"\nAre you sure you want to close account {account_number}?"):
                self.service.close_account(account_number)
                print(formatter.success(f"\n✅ Account {account_number} closed successfully!\n"))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    # ===== PIN MANAGEMENT =====
    def show_pin_menu(self) -> None:
        """PIN management menu."""
        while True:
            print(formatter.subheader("PIN MANAGEMENT"))
            print("""
1. Verify PIN
2. Back to Main Menu
            """)
            choice = self.get_input("Select option", input_type=int)
            
            if choice == 1:
                self.verify_pin()
            elif choice == 2:
                break
            else:
                print(formatter.warning("⚠️ Invalid option"))
    
    def verify_pin(self) -> None:
        """Verify PIN."""
        try:
            print(formatter.subheader("VERIFY PIN"))
            account_number = self.get_input("Enter Account Number", input_type=int)
            pin = self.get_input("Enter PIN")
            
            if self.service.verify_pin(account_number, pin):
                print(formatter.success("\n✅ PIN is correct!\n"))
            
        except AccountException as e:
            print(formatter.error(f"\n❌ {e.message}\n"))
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    # ===== REPORTS & SEARCH =====
    def show_reports_menu(self) -> None:
        """Reports and search menu."""
        while True:
            print(formatter.subheader("REPORTS & SEARCH"))
            print("""
1. List All Accounts
2. Search Accounts
3. Account Statistics
4. Back to Main Menu
            """)
            choice = self.get_input("Select option", input_type=int)
            
            if choice == 1:
                self.list_accounts()
            elif choice == 2:
                self.search_accounts()
            elif choice == 3:
                self.account_statistics()
            elif choice == 4:
                break
            else:
                print(formatter.warning("⚠️ Invalid option"))
    
    def list_accounts(self) -> None:
        """List all accounts."""
        try:
            print(formatter.subheader("ALL ACCOUNTS"))
            accounts = self.service.list_accounts(limit=100)
            print("\n" + formatter.account_list(accounts) + "\n")
            print(formatter.info(f"Total Accounts: {len(accounts)}"))
            
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    def search_accounts(self) -> None:
        """Search accounts."""
        try:
            print(formatter.subheader("SEARCH ACCOUNTS"))
            search_term = self.get_input("Enter Account Number or Name")
            
            accounts = self.service.search_accounts(search_term)
            print("\n" + formatter.account_list(accounts) + "\n")
            print(formatter.info(f"Found: {len(accounts)} account(s)"))
            
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    def account_statistics(self) -> None:
        """Show account statistics."""
        try:
            print(formatter.subheader("ACCOUNT STATISTICS"))
            accounts = self.service.list_accounts(limit=1000)
            
            from app.utils.helpers import format_currency
            
            total_accounts = len(accounts)
            active_accounts = sum(1 for a in accounts if a.is_active)
            inactive_accounts = total_accounts - active_accounts
            savings_accounts = sum(1 for a in accounts if a.account_type == "SAVINGS")
            current_accounts = sum(1 for a in accounts if a.account_type == "CURRENT")
            total_balance = sum(a.balance for a in accounts)
            
            print(f"""
Total Accounts:       {total_accounts}
Active Accounts:      {active_accounts}
Inactive Accounts:    {inactive_accounts}

Savings Accounts:     {savings_accounts}
Current Accounts:     {current_accounts}

Total Balance:        {format_currency(total_balance)}
Average Balance:      {format_currency(total_balance / total_accounts if total_accounts > 0 else 0)}
            """)
            
        except Exception as e:
            print(formatter.error(f"\n❌ Error: {str(e)}\n"))
        
        self.pause()
    
    # Main loop
    def run(self) -> None:
        """Run the menu system."""
        while True:
            self.clear_screen()
            self.print_header()
            
            choice = self.show_main_menu()
            
            if choice == 1:
                self.show_create_account_menu()
            elif choice == 2:
                self.show_operations_menu()
            elif choice == 3:
                self.show_management_menu()
            elif choice == 4:
                self.show_pin_menu()
            elif choice == 5:
                self.show_reports_menu()
            elif choice == 6:
                print(formatter.success("\n👋 Thank you for using Account Service Console!\n"))
                break
            else:
                print(formatter.warning("⚠️ Invalid option. Please try again."))
                self.pause()
