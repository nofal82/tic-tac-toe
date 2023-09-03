from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_database
import sqlite3
import re
from flask_login import current_user, login_required, LoginManager, login_user, logout_user, UserMixin
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired, Email
from flask_wtf import FlaskForm
from validate_email_address import validate_email


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "123"
# Create the database tables
create_database()
# Initialize mail
mail = Mail(app)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config["MAIL_USERNAME"] = 'tshn44@gmail.com'
app.config["MAIL_PASSWORD"] = 'fkfdqsvitzuwcjqu'
mail = Mail(app)
# Initialize the game board
s = URLSafeTimedSerializer('123')
def initialize_board():
    return [[" " for _ in range(3)] for _ in range(3)]
current_player = "X"


@app.route("/")
def index():
    message = None
    if 'board' not in session or 'current_player' not in session:
        if current_user.is_authenticated:
            print("Is authenticated:", current_user.is_authenticated)
            session['board'] = initialize_board()
            session['current_player'] = "X"
        else:
            message = "You need to log in or play as guest to initialize the game."

    board = session.get("board") or initialize_board()
    current_player = session.get("current_player", "X")
    played_as_guest = session.get("played_as_guest", not current_user.is_authenticated)
    session["played_as_guest"] = played_as_guest  # Store the value in the session
    return render_template("index.html", board=board, current_player=current_player, winner=session.get("winner"), played_as_guest=played_as_guest, message=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Validate email
        is_valid = validate_email(email)
        
        # Validate password complexity (at least 8 characters, at least one uppercase, one lowercase, one number)
        password_valid = re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$', password)
        
        if not is_valid:
            flash('Invalid email format.')
            return redirect(url_for('register'))

        if not password_valid:
            flash('Password must be at least 8 characters, with at least one uppercase, one lowercase, and one number.')
            return redirect(url_for('register'))
        # Hash the password before storing
        hashed_password = generate_password_hash(password, method='sha256')
        print(hashed_password)
        conn = sqlite3.connect('game_database.db')
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
            conn.commit()
            flash('Registration successful! Please check your email for confirmation.')
        except sqlite3.IntegrityError:
            flash('Email already registered.')

        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    # Implement a method to load a user by ID
    @staticmethod
    def load_user(user_id):
        conn = sqlite3.connect('game_database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            user = User(user_data[0])  # Create a User instance with the user ID
            conn.close()
            return user

        conn.close()
        return None  # User not found

'''
PasswordResetRequestForm: This form class is designed to capture the email address of a user who has forgotten their password and wishes to reset it. The form contains:

An "email" field, which is a text input field that requires the user to enter a valid email address.
A "submit" button to send the reset request.
PasswordResetForm: This form class is designed for the actual password reset process. It captures a new password and its confirmation. The form contains:

A "password" field, which is a password input field that requires the user to enter a new password. It also requires that this password matches the "confirm" password.
A "confirm" field, which is another password input field where the user is expected to repeat the new password for verification.
Both forms use validators to enforce certain conditions.
For example, DataRequired() ensures that a field is not submitted empty,
Email() checks that the input is a valid email address, and EqualTo() confirms that two fields have the same value.

'''



# Define a class for the password reset request form
class PasswordResetRequestForm(FlaskForm):
    # Define an 'email' field that must be filled out, and must be a valid email address.
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Define a submit button labeled 'Request Password Reset'.
    submit = SubmitField('Request Password Reset')

# Define a class for the password reset form
class PasswordResetForm(FlaskForm):
    # Define a 'password' field that must be filled out.
    # It must also match the 'confirm' field.
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    # Define a 'confirm' field for the user to repeat the new password.
    # Note: No validators are directly attached to this field because
    # it's checked through the 'EqualTo' validator in the 'password' field.
    confirm = PasswordField('Repeat Password')


@login_manager.user_loader
def load_user(user_id):
    return User.load_user(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('game_database.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        if user is None:
            flash('Invalid email or password.')
        elif not check_password_hash(user[2], password):
            flash('Invalid email or password.')
        else:
            # Login the user
            user_id = user[0]
            login_user(User(user_id))  # Create a User instance and log in
            flash('You have been logged in successfully.')
            # Clear the played_as_guest session variable
            session.pop('played_as_guest', None)
            session["played_as_guest"] = False

            return redirect(url_for('index'))

    return render_template('login.html')


@app.route("/logout", methods=['POST'])
def logout():
    logout_user()
    session.pop('played_as_guest', None)
    session.pop('current_player', None)
    session.pop('winner', None)
    session.pop('played_as_guest', None)
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('index'))


@app.route("/move/<int:row>/<int:col>", methods=["POST"])
def make_move(row, col):
    global current_player
    # Check if there's game state stored in the session
    if "board" not in session:
        session["board"] = initialize_board()  # Initialize a new game board
        session["current_player"] = "X"  # Start with player X
        session["winner"] = None  # No winner yet
    
    board = session["board"]
    current_player = session["current_player"]
   
    # Check for play mode
    play_mode = session.get('play_mode', 'human')
    print("Play mode: ", session.get('play_mode'))

    # Validate move and update the board
    if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == " ":
        board[row][col] = current_player
        winner = check_winner(board, current_player)
        if winner:
            session["winner"] = current_player
            session["current_player"] = None   # Set current_player session to None to indicate that the game is over
        elif is_board_full(board):
            current_player = None  # Set current_player to None for a draw
        else:
            # If it's a human vs. computer game, the computer makes the next move
            if play_mode == 'computer':
                computer_row, computer_col = best_move(board)
                
                if computer_row is not None and computer_col is not None:
                    board[computer_row][computer_col] = "O"
                    winner = check_winner(board, "O")

                    if winner:
                        session["winner"] = "O"
                        session["current_player"] = None
                    else:
                        session["current_player"] = "X"  # Switch back to human player

            # If it's a human vs. human game, switch the current player
            else:
                session["current_player"] = "O" if current_player == "X" else "X"
    # Update session data and redirect
    session["board"] = board
    session.modified = True

    return redirect(url_for("index"))


@app.route('/set_play_mode', methods=['POST'])
def set_play_mode():
    # play mode could be 'human' or 'computer'
    play_mode = request.form.get('play_mode', 'human')
    session['play_mode'] = play_mode
    return redirect(url_for('index'))


@app.route('/reset_token/<token>', methods=['GET', 'POST'])
def reset_token(token):
    try:
        # Try to decrypt the token
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except (SignatureExpired, BadTimeSignature):
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('login'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        # Here you need to fetch the user's record from the database by email
        conn = sqlite3.connect('game_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if user:
            # Hash the new password and store it in the database
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed_password, email))
            conn.commit()
            conn.close()
            
            flash('Your password has been reset!', 'success')
            return redirect(url_for('login'))

    return render_template('reset_token.html', form=form)


def get_db():
    db = sqlite3.connect('game_database.db')
    db.row_factory = sqlite3.Row
    return db


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        db.close()

        if user is None:
            flash('This email is not registered with us.')
            return redirect(url_for('forgot'))
        else:
            token = s.dumps(email, salt='email-confirm')
            
            msg = Message('Password Reset Request', sender='noreply@yourdomain.com', recipients=[email])
            link = url_for('reset_token', token=token, _external=True)
            msg.body = f'Your password reset link is {link}'
            
            mail.send(msg)
            
            flash('Password reset email has been sent.')
            return redirect(url_for('login'))
    return render_template('forgot.html')


def get_winner(board):
    # Check rows, columns, and diagonals for a win
    for player in ["X", "O"]:
        for i in range(3):
            if all([board[i][j] == player for j in range(3)]) or \
               all([board[j][i] == player for j in range(3)]) or \
               all([board[i][i] == player for i in range(3)]) or \
               all([board[i][2 - i] == player for i in range(3)]):
                return player
    return None


def minimax(board, depth, maximizing):
    # Define the scores for each endgame situation
    scores = {'X': 1, 'O': -1, 'tie': 0}

    # Determine if there is a winner
    winner = get_winner(board)

    # If we have a winner, return the corresponding score
    if winner is not None:
        return scores[winner]

    # Maximizing player logic (player 'X')
    if maximizing:
        # Initialize max_eval as negative infinity, so any score will be higher
        max_eval = float('-inf')

        # Loop through all board positions
        for i in range(3):
            for j in range(3):
                # Check for an empty cell
                if board[i][j] == ' ':
                    # Make a move for maximizing player 'X'
                    board[i][j] = 'X'
                    
                    # Recursively apply minimax and get the evaluation score
                    evaluation = minimax(board, depth + 1, False)
                    
                    # Undo the move
                    board[i][j] = ' '
                    
                    # Update max_eval if the returned evaluation is higher
                    max_eval = max(evaluation, max_eval)
                    
        # Return the maximum evaluation found
        return max_eval

    # Minimizing player logic (player 'O')
    else:
        # Initialize min_eval as positive infinity, so any score will be lower
        min_eval = float('inf')
        
        # Loop through all board positions
        for i in range(3):
            for j in range(3):
                # Check for an empty cell
                if board[i][j] == ' ':
                    # Make a move for minimizing player 'O'
                    board[i][j] = 'O'
                    
                    # Recursively apply minimax and get the evaluation score
                    evaluation = minimax(board, depth + 1, True)
                    
                    # Undo the move
                    board[i][j] = ' '
                    
                    # Update min_eval if the returned evaluation is lower
                    min_eval = min(evaluation, min_eval)
                    
        # Return the minimum evaluation found
        return min_eval


def best_move(board):
    # Initialize the maximum evaluation to negative infinity.
    # We will update this value whenever we find a better move.
    max_eval = float('-inf')

    # Initialize 'move' to None. This will store the row, col tuple for the best move found.
    move = None

    # Loop through every cell on the board to check if it's an empty cell (' ').
    for i in range(3):
        for j in range(3):
            # If we find an empty cell, we consider it as a potential move.
            if board[i][j] == ' ':
                # Make a move for 'X' in the empty cell.
                board[i][j] = 'X'
                
                # Use the minimax function to evaluate the board state after this move.
                # We use depth = 0 and maximizing = False because 'X' has just moved, so it's 'O's turn.
                evaluation = minimax(board, 0, False)

                # Undo the move to restore the original board state.
                board[i][j] = ' '

                # If this move results in a better evaluation, update max_eval and store this move as the best.
                if evaluation > max_eval:
                    max_eval = evaluation
                    move = (i, j)

    # Return the best move found.
    return move


def store_gameplay_data(user_id, winner):
    conn = sqlite3.connect('game_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO gameplay_data (user_id, winner) VALUES (?, ?)', (user_id, winner))
        conn.commit()
    except sqlite3.Error as e:
        print("An error occurred:", e)

    conn.close()


def check_winner(board, player):
    # Check rows, columns, and diagonals for a win
    for i in range(3):
        if all([board[i][j] == player for j in range(3)]):
            return True
        if all([board[j][i] == player for j in range(3)]):
            return True
    if all([board[i][i] == player for i in range(3)]) or all([board[i][2 - i] == player for i in range(3)]):
        return True
    return False


@app.route("/reset", methods=["POST"])
def reset_game():
    session["board"] = initialize_board()  # Initialize a new game board
    session["current_player"] = "X"  # Start with player X
    session["winner"] = None  # No winner yet
    session.modified = True
    return redirect(url_for("index"))


def is_board_full(board):
    return all([cell != " " for row in board for cell in row])


if __name__ == "__main__":
    app.run(debug=True)