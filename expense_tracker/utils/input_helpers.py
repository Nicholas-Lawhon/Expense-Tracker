from typing import List, Tuple, Type, Any, Union
from datetime import datetime
import enum
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from expense_tracker.models import Base
from expense_tracker.db.operations import BaseOperations
from expense_tracker.utils.validation import check_number_range, check_string_length, user_validation_message

EXIT_COMMANDS = ('exit', 'quit')


def is_exit_command(value: str) -> bool:
    """
    Checks if the user entered an exit command.

    Returns True if an exit command was entered, otherwise False.
    """
    return value.lower() in EXIT_COMMANDS


def validate_string(value: str, min_length: int = 1) -> bool:
    return len(value) >= min_length


def validate_number(value: float, min_value: float = 0) -> bool:
    return value >= min_value


def validate_date(value: datetime.date) -> bool:
    try:
        datetime.strptime(str(value), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_enum(value: enum.Enum) -> bool:
    return isinstance(value, enum.Enum)


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
                if (min_value is not None or max_value is not None) and not check_number_range(int_value, min_value,
                                                                                               max_value):
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
                if (min_value is not None or max_value is not None) and not check_number_range(float_value, min_value,
                                                                                               max_value):
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

                if (min_length is not None or max_length is not None) and not check_string_length(value, min_length,
                                                                                                  max_length):
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
                return datetime.strptime(str(date_string), "%Y-%m-%d").date()
            except ValueError:
                print(f"Invalid date format. Please use YYYY-MM-DD or {' / '.join(EXIT_COMMANDS)} to quit.")
            except (EOFError, KeyboardInterrupt):
                print(f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")


def display_model_instances(session: Session, model: Type[Base]) -> bool:
    instances, total = BaseOperations.get_all(session, model)
    if total == 0:
        print(f"\nNo {model.__name__} instances available. Please create one first.")
        return False

    print(f"\nAvailable {model.__name__} instances:")
    for instance in instances:
        print(f"ID: {instance.id} - Name: {instance.name}")

    print()
    return True


def get_model_instance_id(session: Session, model: Type[Base], prompt: str) -> Union[int, str]:
    while True:
        instance_id = UserInput.get_int(prompt)
        if instance_id == 'exit':
            return 'exit'

        instance = BaseOperations.read(session, model, instance_id)
        if instance:
            return instance_id
        print(f"Invalid {model.__name__} ID. Please try again.")


def get_related_instance_id(session: Session, model: Type[Base]) -> Union[int, str]:
    if not display_model_instances(session, model):
        return None
    return get_model_instance_id(session, model, f"Enter the ID of the {model.__name__}: ")


def get_enum_value(enum_class: Type[enum.Enum], prompt: str) -> Any:
    print(f"Available options for {enum_class.__name__}:")
    for i, enum_value in enumerate(enum_class, 1):
        print(f"{i}. {enum_value.name}")

    while True:
        choice = UserInput.get_int(prompt, min_value=1, max_value=len(enum_class))
        if is_exit_command(str(choice)):
            return 'exit'
        try:
            return list(enum_class)[choice - 1]
        except IndexError:
            print(f"Invalid choice. Please enter a number between 1 and {len(enum_class)}")
