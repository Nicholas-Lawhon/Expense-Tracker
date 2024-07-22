def check_number_range(
    value: int | float,
    min_value: int | float | None = None,
    max_value: int | float | None = None
) -> bool:
    """
    Checks if a number (either int or float) is within a specified range.
    Handles cases where min_value or max_value might not be provided.

    Args:
        value (int | float): The number to check.
        min_value (int | float | None): The minimum value of the range, or None.
        max_value (int | float | None): The maximum value of the range, or None.

    Returns:
        bool: True if the number is within the range, False otherwise.
    """
    if min_value is not None and max_value is not None:
        return min_value <= value <= max_value
    elif min_value is not None:
        return min_value <= value
    elif max_value is not None:
        return value <= max_value
    else:
        # If neither min_value nor max_value is provided, default to True.
        return True


def check_string_length(
    value: str,
    min_value: int | None = None,
    max_value: int | None = None
) -> bool:
    """
    Checks if a string's length is within a specified range.
    Handles cases where min_value or max_value might not be provided.

    Args:
        value (str): The string to check.
        min_value (int | None): The minimum length of the string, or None.
        max_value (int | None): The maximum length of the string, or None.

    Returns:
        bool: True if the string's length is within the range, False otherwise.
    """
    if min_value is not None and max_value is not None:
        return min_value <= len(value) <= max_value
    elif min_value is not None:
        return min_value <= len(value)
    elif max_value is not None:
        return len(value) <= max_value
    else:
        # If neither min_value nor max_value is provided, default to True.
        return True


def user_validation_message(
    value: int | float | str,
    min_value: int | float | None = None,
    max_value: int | float | None = None
) -> str:
    """
    Checks if a value is within a specified range and returns a message based on the result.

    Args:
        value (int | float | str): The value to check.
        min_value (int | float | None): The minimum value of the range, or None.
        max_value (int | float | None): The maximum value of the range, or None.

    Returns:
        str: The message to display, based on the results of the check.
    """
    base_message = "Please enter a"
    if isinstance(value, str):
        base_message += " string with a length"
        comparison_value = len(value)
    else:
        base_message += " value"
        comparison_value = value

    if min_value is not None and max_value is not None:
        if not (min_value <= comparison_value <= max_value):
            return f"{base_message} between {min_value} and {max_value}."
    elif min_value is not None:
        if not (min_value <= comparison_value):
            return f"{base_message} greater than or equal to {min_value}."
    elif max_value is not None:
        if not (comparison_value <= max_value):
            return f"{base_message} less than or equal to {max_value}."

    return "The input does not meet the validation criteria."
