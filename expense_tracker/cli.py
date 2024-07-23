from typing import List, Dict, Any, Union, Type
from datetime import datetime

from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker, Mapped
from sqlalchemy.orm.attributes import InstrumentedAttribute

from expense_tracker.db.operations import BaseOperations
from expense_tracker.db.models import Account, Transaction, Category, Budget, RecurringExpense, Base
from expense_tracker.db.connection import get_db_engine
from expense_tracker.utils.validation import check_number_range, check_string_length, user_validation_message
from expense_tracker.utils.input_helpers import is_exit_command, EXIT_COMMANDS


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


class CLI:
    def __init__(self):
        self.menu_display = MenuDisplay()
        self.user_input = UserInput()
        self.engine = get_db_engine()
        self.Session = sessionmaker(bind=self.engine)

    def run(self):
        """
        Main loop for the CLI application.

        Displays the main menu and processes the user choices until exit is selected.
        """
        while True:
            self.menu_display.show_main_menu()
            choice = self.user_input.get_int("Enter your choice: ", min_value=0, max_value=5)

            if choice == 0 or is_exit_command(str(choice)):
                print("Exiting the application. Goodbye!")
                break

            self.process_main_menu_choice(choice)

    def process_main_menu_choice(self, choice: int):
        """
        Processes the user's main menu choice.

        Args:
            choice (int): The user's menu choice.
        """
        menu_actions = {
            1: (Account, "Accounts"),
            2: (Budget, "Budgets"),
            3: (Category, "Categories"),
            4: (RecurringExpense, "Recurring Expenses"),
            5: (Transaction, "Transactions"),
        }

        action = menu_actions.get(choice)
        if action:
            self.process_sub_menu_choice(action[0], action[1])
        else:
            print("Invalid choice. Please try again.")

    def process_sub_menu_choice(self, model: Type[Base], model_name: str):
        """
        Process the submenu choices for a specific model.

        Args:
             model (Type[Base]): The SQLAlchemy model class to manage.
             model_name (str): The display name for the model.
        """
        while True:
            self.menu_display.show_submenu(f"Manage {model_name}",
                                           [f"View {model_name}",
                                            f"Add {model_name}",
                                            f"Update {model_name}",
                                            f"Delete {model_name}"])
            choice = self.user_input.get_int("Enter your choice: ", min_value=0, max_value=4)

            if choice == 0 or is_exit_command(str(choice)):
                break

            self.manage_model(model, choice)

    def manage_model(self, model: Type[Base], choice: int):
        """
        Manage CRUD operations for a specific model based on user choice.

        Args:
             model (Type[Base]): The SQLAlchemy model class to manage.
             choice (int): The user's choice of operation.
        """
        model_actions = {
            1: lambda m: self.view_items(m),
            2: lambda m: self.add_item(m),
            3: lambda m: self.update_item(m),
            4: lambda m: self.delete_item(m)
        }

        action = model_actions.get(choice)
        if action:
            action(model)
        else:
            print("Invalid choice. Please try again.")

    def view_items(self, model: Type[Base]):
        """
        Display all items of a given model.

        Args:
            model (Type[Base]): The SQLAlchemy model class to view.
        """
        with self.Session() as session:
            items, total = BaseOperations.get_all(session, model)
            if items:
                print(f"\nTotal {model.__name__} Items: {total}")
                for item in items:
                    print(CLI.format_item(item))
            else:
                print(f"No {model.__name__} items found.")

    def add_item(self, model: Type[Base]):
        """
        Add a new item of a given model.

        Args:
            model (Type[Base]): The SQLAlchemy model class to add an item to.
        """
        print(f"Attempting to add a new {model.__name__}")  # Debug print
        attributes = self.get_model_input(model)
        print(f"Received attributes: {attributes}")  # Debug print
        if attributes:
            try:
                with self.Session() as session:
                    new_item = BaseOperations.create(session, model, **attributes)
                    print(f"\nNew {model.__name__} added successfully:")
                    print(self.format_item(new_item))
            except Exception as e:
                print(f"Error creating new {model.__name__}: {str(e)}")
        else:
            print(f"No attributes provided for new {model.__name__}. Cancelling addition.")

    def update_item(self, model: Type[Base]):
        """
        Update an existing item of a given model.

        Args:
            model (Type[Base]): The SQLAlchemy model class to update an item from.
        """
        item_id = self.user_input.get_int(f"Enter the ID of the {model.__name__} to update: ")
        with self.Session() as session:
            item = BaseOperations.read(session, model, item_id)
            if item:
                print(f"\nCurrent values:")
                print(CLI.format_item(item))
                attributes = self.get_model_input(model, for_update=True)
                if attributes:
                    updated_item = BaseOperations.update(session, model, item_id, **attributes)
                    print(f"\n{model.__name__} updated successfully:")
                    print(CLI.format_item(updated_item))
            else:
                print(f"{model.__name__} with ID {item_id} not found.")

    def delete_item(self, model: Type[Base]):
        """
        Delete an existing item of a given model.

        Args:
            model (Type[Base]): The SQLAlchemy model class to delete an item from.
        """
        item_id = self.user_input.get_int(f"Enter the ID of the {model.__name__} to delete: ")
        with self.Session() as session:
            item = BaseOperations.read(session, model, item_id)
            if item:
                print(f"\nItem to delete:")
                print(CLI.format_item(item))
                confirm = self.user_input.get_string("Are you sure you want to delete this item? (yes/no): ")
                if confirm.lower() == 'yes':
                    BaseOperations.delete(session, model, item_id)
                    print(f"{model.__name__} deleted successfully.")
                else:
                    print("Deletion canceled.")
            else:
                print(f"{model.__name__} with ID {item_id} not found.")

    def get_model_input(self, model: Type[Base], for_update: bool = False) -> Dict[str, Any]:
        """
        Get user input for a model's attributes.

        Args:
            model (Type[Base]): The SQLAlchemy model class.
            for_update (bool): Whether this input is for an update operation.

        Returns:
            Dict[str, Any]: Dictionary of attribute names and values.
        """
        print(f"Getting input for {model.__name__}")  # Debug print
        input_data = {}
        mapper = inspect(model)
        for attr_name, attr in mapper.column_attrs.items():
            print(f"Checking attribute: {attr_name}")  # Debug print
            if attr_name != 'id':  # Skip the 'id' attribute
                if for_update:
                    update = self.user_input.get_string(f"Update {attr_name}? (yes/no): ")
                    if update.lower() != 'yes':
                        continue

                column = attr.columns[0]
                attr_type = column.type.python_type
                print(f"Attribute {attr_name} is of type {attr_type}")  # Debug print

                while True:
                    value = None
                    if attr_type == int:
                        value = self.user_input.get_int(f"Enter {attr_name}: ")
                    elif attr_type == float:
                        value = self.user_input.get_float(f"Enter {attr_name}: ")
                    elif attr_type == str:
                        value = self.user_input.get_string(f"Enter {attr_name}: ")
                    elif attr_type == datetime.date:
                        value = self.user_input.get_date(f"Enter {attr_name} (YYYY-MM-DD): ")
                    else:
                        print(f"Unsupported attribute type for {attr_name}. Skipping.")
                        break

                    print(f"Received value for {attr_name}: {value}")  # Debug print

                    if value == 'exit':
                        return {}

                    if value is not None and self.validate_input(model, attr_name, value):
                        input_data[attr_name] = value
                        break
                    else:
                        print(f"Invalid input for {attr_name}. Please try again.")

        print(f"Returning input data: {input_data}")  # Debug print
        return input_data

    @staticmethod
    def validate_input(model: Type[Base], attr: str, value: Any) -> bool:
        """
        Validate user input for a specific model attribute.

        Args:
             model (Type[Base]): The SQL Alchemy model class.
             attr (str): The attribute name.
             value (Any): The input value to validate.

        Returns:
            bool: True if the input is valid, False otherwise.
        """
        # TODO: Implement validation logic using methods from validation.py.
        # For now, assumes all input is valid.
        return True

    @staticmethod
    def get_model_attributes(model: Type[Base]) -> List[str]:
        """
        Get the attributes of a given model.

        Args:
            model (Type[Base]): The SQLAlchemy model class.

        Returns:
            List[str]: List of attribute names.
        """
        return [attr for attr in dir(model) if not attr.startswith('_') and attr != 'id' and not callable(getattr(model, attr))]

    @staticmethod
    def format_item(item: Base) -> str:
        """
        Format an item for display.

        Args:
             item (Base): The SQLAlchemy model instance to format.

        Returns:
            str: A formatted string representation of the item.
        """
        attributes = inspect(item).attrs
        output = [f"ID: {item.id}"]  # Always include the ID first

        for attr_name, attr in attributes.items():
            if attr_name not in ['metadata', 'registry']:  # Exclude these attributes
                value = getattr(item, attr_name)
                if isinstance(value, list):
                    if value:  # Only include non-empty lists
                        output.append(f"{attr_name}: {len(value)} items")
                elif value is not None:  # Only include non-None values
                    output.append(f"{attr_name}: {value}")

        return " | ".join(output)


if __name__ == "__main__":
    cli = CLI()
    cli.run()
