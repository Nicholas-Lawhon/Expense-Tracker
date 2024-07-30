import pytest
from datetime import datetime
from expense_tracker.cli import UserInput
from expense_tracker.utils.input_helpers import EXIT_COMMANDS


class TestGetInt:
    """
    Tests for the get_int method of UserInput class.
    """

    @pytest.fixture
    def mock_print(self, mocker):
        return mocker.patch('builtins.print')

    def test_returns_integer_within_range(self, mocker):
        mocker.patch('builtins.input', return_value='5')
        result = UserInput.get_int("Enter a number: ", min_value=1, max_value=10)
        assert result == 5

    def test_returns_exit_on_exit_input(self, mocker):
        mocker.patch('builtins.input', return_value='exit')
        result = UserInput.get_int("Enter a number: ")
        assert result == 'exit'

    def test_returns_exit_on_quit_input(self, mocker):
        mocker.patch('builtins.input', return_value='quit')
        result = UserInput.get_int("Enter a number: ")
        assert result == 'exit'

    def test_returns_integer_no_range(self, mocker):
        mocker.patch('builtins.input', return_value='7')
        result = UserInput.get_int("Enter a number: ")
        assert result == 7

    def test_handles_non_integer_input(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['abc', '5'])
        result = UserInput.get_int("Enter a number: ")
        assert result == 5
        mock_print.assert_called_with(
            f"Invalid input. Please enter a valid number (integer) or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_handles_below_min_value(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['0', '5'])
        result = UserInput.get_int("Enter a number: ", min_value=1)
        assert result == 5
        mock_print.assert_called()

    def test_handles_above_max_value(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['11', '5'])
        result = UserInput.get_int("Enter a number: ", max_value=10)
        assert result == 5
        mock_print.assert_called()

    def test_handles_no_min_max_values(self, mocker):
        mocker.patch('builtins.input', return_value='5')
        result = UserInput.get_int("Enter a number: ")
        assert result == 5

    def test_handles_only_min_value_specified(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['0', '3'])
        result = UserInput.get_int("Enter a number: ", min_value=1)
        assert result == 3
        mock_print.assert_called()

    def test_handles_only_max_value_specified(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['11', '7'])
        result = UserInput.get_int("Enter a number: ", max_value=10)
        assert result == 7
        mock_print.assert_called()

    def test_handles_eoferror_during_input(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=[EOFError, '5'])
        result = UserInput.get_int("Enter a number:")
        assert result == 5
        mock_print.assert_called_with(
            f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_handles_keyboardinterrupt_during_input(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=[KeyboardInterrupt, '5'])
        result = UserInput.get_int("Enter a number:")
        assert result == 5
        mock_print.assert_called_with(
            f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_decimal_input(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['5.5', '5'])
        result = UserInput.get_int("Enter a number: ")
        assert result == 5
        mock_print.assert_called_with(
            f"Invalid input. Please enter a valid number (integer) or {' / '.join(EXIT_COMMANDS)} to quit.")


class TestGetFloat:
    """
    Tests for the get_float method of the UserInput class.
    """

    @pytest.fixture
    def mock_print(self, mocker):
        return mocker.patch('builtins.print')

    def test_valid_float_within_range(self, mocker):
        mocker.patch('builtins.input', return_value='50.5')
        result = UserInput.get_float("Enter a float: ", min_value=0.0, max_value=100.0)
        assert result == 50.5

    def test_valid_float_no_range(self, mocker):
        mocker.patch('builtins.input', return_value='25.75')
        result = UserInput.get_float("Enter a float: ")
        assert result == 25.75

    def test_exit_command(self, mocker):
        mocker.patch('builtins.input', return_value='exit')
        result = UserInput.get_float("Enter a float: ")
        assert result == 'exit'

    def test_quit_command(self, mocker):
        mocker.patch('builtins.input', return_value='quit')
        result = UserInput.get_float("Enter a float: ")
        assert result == 'exit'

    def test_float_at_min_boundary(self, mocker):
        mocker.patch('builtins.input', return_value='0.0')
        result = UserInput.get_float("Enter a float: ", min_value=0.0, max_value=100.0)
        assert result == 0.0

    def test_float_at_max_boundary(self, mocker):
        mocker.patch('builtins.input', return_value='100.0')
        result = UserInput.get_float("Enter a float: ", min_value=0.0, max_value=100.0)
        assert result == 100.0

    def test_float_below_min_boundary(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['-1.0', '50.0'])
        result = UserInput.get_float("Enter a float: ", min_value=0.0, max_value=100.0)
        assert result == 50.0
        mock_print.assert_called()

    def test_float_above_max_boundary(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['101.0', '50.0'])
        result = UserInput.get_float("Enter a float: ", min_value=0.0, max_value=100.0)
        assert result == 50.0
        mock_print.assert_called()

    def test_non_numeric_string(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['abc', '42.0'])
        result = UserInput.get_float("Enter a float: ")
        assert result == 42.0
        mock_print.assert_called_with(
            f"Invalid input. Please enter a valid number (float) or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_empty_string(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['', '42.0'])
        result = UserInput.get_float("Enter a float: ")
        assert result == 42.0
        mock_print.assert_called_with(
            f"Invalid input. Please enter a valid number (float) or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_float_with_spaces(self, mocker):
        mocker.patch('builtins.input', return_value=' 42.42 ')
        result = UserInput.get_float("Enter a float: ")
        assert result == 42.42

    def test_very_large_float(self, mocker):
        mocker.patch('builtins.input', return_value='1e308')
        result = UserInput.get_float("Enter a float: ")
        assert result == 1e308

    def test_very_small_float(self, mocker):
        mocker.patch('builtins.input', return_value='1e-308')
        result = UserInput.get_float("Enter a float: ")
        assert result == 1e-308

    def test_handles_eoferror_during_input(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=[EOFError, '5.0'])
        result = UserInput.get_float("Enter a float:")
        assert result == 5.0
        mock_print.assert_called_with(
            f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_handles_keyboardinterrupt_during_input(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=[KeyboardInterrupt, '5.0'])
        result = UserInput.get_float("Enter a float:")
        assert result == 5.0
        mock_print.assert_called_with(
            f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_integer_input(self, mocker):
        mocker.patch('builtins.input', return_value='5')
        result = UserInput.get_float("Enter a float: ")
        assert result == 5.0


class TestGetString:
    """
    Tests for the get_string method of the UserInput class.
    """

    @pytest.fixture
    def mock_print(self, mocker):
        return mocker.patch('builtins.print')

    def test_valid_string_within_length_range(self, mocker):
        mocker.patch('builtins.input', return_value='validstring')
        result = UserInput.get_string("Enter a string: ", min_length=3, max_length=20)
        assert result == 'validstring'

    def test_valid_string_without_length_constraints(self, mocker):
        mocker.patch('builtins.input', return_value='anystring')
        result = UserInput.get_string("Enter a string: ")
        assert result == 'anystring'

    def test_exit_command_terminates_input(self, mocker):
        mocker.patch('builtins.input', return_value='exit')
        result = UserInput.get_string("Enter a string: ")
        assert result == 'exit'

    def test_quit_command_terminates_input(self, mocker):
        mocker.patch('builtins.input', return_value='quit')
        result = UserInput.get_string("Enter a string: ")
        assert result == 'exit'

    def test_string_shorter_than_min_length(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['ab', 'validstring'])
        result = UserInput.get_string("Enter a string: ", min_length=3)
        assert result == 'validstring'
        mock_print.assert_called()

    def test_string_longer_than_max_length(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['toolongstring', 'valid'])
        result = UserInput.get_string("Enter a string: ", max_length=10)
        assert result == 'valid'
        mock_print.assert_called()

    def test_empty_string_no_constraints(self, mocker):
        mocker.patch('builtins.input', return_value='')
        result = UserInput.get_string("Enter a string: ")
        assert result == ''

    def test_string_at_min_length_boundary(self, mocker):
        mocker.patch('builtins.input', return_value='abc')
        result = UserInput.get_string("Enter a string: ", min_length=3)
        assert result == 'abc'

    def test_string_at_max_length_boundary(self, mocker):
        mocker.patch('builtins.input', return_value='abcdefghij')
        result = UserInput.get_string("Enter a string: ", max_length=10)
        assert result == 'abcdefghij'

    def test_string_with_leading_trailing_spaces(self, mocker):
        mocker.patch('builtins.input', return_value='  spaced  ')
        result = UserInput.get_string("Enter a string: ")
        assert result == 'spaced'

    def test_string_with_special_characters(self, mocker):
        mocker.patch('builtins.input', return_value='!@#$%^&*()')
        result = UserInput.get_string("Enter a string: ")
        assert result == '!@#$%^&*()'

    def test_string_with_numeric_characters(self, mocker):
        mocker.patch('builtins.input', return_value='1234567890')
        result = UserInput.get_string("Enter a string: ")
        assert result == '1234567890'

    def test_string_with_mixed_case_characters(self, mocker):
        mocker.patch('builtins.input', return_value='MiXeDcAsE')
        result = UserInput.get_string("Enter a string: ")
        assert result == 'MiXeDcAsE'

    def test_handles_eoferror_during_input(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=[EOFError, 'valid_string'])
        result = UserInput.get_string("Enter a string:")
        assert result == 'valid_string'
        mock_print.assert_called_with(
            f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_handles_keyboardinterrupt_during_input(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=[KeyboardInterrupt, 'valid_string'])
        result = UserInput.get_string("Enter a string:")
        assert result == 'valid_string'
        mock_print.assert_called_with(
            f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_whitespace_string_with_min_length(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['   ', 'valid'])
        result = UserInput.get_string("Enter a string: ", min_length=1)
        assert result == 'valid'
        mock_print.assert_called()

    def test_whitespace_string_without_length_constraints(self, mocker):
        mocker.patch('builtins.input', return_value='   ')
        result = UserInput.get_string("Enter a string: ")
        assert result == ''


class TestGetDate:
    """
    Tests for the get_date method of the UserInput class.
    """

    @pytest.fixture
    def mock_print(self, mocker):
        return mocker.patch('builtins.print')

    def test_valid_date_input(self, mocker):
        mocker.patch('builtins.input', return_value='2023-10-05')
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()

    def test_exit_command(self, mocker):
        mocker.patch('builtins.input', return_value='exit')
        result = UserInput.get_date("Enter date:")
        assert result == 'exit'

    def test_quit_command(self, mocker):
        mocker.patch('builtins.input', return_value='quit')
        result = UserInput.get_date("Enter date:")
        assert result == 'exit'

    def test_date_with_spaces(self, mocker):
        mocker.patch('builtins.input', return_value=' 2023-10-05 ')
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()

    def test_invalid_date_format(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['10-05-2023', '2023-10-05'])
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()
        mock_print.assert_called_with(
            f"Invalid date format. Please use YYYY-MM-DD or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_non_date_string(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['not-a-date', '2023-10-05'])
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()
        mock_print.assert_called_with(
            f"Invalid date format. Please use YYYY-MM-DD or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_empty_string(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['', '2023-10-05'])
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()
        mock_print.assert_called_with(
            f"Invalid date format. Please use YYYY-MM-DD or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_invalid_month_day_values(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['2023-13-01', '2023-10-05'])
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()
        mock_print.assert_called_with(
            f"Invalid date format. Please use YYYY-MM-DD or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_date_with_extra_characters(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['2023-10-05abc', '2023-10-05'])
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()
        mock_print.assert_called_with(
            f"Invalid date format. Please use YYYY-MM-DD or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_eof_error_interrupt(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=[EOFError, '2023-10-05'])
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()
        mock_print.assert_called_with(
            f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_keyboard_interrupt(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=[KeyboardInterrupt, '2023-10-05'])
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()
        mock_print.assert_called_with(
            f"\nInput interrupted. Please try again or type {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_different_locale_format(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['05-10-2023', '2023-10-05'])
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()
        mock_print.assert_called_with(
            f"Invalid date format. Please use YYYY-MM-DD or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_different_separator_format(self, mocker, mock_print):
        mocker.patch('builtins.input', side_effect=['2023/10/05', '2023-10-05'])
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2023, 10, 5).date()
        mock_print.assert_called_with(
            f"Invalid date format. Please use YYYY-MM-DD or {' / '.join(EXIT_COMMANDS)} to quit.")

    def test_leap_year_date(self, mocker):
        # Test for February 29 in a leap year (2024 is a leap year)
        mocker.patch('builtins.input', return_value='2024-02-29')
        result = UserInput.get_date("Enter date:")
        assert result == datetime(2024, 2, 29).date()
