"""Chess"""


class Board:
    """Represents the chess board."""

    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.ranks = ["a", "b", "c", "d", "e", "f", "g", "h"]
        self.white_pieces = [
            Rook(7, 0, True),
            Rook(7, 7, True),
            Knight(7, 1, True),
            Knight(7, 6, True),
            Bishop(7, 2, True),
            Bishop(7, 5, True),
            Queen(7, 3, True),
            King(7, 4, True),
        ] + [Pawn(6, column, True) for column in range(8)]

        self.black_pieces = [
            Rook(0, 0, False),
            Rook(0, 7, False),
            Knight(0, 1, False),
            Knight(0, 6, False),
            Bishop(0, 2, False),
            Bishop(0, 5, False),
            Queen(0, 3, False),
            King(0, 4, False),
        ] + [Pawn(1, column, False) for column in range(8)]

    def get_square(self, row, column):
        """
        Returns the piece object at a given index in the list.
        """
        return self.board[row][column]

    def print_board(self):
        """Prints the board list row by row, space-separated."""
        print("\t".join(self.ranks) + "\n")
        for row_number, row in enumerate(self.board):
            print("\t".join([str(i) for i in row]) + f"\t{8 - row_number}")

    def initialise_board(self):
        """Initialises the board list with the pieces in their places"""
        for piece in self.white_pieces + self.black_pieces:
            self.board[piece.row][piece.column] = piece


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

    def __repr__(self):
        return str(self)


