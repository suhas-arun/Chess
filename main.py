"""Chess"""


class Board:
    """Represents the chess board."""

    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]

    def get_square(self, row, column):
        """
        Returns the piece object at a given index in the list.
        """
        return self.board[row][column]

    def print_board(self):
        """Prints the board list row by row, space-separated."""
        for row in self.board:
            print("\t".join([str(i) for i in row]))


class Piece:
    """
    Represents a general piece on the board. The value is defined by the
    type of piece: Pawn = 1, Bishop, Knight = 3, Rook = 5, Queen = 9.
    The colour attribute is a Boolean: True = white, False = black.
    """

    def __init__(self, row, column, value, colour):
        self.row = row
        self.column = column
        self.value = value
        self.colour = colour

    def get_value(self):
        """
        Returns the signed value of the piece. If the piece is white, then the
        value is positive. Otherwise it is negative.
        """
        return self.value if self.colour else self.value * -1

    def generate_moves(self):
        """
        Generates the moves that the piece can make. Implemented differently
        by each subclass. If the piece is white, it is moving upwards, else
        it is moving downwards on the board.
        """


class Game:
    """Controls the mechanisms of the game"""

    def __init__(self):
        self.board = Board()

    def input_move(self):
        """
        Takes input for a move. This is done by taking input for the current
        square that the piece to be moved is on, and the square where the piece
        is to be moved.
        """
        current_row, current_column = map(int, input("Piece (y x): ").split())
        new_row, new_column = map(int, input("Square (y x): ").split())

        return ((current_row, current_column), (new_row, new_column))

    def is_move_legal(self, current_square, new_square):
        """
        Checks if the move abides by the moving rules for that piece.
        """
        current_row, current_column = current_square
        piece = self.board.board[current_row][current_column]
        if piece is None:
            return False

        return new_square in piece.generate_moves()


class Pawn(Piece):
    """Piece with value 1."""

    def __init__(self, row, column, colour):
        super().__init__(row, column, 1, colour)
        self.has_moved = False
        self.direction = 1 if self.colour else -1

    def generate_moves(self):
        """
        Pawns can move 1 square forward and 2 squares forward if they have not
        yet moved.
        """
        moves = []

        moves.append((self.row - self.direction, self.column))
        if not self.has_moved:
            moves.append((self.row - 2 * self.direction, self.column))

        return moves

    def get_attacked_squares(self):
        """
        Pawns can move 1 square forward diagonally when they take an opponent's
        piece.
        """
        moves = [
            (self.row - self.direction, self.column - 1),
            (self.row - self.direction, self.column + 1),
        ]
        return moves

    def __str__(self):
        output = "P"
        if not self.colour:
            output += "'"
        return output


class Bishop(Piece):
    """Piece with value 3"""

    def __init__(self, row, column, colour):
        super().__init__(row, column, 3, colour)

    def generate_moves(self):
        """
        Bishops can move diagonally any number of spaces.
        """
        moves = []

        # Top right diagonal
        moves += list(zip(range(self.row - 1, -1, -1), range(self.column + 1, 8)))

        # Top left diagonal
        moves += list(zip(range(self.row - 1, -1, -1), range(self.column - 1, -1, -1)))

        # Bottom right diagonal
        moves += list(zip(range(self.row + 1, 8), range(self.column + 1, 8)))

        # Bottom left diagonal
        moves += list(zip(range(self.row + 1, 8), range(self.column - 1, -1, -1)))

        return moves

    def __str__(self):
        output = "B"
        if not self.colour:
            output += "'"
        return output


class Knight(Piece):
    """Piece with value 3"""

    def __init__(self, row, column, colour):
        super().__init__(row, column, 3, colour)

    def generate_moves(self):
        """Knights move in an L shape."""
        relative_moves = [
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
        ]
        moves = []

        for vertical_shift, horizontal_shift in relative_moves:
            new_row = self.row + vertical_shift
            new_column = self.column + horizontal_shift
            if 0 <= new_row < 8 and 0 <= new_column < 8:
                moves.append((new_row, new_column))

        return moves

    def __str__(self):
        output = "N"
        if not self.colour:
            output += "'"
        return output


class Rook(Piece):
    """Piece with value 5"""

    def __init__(self, row, column, colour):
        super().__init__(row, column, 5, colour)
        self.has_moved = False

    def generate_moves(self):
        """Rooks move up and down their column and row"""
        moves = []

        # Squares on the same row
        columns = list(range(8))
        columns.pop(self.column)
        moves += [(self.row, i) for i in columns]

        # Squares on the same column
        rows = list(range(8))
        rows.pop(self.row)
        moves += [(i, self.column) for i in rows]

        return moves

    def __str__(self):
        output = "R"
        if not self.colour:
            output += "'"
        return output


class Queen(Piece):
    """Piece with value 9"""

    def __init__(self, row, column, colour):
        super().__init__(row, column, 9, colour)

    def generate_moves(self):
        """Queens can move diagonally or in straight lines."""
        moves = []

        # Top right diagonal
        moves += list(zip(range(self.row - 1, -1, -1), range(self.column + 1, 8)))

        # Top left diagonal
        moves += list(zip(range(self.row - 1, -1, -1), range(self.column - 1, -1, -1)))

        # Bottom right diagonal
        moves += list(zip(range(self.row + 1, 8), range(self.column + 1, 8)))

        # Bottom left diagonal
        moves += list(zip(range(self.row + 1, 8), range(self.column - 1, -1, -1)))

        # Squares on the same row
        columns = list(range(8))
        columns.pop(self.column)
        moves += [(self.row, i) for i in columns]

        # Squares on the same column
        rows = list(range(8))
        rows.pop(self.row)
        moves += [(i, self.column) for i in rows]

        return moves

    def __str__(self):
        output = "Q"
        if not self.colour:
            output += "'"
        return output


class King(Piece):
    """
    Piece initialised with value 10000. If this piece is attacked and it has no
    legal moves, the game is over.
    """

    def __init__(self, row, column, colour):
        super().__init__(row, column, 10000, colour)
        self.has_moved = False

    def generate_moves(self):
        """Kings can move one square in any direction."""
        relative_moves = [
            (1, 1),
            (1, 0),
            (1, -1),
            (0, 1),
            (0, -1),
            (-1, 1),
            (-1, 0),
            (-1, -1),
        ]
        moves = []

        for vertical_shift, horizontal_shift in relative_moves:
            new_row = self.row + vertical_shift
            new_column = self.column + horizontal_shift
            if 0 <= new_row < 8 and 0 <= new_column < 8:
                moves.append((new_row, new_column))

        return moves

    def __str__(self):
        output = "K"
        if not self.colour:
            output += "'"
        return output


game = Game()
game.input_move()
game.board.print_board()
# game.board.board[2][1] = Queen(2, 1, True)
# print(game.is_move_legal((2, 1), (2, 6)))
# print(game.is_move_legal((2, 1), (3, 6)))
# print(game.is_move_legal((2, 1), (7, 1)))
# print(game.is_move_legal((2, 1), (7, 2)))
# print(game.is_move_legal((3, 1), (7, 2)))
