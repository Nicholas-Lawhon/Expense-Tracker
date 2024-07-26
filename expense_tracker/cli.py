from typing import List, Dict, Any, Union, Type
from datetime import datetime
import enum
from sqlalchemy import inspect, Enum as SQLAlchemyEnum
from sqlalchemy.orm import sessionmaker, Mapped
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from expense_tracker.db.operations import BaseOperations
from expense_tracker.db.models import Account, Transaction, Category, Budget, RecurringExpense, Base, IntervalType, TransactionType
from expense_tracker.db.connection import get_db_engine, get_db_session
from expense_tracker.utils.validation import check_number_range, check_string_length, user_validation_message
from expense_tracker.utils.input_helpers import is_exit_command, EXIT_COMMANDS


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
        self.get_session = get_db_session  # Changed to the function itself, not its result

    def run(self) -> None:
        while True:
            self.menu_display.show_main_menu()
            choice = self.user_input.get_int("Enter your choice: ", min_value=0, max_value=5)

            if choice == 0 or is_exit_command(str(choice)):
                print("Exiting the application. Goodbye!")
                break

            self.process_main_menu_choice(choice)

    def process_main_menu_choice(self, choice: int) -> None:
        menu_actions: Dict[int, Tuple[Type[Base], str]] = {
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

    def process_sub_menu_choice(self, model: Type[Base], model_name: str) -> None:
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

    def manage_model(self, model: Type[Base], choice: int) -> None:
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

    def view_items(self, model: Type[Base]) -> None:
        with self.get_session() as session:
            items, total = BaseOperations.get_all(session, model)
            if items:
                print(f"\nTotal {model.__name__} Items: {total}")
                for item in items:
                    print(CLI.format_item(item))
            else:
                print(f"No {model.__name__} items found.")

    def add_item(self, model: Type[Base]) -> None:
        print(f"Attempting to add a new {model.__name__}")
        attributes = self.get_model_input(model)
        print(f"Received attributes: {attributes}")
        if attributes:
            try:
                with self.get_session() as session:
                    new_item = BaseOperations.create(session, model, **attributes)
                    print(f"\nNew {model.__name__} added successfully:")
                    print(self.format_item(new_item))
            except IntegrityError as e:
                print(f"Database integrity error: {str(e)}")
            except SQLAlchemyError as e:
                print(f"Database error: {str(e)}")
            except Exception as e:
                print(f"An unexpected error occurred: {str(e)}")
        else:
            print(f"No attributes provided for new {model.__name__}. Cancelling addition.")

    def update_item(self, model: Type[Base]) -> None:
        item_id = self.user_input.get_int(f"Enter the ID of the {model.__name__} to update: ")
        try:
            with self.get_session() as session:
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
        except IntegrityError as e:
            print(f"Database integrity error: {str(e)}")
        except SQLAlchemyError as e:
            print(f"Database error: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    def delete_item(self, model: Type[Base]) -> None:
        item_id = self.user_input.get_int(f"Enter the ID of the {model.__name__} to delete: ")
        try:
            with self.get_session() as session:
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
        except IntegrityError as e:
            print(f"Database integrity error: {str(e)}")
        except SQLAlchemyError as e:
            print(f"Database error: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

    def get_model_input(self, model: Type[Base], for_update: bool = False) -> Dict[str, Any]:
        print(f"Getting input for {model.__name__}")
        input_data: Dict[str, Any] = {}
        mapper = inspect(model)
        for attr_name, attr in mapper.column_attrs.items():
            print(f"Checking attribute: {attr_name}")
            if attr_name != 'id':
                if for_update:
                    update = self.user_input.get_string(f"Update {attr_name}? (yes/no): ")
                    if update.lower() != 'yes':
                        continue

                column = attr.columns[0]
                attr_type = column.type.python_type
                print(f"Attribute {attr_name} is of type {attr_type}")

                while True:
                    value: Any = None
                    if attr_type == int:
                        value = self.user_input.get_int(f"Enter {attr_name}: ")
                    elif attr_type == float:
                        value = self.user_input.get_float(f"Enter {attr_name}: ")
                    elif attr_type == str:
                        if isinstance(column.type, SQLAlchemyEnum):
                            enum_class = column.type.enum_class
                            print(f"Available options for {attr_name}:")
                            for enum_value in enum_class:
                                print(f"- {enum_value.name}")
                            value = self.user_input.get_string(f"Enter {attr_name} (one of the above options): ")
                            try:
                                value = enum_class[value.upper()]
                            except KeyError:
                                print(f"Invalid option for {attr_name}. Please try again.")
                                continue
                        else:
                            value = self.user_input.get_string(f"Enter {attr_name}: ")
                    elif attr_type == datetime.date:
                        while True:
                            try:
                                value = self.user_input.get_date(f"Enter {attr_name} (YYYY-MM-DD): ")
                                break
                            except ValueError:
                                print("Invalid date format. Please use YYYY-MM-DD.")
                    else:
                        print(f"Unsupported attribute type for {attr_name}. Skipping.")
                        break

                    print(f"Received value for {attr_name}: {value}")

                    if value == 'exit':
                        return {}

                    if value is not None and self.validate_input(model, attr_name, value):
                        input_data[attr_name] = value
                        break
                    else:
                        print(f"Invalid input for {attr_name}. Please try again.")

        print(f"Returning input data: {input_data}")
        return input_data

    @staticmethod
    def validate_input(model: Type[Base], attr: str, value: Any) -> bool:
        # TODO: Implement more robust validation logic
        if attr == 'name' and isinstance(value, str):
            return len(value) > 0
        elif attr in ['amount', 'balance'] and isinstance(value, (int, float)):
            return value >= 0
        elif attr == 'date' and isinstance(value, datetime.date):
            return value <= datetime.date.today()
        elif attr in ['type', 'interval'] and isinstance(value, enum.Enum):
            return True
        return True  # Default to True for unhandled cases

    @staticmethod
    def get_model_attributes(model: Type[Base]) -> List[str]:
        return [attr for attr in dir(model) if not attr.startswith('_') and attr != 'id' and not callable(getattr(model, attr))]

    @staticmethod
    def format_item(item: Base) -> str:
        attributes = inspect(item).attrs
        output = [f"ID: {item.id}"]

        for attr_name, attr in attributes.items():
            if attr_name not in ['metadata', 'registry']:
                value = getattr(item, attr_name)
                if isinstance(value, list):
                    if value:
                        output.append(f"{attr_name}: {len(value)} items")
                elif value is not None:
                    output.append(f"{attr_name}: {value}")

        return " | ".join(output)


if __name__ == "__main__":
    cli = CLI()
    cli.run()