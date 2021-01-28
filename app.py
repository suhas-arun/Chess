"""Flask webapp"""

from flask import Flask, render_template
from chess_engine import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"

app.debug = True

GAME = Game()
GAME.board.initialise_board()

@app.route("/")
def play():
    """2 player game"""
    return render_template("board.html", board=GAME.board.board)

if __name__ == "__main__":
    app.run(debug=True)

