"""Flask webapp"""

from flask import Flask, render_template, request, redirect
from chess_engine import Game

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"

app.debug = True

GAME = Game()
GAME.board.initialise_board()
current_move: list = []
white_pawn = GAME.board.board[6][4]


@app.route("/")
def play():
    """2 player game"""
    return render_template(
        "board.html", board=GAME.board.board, current_move=current_move
    )


@app.route("/move", methods=["GET", "POST"])
def move():
    """
    When a square on the board is clicked, a post request is made, returning
    the row and column of the square that was clicked. After a second square
    is clicked
    """
    column = int(request.args.get("column")) - 1
    row = int(request.args.get("row")) - 1
    new_square = (row, column)

    if len(current_move) == 1:  # The piece is being moved to the new square
        current_square = current_move[0]
        if GAME.validate_move(current_square, new_square):
            GAME.execute_move(current_square, new_square)
            GAME.is_checkmate_or_stalemate()

            current_move.append(new_square)
            print(white_pawn.en_passant_possible)
        else:
            del current_move[:]
            if GAME.board.board[row][column]:
                current_move.append(new_square)

    else:  # The piece to be moved is on the new square
        del current_move[:]
        current_move.append(new_square)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
