# Tic-Tac-Toe Web Application

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [License](#license)

## Introduction
This is a web-based Tic-Tac-Toe game that supports both single-player and multiplayer modes. Built using Python's Flask framework, it provides a user-friendly interface, email-based authentication, and secure data storage.

## Features
- **Multiplayer Mode**: Play against your friends.
- **Single-Player Mode**: Play against a computer.
- **User Authentication**: Secure login and registration system.
- **Game Stats**: Keep track of your scores.
- **Forgot Password**: Reset your password via email.

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/nofal82/tic-tac-toe.git
    ```

2. Navigate to the project directory:
    ```bash
    cd tic-tac-toe
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask application:
    ```bash
    flask run
    ```

5. Open your web browser and go to `http://localhost:5000/`.

## Usage
- **Register or Log In**: To play the game, you'll need to register or log in first.
- **Choose Play Mode**: After logging in, you can choose either to play against another human or against the computer.
- **Make Your Move**: Click on an empty cell to place your marker ('X' or 'O').
- **Win**: Complete a row, column, or diagonal with your marker to win.

## Testing
Testing is done using pytest. To run the tests, navigate to the project directory and execute the following command:

```bash
pytest