class Game:
    """Controls the mechanisms of the game"""

    def __init__(self):
        self.board = Board()
        self.current_player_colour = True
        self.white_check = False
        self.black_check = False
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)

    def play(self):
        """Controls the overall mechanism of playing the game"""
        self.board.print_board()
        print("\nWhite:" if self.current_player_colour else "\nBlack:")
        move = self.input_move()
        while move != "Quit":
            current_square, new_square = move
            if self.validate_move(
                current_square, new_square
            ) and not self.is_move_blocked(current_square, new_square):
                self.execute_move(current_square, new_square)
                print()
                self.board.print_board()
            else:
                print("Not legal")

            print("\nWhite:" if self.current_player_colour else "\nBlack:")
            move = self.input_move()

    def input_move(self):
        """
        Takes input for a move. This is done by taking input for the current
        square that the piece to be moved is on, and the square where the piece
        is to be moved.
        """
        current_column, current_row = list(input("Piece (xy): "))
        new_column, new_row = list(input("Square (x y): "))

        current_column = self.board.ranks.index(current_column)
        new_column = self.board.ranks.index(new_column)

        return ((8 - int(current_row), current_column), (8 - int(new_row), new_column))

    def validate_move(self, current_square, new_square):
        """
        Validates a move by checking if the piece is allowed to move to the new
        square and if the new square does not have another piece of the same
        colour.
        """
        current_row, current_column = current_square
        new_row, new_column = new_square

        current_piece = self.board.board[current_row][current_column]
        piece_at_new_square = self.board.board[new_row][new_column]

        if not self.is_move_legal(current_square, new_square):
            return False

        if piece_at_new_square is not None:
            if current_piece.colour == piece_at_new_square.colour:
                return False

        self.is_king_in_check()
        valid = True

        self.board.board[current_row][current_column] = None
        self.board.board[new_row][new_column] = current_piece

        if self.current_player_colour:  # The current player is white
            if isinstance(current_piece, King):
                self.white_king_location = (new_row, new_column)

            self.is_king_in_check()
            if self.white_check:
                valid = False

            if isinstance(current_piece, King):
                self.white_king_location = (current_row, current_column)

        else:
            if isinstance(current_piece, King):
                self.black_king_location = (new_row, new_column)

            self.is_king_in_check()
            if self.black_check:
                valid = False

            if isinstance(current_piece, King):
                self.black_king_location = (current_row, current_column)

        self.board.board[current_row][current_column] = current_piece
        self.board.board[new_row][new_column] = piece_at_new_square

        return valid

    def is_move_legal(self, current_square, new_square):
        """
        Checks if the move abides by the moving rules for that piece.
        """
        current_row, current_column = current_square
        new_row, new_column = new_square
        piece = self.board.board[current_row][current_column]
        if piece is None or piece.colour != self.current_player_colour:
            return False

        if isinstance(piece, Pawn):
            piece_at_square = self.board.board[new_row][new_column]
            if piece_at_square and piece_at_square.colour != self.current_player_colour:
                return new_square in piece.get_attacked_squares()

        return new_square in piece.generate_moves()

    def is_move_blocked(self, current_square, new_square):
        """
        Checks if a move is blocked by another piece. This only applies to
        pawns, bishops, rooks and queens.
        """
        current_row, current_column = current_square
        piece = self.board.board[current_row][current_column]

        if isinstance(piece, (King, Knight)):
            return False

        squares_passed = self.get_passed_squares(current_square, new_square)
        return any(
            [self.board.board[square[0]][square[1]] for square in squares_passed]
        )

    def get_passed_squares(self, current_square, new_square):
        """Returns the squares which a piece moves over when a move is made."""

        current_row, current_column = current_square
        new_row, new_column = new_square
        squares = []

        if new_column > current_column:
            if new_row > current_row:  # bottom right diagonal
                squares = list(
                    zip(
                        range(current_row + 1, new_row + 1),
                        range(current_column + 1, new_column),
                    )
                )

            elif new_row == current_row:  # right
                squares = [
                    (current_row, current_column + i)
                    for i in range(1, new_column - current_column)
                ]

            else:
                squares = list(  # top right diagonal
                    zip(
                        range(current_row - 1, new_row, -1),
                        range(current_column + 1, new_column),
                    )
                )

        elif new_column == current_column:
            if new_row > current_row:  # below
                squares = [
                    (current_row + i, current_column)
                    for i in range(1, new_row - current_row)
                ]

            else:  # above
                squares = [
                    (current_row - i, current_column)
                    for i in range(1, current_row - new_row, 1)
                ]

        else:
            if new_row > current_row:  # bottom left diagonal
                squares = list(
                    zip(
                        range(current_row + 1, new_row),
                        range(current_column - 1, new_column, -1),
                    )
                )

            elif new_row == current_row:  # left
                squares = [
                    (current_row, current_column - i)
                    for i in range(1, current_column - new_column)
                ]

            else:  # top left diagonal
                squares = list(
                    zip(
                        range(current_row - 1, new_row, -1),
                        range(current_column - 1, new_column, -1),
                    )
                )

        return squares

    def execute_move(self, current_square, new_square):
        """
        Executes a move by moving the piece object's location in the board list
        """
        current_row, current_column = current_square
        new_row, new_column = new_square

        piece = self.board.board[current_row][current_column]
        piece_at_new_square = self.board.board[new_row][new_column]

        self.board.board[current_row][current_column] = None
        self.board.board[new_row][new_column] = piece
        piece.row = new_row
        piece.column = new_column

        if piece_at_new_square:
            if piece_at_new_square.colour:
                self.board.white_pieces.remove(piece_at_new_square)
            else:
                self.board.black_pieces.remove(piece_at_new_square)

        if isinstance(piece, (Pawn, Rook, King)):
            piece.has_moved = True

        if isinstance(piece, King):
            if piece.colour:
                self.white_king_location = (new_row, new_column)
            else:
                self.black_king_location = (new_row, new_column)

        self.current_player_colour = not self.current_player_colour

    def is_king_in_check(self):
        """
        Checks all rows, columns and diagonals leading out from the king and
        checks if there are any opponent pieces attacking the king.
        """
        self.white_check = False
        self.black_check = False
        current_colour = self.current_player_colour
        if current_colour:
            current_row, current_column = self.white_king_location
        else:
            current_row, current_column = self.black_king_location

        directions = [
            # Rook/Queen directions (straight lines):
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            # Bishop/Queen directions (diagonal lines):
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        for i, direction in enumerate(directions):
            for step in range(1, 8):
                new_row = current_row + direction[0] * step
                new_column = current_column + direction[1] * step
                if 0 <= new_row < 8 and 0 <= new_column < 8:
                    piece = self.board.board[new_row][new_column]
                    if piece is None:
                        continue
                    if piece.colour == self.current_player_colour:
                        break
                    if (0 <= i <= 3 and isinstance(piece, (Rook, Queen))) or (
                        4 <= i <= 7
                        and isinstance(piece, (Bishop, Queen))
                        or (
                            isinstance(piece, Pawn)
                            and (current_row, current_column)
                            in piece.get_attacked_squares()
                        )
                    ):
                        if self.current_player_colour:
                            self.white_check = True
                        else:
                            self.black_check = True
                break

        knight_positions = [
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
        ]

        for vertical_shift, horizontal_shift in knight_positions:
            new_row = current_row + vertical_shift
            new_column = current_column + horizontal_shift
            if 0 <= new_row < 8 and 0 <= new_column < 8:
                piece = self.board.board[new_row][new_column]
                if piece is None or piece.colour == self.current_player_colour:
                    continue
                if isinstance(piece, Knight):
                    if self.current_player_colour:
                        self.white_check = True
                    else:
                        self.black_check = True


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


GAME = Game()
GAME.board.initialise_board()
GAME.play()
