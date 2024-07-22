EXIT_COMMANDS = ('exit', 'quit')


def is_exit_command(value: str) -> bool:
    """
    Checks if the user entered an exit command.

    Returns True if an exit command was entered, otherwise False.
    """
    return value.lower() in EXIT_COMMANDS
