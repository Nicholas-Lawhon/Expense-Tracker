from typing import List, Dict, Any, Union, Type
from datetime import datetime
import enum
from sqlalchemy import inspect, Enum as SQLAlchemyEnum
from sqlalchemy.orm import sessionmaker, Mapped
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound

from expense_tracker.db.operations import BaseOperations
from expense_tracker.db.models import Account, Transaction, Category, Budget, RecurringExpense, Base, IntervalType, TransactionType
from expense_tracker.db.connection import get_db_engine, get_db_session
from expense_tracker.utils.validation import check_number_range, check_string_length, user_validation_message
from expense_tracker.utils.input_helpers import (
    UserInput, is_exit_command, EXIT_COMMANDS, display_model_instances,
    get_model_instance_id, get_related_instance_id, get_enum_value,
    validate_string, validate_number, validate_date, validate_enum
)
from expense_tracker.utils.logger import setup_logger


logger = setup_logger('cli', 'cli.log')


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


class CLI:
    def __init__(self):
        self.menu_display = MenuDisplay()
        self.user_input = UserInput()
        self.engine = get_db_engine()
        self.get_session = get_db_session

    def run(self) -> None:
        while True:
            try:
                self.menu_display.show_main_menu()
                choice = self.user_input.get_int("Enter your choice: ", min_value=0, max_value=5)

                if choice == 0 or is_exit_command(str(choice)):
                    print("Exiting the application. Goodbye!")
                    break

                self.process_main_menu_choice(choice)
            except Exception as e:
                logger.error(f"An error occurred in the main loop: {str(e)}")
                print("An unexpected error occurred. Please try again")

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
        attributes = self.get_model_input(model)
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
        input_data = {}
        mapper = inspect(model)

        for attr_name, attr in mapper.column_attrs.items():
            if attr_name == 'id':
                continue

            if for_update:
                update = self.user_input.get_string(f"Update {attr_name}? (yes/no): ")
                if update.lower() != 'yes':
                    continue

            column = attr.columns[0]
            value = self.get_attribute_value(model, attr_name, column)

            if value == 'exit':
                return {}

            if value is not None:
                if self.validate_input(model, attr_name, value):
                    input_data[attr_name] = value
            else:
                print(f"Invalid input for {attr_name}. Please try again.")
                continue

        return input_data

    def validate_input(self, model: Type[Base], attr: str, value: Any) -> bool:
        try:
            if attr == 'name':
                return validate_string(value)
            elif attr in ['amount', 'balance']:
                return validate_number(value)
            elif attr == 'date':
                return validate_date(value)
            elif attr in ['type', 'interval']:
                return validate_enum(value)
            else:
                # For attributes we don't have specific validation for, we'll consider them valid
                return True
        except Exception as e:
            logger.error(f"Error validating {attr}: {str(e)}")
            return False

    def get_attribute_value(self, model: Type[Base], attr_name: str, column: Any) -> Any:
        try:
            if column.foreign_keys:
                return self.handle_foreign_key(column)
            elif isinstance(column.type, SQLAlchemyEnum):
                return self.handle_enum(column.type.enum_class, attr_name)
            else:
                return self.handle_basic_type(attr_name, column.type.python_type)
        except Exception as e:
            logger.error(f"Error getting attribute value for {attr_name}: {str(e)}")
            return None

    def handle_foreign_key(self, column: Any) -> Any:
        related_model = list(column.foreign_keys)[0].column.table
        with self.get_session() as session:
            return get_related_instance_id(session, related_model)

    def handle_enum(self, enum_class: Type[enum.Enum], attr_name: str) -> Any:
        return get_enum_value(enum_class, f"Enter {attr_name} (one of the above options): ")

    def handle_basic_type(self, attr_name: str, attr_type: Type) -> Any:
        if attr_type == int:
            return self.user_input.get_int(f"Enter {attr_name}: ")
        elif attr_type == float:
            return self.user_input.get_float(f"Enter {attr_name}: ")
        elif attr_type == str:
            return self.user_input.get_string(f"Enter {attr_name}: ")
        elif attr_type == datetime.date:
            return self.user_input.get_date(f"Enter {attr_name} (YYYY-MM-DD): ")
        else:
            logger.warning(f"Unsupported attribute type for {attr_name}. Skipping.")
            print(f"Unsupported attribute type for {attr_name}. Skipping.")
            return None

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
