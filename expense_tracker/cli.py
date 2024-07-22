from expense_tracker.db.operations import BaseOperations
from expense_tracker.db.models import Account, Transaction, Category, Budget, RecurringExpense
from expense_tracker.utils.validation import check_number_range, check_string_length, user_validation_message
from expense_tracker.utils.input_helpers import is_exit_command, EXIT_COMMANDS
from typing import List, Type, Any, Union
from datetime import datetime


# Outline:
# To start: User will see a menu with options to view and manage models (add, delete, update).
# Models: Will need to view/manage Transactions, Categories, Budget, Recurring Expenses, Accounts
# Export and import options will be available for mass uploading of transactions and data.


class MenuDisplay:
    @staticmethod
    def show_main_menu() -> None:
        print("\n-- Main Menu --")
        print("1. Manage Accounts")
        print("2. Manage Budgets")
        print("3. Manage Categories")
        print("4. Manage Recurring Expenses")
        print("5. Manage Transactions")
        print("0. Exit")

    @staticmethod
    def show_submenu(title: str, options: List[str]) -> None:
        print(f"\n-- {title} --")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print("0. Back to Main Menu")


class UserInput:
    @staticmethod
    def get_int(
        prompt: str,
        min_value: Union[int, None] = None,
        max_value: Union[int, None] = None
    ) -> Union[int, str]:
        """
        Get an integer input from the user within an optional range.

        Uses check_number_range() for range validation and user_validation_message() for user feedback.
        Returns 'exit' if is_exit_command() evaluates True.
        """
        while True:
            try:
                value = input(prompt)
                if is_exit_command(value):
                    return 'exit'

                int_value = int(value)
                if (min_value is not None or max_value is not None) and not check_number_range(int_value, min_value, max_value):
                    print(user_validation_message(int_value, min_value, max_value))
                else:
                    return int_value
            except ValueError:
                print(f"Invalid input. Please enter a valid number (integer) or {' / '.join(EXIT_COMMANDS)} to quit.")
            except (EOFError, KeyboardInterrupt):
                print(f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    @staticmethod
    def get_float(
        prompt: str,
        min_value: Union[float, None] = None,
        max_value: Union[float, None] = None
    ) -> Union[float, str]:
        """
        Get a float input from the user within an optional range.

        Uses check_number_range() for range validation and user_validation_message() for user feedback.
        Returns 'exit' if is_exit_command() evaluates True.
        """
        while True:
            try:
                value = input(prompt)
                if is_exit_command(value):
                    return 'exit'

                float_value = float(value)
                if (min_value is not None or max_value is not None) and not check_number_range(float_value, min_value, max_value):
                    print(user_validation_message(float_value, min_value, max_value))
                else:
                    return float_value
            except ValueError:
                print(f"Invalid input. Please enter a valid number (float) or {' / '.join(EXIT_COMMANDS)} to quit.")
            except (EOFError, KeyboardInterrupt):
                print(f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    @staticmethod
    def get_string(
        prompt: str,
        min_length: Union[int, None] = None,
        max_length: Union[int, None] = None
    ) -> str:
        """
        Get a string input from the user within an optional length range.

        Uses check_string_length() for range validation and user_validation_message() for user feedback.
        Returns 'exit' if is_exit_command() evaluates True.
        """
        while True:
            try:
                value = input(prompt).strip()
                if is_exit_command(value):
                    return 'exit'

                if (min_length is not None or max_length is not None) and not check_string_length(value, min_length, max_length):
                    print(user_validation_message(value, min_length, max_length))
                else:
                    return value
            except ValueError:
                print(f"Invalid input. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")
            except (EOFError, KeyboardInterrupt):
                print(f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    @staticmethod
    def get_date(prompt: str) -> Union[datetime.date, str]:
        """
        Get a date input from the user in the format YYYY-MM-DD.

        Returns 'exit' if is_exit_command() evaluates True.
        """
        while True:
            try:
                date_string = input(prompt).strip()
                if is_exit_command(date_string):
                    return 'exit'
                return datetime.strptime(date_string, "%Y-%m-%d").date()
            except ValueError:
                print(f"Invalid date format. Please use YYYY-MM-DD or {' / '.join(EXIT_COMMANDS)} to quit.")
            except (EOFError, KeyboardInterrupt):
                print(f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")
