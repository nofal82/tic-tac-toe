from project import validate_email  # Import the function
from project import check_winner  # Import the function
import re  # Import the regex module

# Testing Email Validation
def test_validate_email():
    assert validate_email("test@email.com") == True
    assert validate_email("invalid-email") == False
    assert validate_email("another.test@email.com") == True
    assert validate_email("") == False

# Testing Password Complexity directly with Regex
def test_validate_password():
    assert re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$', "Password123") is not None
    assert re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$', "Password") is None
    assert re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$', "pass") is None
    assert re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$', "PASS123") is None
    assert re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$', "") is None


def test_check_winner():
    # Test a winning row for player 'X'
    board = [
        ['X', 'X', 'X'],
        [' ', ' ', ' '],
        [' ', ' ', ' ']
    ]
    assert check_winner(board, 'X') == True

    # Test a non-winning board for player 'X'
    board = [
        ['X', ' ', ' '],
        [' ', 'X', ' '],
        [' ', ' ', 'X']
    ]
    assert check_winner(board, 'O') == False

    # Test a winning column for player 'O'
    board = [
        [' ', 'O', ' '],
        [' ', 'O', ' '],
        [' ', 'O', ' ']
    ]
    assert check_winner(board, 'O') == True

    # Test a winning diagonal for player 'X'
    board = [
        ['X', ' ', ' '],
        [' ', 'X', ' '],
        [' ', ' ', 'X']
    ]
    assert check_winner(board, 'X') == True

    # Test another winning diagonal for player 'X'
    board = [
        [' ', ' ', 'X'],
        [' ', 'X', ' '],
        ['X', ' ', ' ']
    ]
    assert check_winner(board, 'X') == True