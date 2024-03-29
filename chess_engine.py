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

        self.white_pieces_taken = []
        self.black_pieces_taken = []

    def print_board(self):
        """Prints the board list row by row, tab-separated."""
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
    """Controls the overall mechanisms of the game."""

    def __init__(self):
        self.board = Board()
        self.current_player_colour = True
        self.white_check = False
        self.black_check = False
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.white_checkmate = False
        self.black_checkmate = False
        self.stalemate = False
        self.current_move = []
        self.show_promotion_box = False
        self.promotion_square = ()
        self.ai_game = False
        self.ai_colour = None
        self.in_progress = False
        self.__just_castled = False
        self.__en_passant_move = False

    def play(self):
        """Allows the game to played in the terminal (without a GUI)."""
        self.board.print_board()
        while not (self.white_checkmate or self.black_checkmate or self.stalemate):
            print("\nWhite:" if self.current_player_colour else "\nBlack:")
            current_square, new_square = self.input_move()
            if self.validate_move(current_square, new_square):
                self.execute_move(current_square, new_square)
                print()
                self.board.print_board()
                self.is_checkmate_or_stalemate()
                self.check_draw()
            else:
                print("Not legal")

        if self.white_checkmate:
            print("\nCheckmate. White wins!")
        elif self.black_checkmate:
            print("\nCheckmate. Black wins!")
        elif self.stalemate:
            print("\nStalemate. It's a draw!")

    def input_move(self):
        """
        Takes input for a move. This is done by taking input for the current
        square that the piece to be moved is on, and the square where the piece
        is to be moved. The squares are described using the standard algebraic
        notation (1-8 for rows, a-h for columns). This is only used when
        playing the game without a GUI.
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
        colour. It also checks if the move results in the player's own king
        being in check, in which case the move is invalid.
        """
        current_row, current_column = current_square
        new_row, new_column = new_square

        current_piece = self.board.board[current_row][current_column]
        piece_at_new_square = self.board.board[new_row][new_column]

        # Check if move is legal for that type of piece and if move is blocked
        if not self.__is_move_legal(
            current_square, new_square
        ) or self.__is_move_blocked(current_square, new_square):
            return False

        # Check if there is a piece at the new square of the same colour
        if piece_at_new_square is not None:
            if current_piece.colour == piece_at_new_square.colour:
                return False

        self.__is_king_in_check()

        # check if move is castle
        if isinstance(current_piece, King):
            if (
                new_row == current_row
                and new_column == current_column + 2
                or new_column == current_column - 2
            ):
                return self.__validate_castling_move(current_square, new_square)

        # Check if the move puts the player's own king in check:

        valid = True

        # Execute the move
        self.board.board[current_row][current_column] = None
        self.board.board[new_row][new_column] = current_piece

        if self.current_player_colour:  # The current player is white
            if isinstance(current_piece, King):
                self.white_king_location = (new_row, new_column)

            self.__is_king_in_check()

            if self.white_check:  # Move puts own king in check => invalid
                valid = False

            if isinstance(current_piece, King):
                self.white_king_location = (current_row, current_column)

        else:  # The current player is black
            if isinstance(current_piece, King):
                self.black_king_location = (new_row, new_column)

            self.__is_king_in_check()

            if self.black_check:
                valid = False

            if isinstance(current_piece, King):
                self.black_king_location = (current_row, current_column)

        # Undo the move
        self.board.board[current_row][current_column] = current_piece
        self.board.board[new_row][new_column] = piece_at_new_square

        return valid

    def __is_move_legal(self, current_square, new_square):
        """
        Checks if the move abides by the moving rules for that piece.
        """
        if self.__en_passant_move:  # Stops infinite recursion after en passant
            self.__en_passant_move = False
            return True

        current_row, current_column = current_square
        new_row, new_column = new_square
        piece = self.board.board[current_row][current_column]
        if piece is None or piece.colour != self.current_player_colour:
            return False

        # Allows castling moves
        if isinstance(piece, King):
            if (
                new_row == current_row
                and new_column == current_column + 2
                or new_column == current_column - 2
            ):
                return True

        # Allows diagonal attacks from pawns
        if isinstance(piece, Pawn):
            piece_at_square = self.board.board[new_row][new_column]
            if (
                piece_at_square
                and piece_at_square.colour != self.current_player_colour
                or self.__validate_en_passant(current_square, new_square)
            ):
                return new_square in piece.get_attacked_squares()

        return new_square in piece.generate_moves()

    def __is_move_blocked(self, current_square, new_square):
        """
        Checks if a move is blocked by another piece. This is done by checking
        if there are any pieces in the squares between the current and new
        squares.
        """
        current_row, current_column = current_square
        piece = self.board.board[current_row][current_column]

        if isinstance(piece, Knight):
            return False

        squares_passed = self.__get_passed_squares(current_square, new_square)
        return any(
            [self.board.board[square[0]][square[1]] for square in squares_passed]
        )

    def __get_passed_squares(self, current_square, new_square):
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
        # Prevents move from being executed twice after castling
        if self.__just_castled:
            self.__just_castled = False
            return

        current_row, current_column = current_square
        new_row, new_column = new_square

        # Updates items in board list
        piece = self.board.board[current_row][current_column]
        piece_at_new_square = self.board.board[new_row][new_column]

        self.board.board[current_row][current_column] = None
        self.board.board[new_row][new_column] = piece
        piece.row = new_row
        piece.column = new_column

        # Updates pieces currently on the board and pieces taken
        if piece_at_new_square:
            if piece_at_new_square.colour:
                self.board.white_pieces.remove(piece_at_new_square)
                self.board.white_pieces_taken.append(piece_at_new_square)
            else:
                self.board.black_pieces.remove(piece_at_new_square)
                self.board.black_pieces_taken.append(piece_at_new_square)

        self.__update_en_passant()

        # Checks if pawn should be promoted, or if it can be taken en passant
        # promote_pawn only called when playing the game without a GUI.
        if isinstance(piece, Pawn):
            if self.current_player_colour:
                if new_row == 0:
                    # self.__promote_pawn(piece)
                    pass
                elif current_row == 6 and new_row == 4:
                    piece.en_passant_possible = True
            else:
                if new_row == 7:
                    # self.__promote_pawn(piece)
                    pass
                elif current_row == 1 and new_row == 3:
                    piece.en_passant_possible = True

        if isinstance(piece, (Pawn, Rook, King)):
            piece.has_moved = True

        if isinstance(piece, King):
            if piece.colour:
                self.white_king_location = (new_row, new_column)
            else:
                self.black_king_location = (new_row, new_column)

        # Switches current player
        self.current_player_colour = not self.current_player_colour

    def __is_king_in_check(self):

        """
        Looks at all rows, columns and diagonals leading out from the king and
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
            # Bishop/Queen/Pawn directions (diagonal lines):
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
                    # If there is a piece of the same colour in that direction,
                    # then it will block any attacks from pieces behind it
                    if piece.colour == self.current_player_colour:
                        break
                    # The king is in check if any of these types of pieces are
                    # found in the directions in which they attack.
                    if (0 <= i <= 3 and isinstance(piece, (Rook, Queen))) or (
                        4 <= i <= 7
                        and isinstance(piece, (Bishop, Queen))
                        or (
                            isinstance(piece, Pawn)
                            and (current_row, current_column)
                            in piece.get_attacked_squares()
                        )
                        or isinstance(piece, King)
                        and (current_row, current_column) in piece.generate_moves()
                    ):
                        if self.current_player_colour:
                            self.white_check = True
                        else:
                            self.black_check = True
                break

        # Look for knight checks:
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

    def is_checkmate_or_stalemate(self):
        """
        Determines whether the current player is in checkmate or stalemate.
        This is done by checking if there are any possible moves for any of the
        pieces on the board.
        """

        if self.current_player_colour:  # Current player is white
            pieces = self.board.white_pieces
        else:
            pieces = self.board.black_pieces

        # Check if there are any valid moves
        for piece in pieces:
            current_square = (piece.row, piece.column)
            moves = piece.generate_moves()
            if isinstance(piece, Pawn):
                moves += piece.get_attacked_squares()
            for new_square in moves:
                if self.validate_move(current_square, new_square):
                    return

        if self.current_player_colour:  # Current player is white
            self.__is_king_in_check()

            if self.white_check:
                self.black_checkmate = True
            else:
                self.stalemate = True

        else:  # Current player is black
            self.__is_king_in_check()

            if self.black_check:
                self.white_checkmate = True
            else:
                self.stalemate = True

    def __validate_castling_move(self, current_square, new_square):
        """
        Determines whether a castling move is valid. The move is invalid if
        there are any pieces between the king and rook, if either the king or
        rook have moved previously, the king is in check or it moves over check
        """
        current_row, current_column = current_square
        _, new_column = new_square

        king_piece = self.board.board[current_row][current_column]
        passed_squares_columns = []

        if new_column > current_column:  # King-side castle
            end_column = 7
            rook_piece = self.board.board[current_row][end_column]
            passed_squares_columns = list(range(current_column, new_column + 1))
            new_rook_column = new_column - 1

        else:  # Queen-side castle
            end_column = 0
            rook_piece = self.board.board[current_row][end_column]
            passed_squares_columns = list(range(current_column, new_column - 1, -1))
            new_rook_column = new_column + 1

        # Move is invalid if it is blocked, either the king or rook have moved
        # or if king is in check
        if (
            self.__is_move_blocked(current_square, (current_row, end_column))
            or king_piece.has_moved
            or rook_piece is None
            or rook_piece.has_moved
            or (self.current_player_colour and self.white_check)
            or (not self.current_player_colour and self.black_check)
        ):
            return False

        # Check if king passes over attacked squares
        valid = True
        for column in passed_squares_columns:
            self.board.board[current_row][column] = king_piece

            if self.current_player_colour:  # The current player is white
                self.white_king_location = (current_row, column)

                self.__is_king_in_check()

                if self.white_check:
                    valid = False

                self.white_king_location = (current_row, current_column)

            else:
                self.black_king_location = (current_row, column)

                self.__is_king_in_check()

                if self.black_check:
                    valid = False

                self.black_king_location = (current_row, current_column)

            self.board.board[current_row][current_column] = king_piece
            self.board.board[current_row][column] = None

        if valid:  # execute castle moves
            self.execute_move(current_square, new_square)
            self.current_player_colour = not self.current_player_colour
            self.execute_move(
                (current_row, rook_piece.column), (current_row, new_rook_column)
            )
            self.__just_castled = True
            return True
        return False

    def __promote_pawn(self, pawn):
        """
        Promotes the pawn to a new piece when it reaches the last row.
        This method is only used when playing the game without a GUI.
        """
        row = pawn.row
        column = pawn.column
        colour = pawn.colour

        new_piece = None
        while new_piece is None:
            piece_name = input("New piece (Queen/Rook/Bishop/Knight): ").lower()
            if piece_name == "queen":
                new_piece = Queen(row, column, colour)
            elif piece_name == "rook":
                new_piece = Rook(row, column, colour)
            elif piece_name == "bishop":
                new_piece = Bishop(row, column, colour)
            elif piece_name == "knight":
                new_piece = Knight(row, column, colour)

        if colour:
            self.board.white_pieces.remove(pawn)
            self.board.white_pieces.append(new_piece)
        else:
            self.board.black_pieces.remove(pawn)
            self.board.black_pieces.append(new_piece)

        self.board.board[row][column] = new_piece

    def __update_en_passant(self):
        """
        Sets the 'en passant possible' attribute for all pawns to false
        after a move is made.
        """
        if self.current_player_colour:
            pieces = self.board.white_pieces
        else:
            pieces = self.board.black_pieces

        for piece in pieces:
            if isinstance(piece, Pawn):
                piece.en_passant_possible = False

    def __validate_en_passant(self, current_square, new_square):
        """Checks if en passant move is valid"""
        current_row, current_column = current_square
        new_row, new_column = new_square

        if (
            (self.current_player_colour and new_row != 2)
            or (not self.current_player_colour and new_row != 5)
            or new_column not in (current_column - 1, current_column + 1)
        ):
            return False

        # Get pawn that would be captured
        en_passant_piece = self.board.board[current_row][new_column]

        if isinstance(en_passant_piece, Pawn):
            if en_passant_piece.en_passant_possible:
                self.__en_passant_move = True
                if self.validate_move(current_square, new_square):
                    # If AI is playing, you do not want the move to executed
                    # while searching for valid moves
                    if self.current_player_colour == self.ai_colour:
                        return True
                    self.__execute_en_passant_move(
                        current_square, new_square, en_passant_piece
                    )
                    return True

        return False

    def __execute_en_passant_move(self, current_square, new_square, piece):
        """Executes an en passant move."""
        current_row, _ = current_square
        _, new_column = new_square

        # Remove captured piece from board
        self.board.board[current_row][new_column] = None
        if self.current_player_colour: # Player is white
            self.board.black_pieces.remove(piece)
            self.board.black_pieces_taken.append(piece)
        else: # Player is black
            self.board.white_pieces.remove(piece)
            self.board.white_pieces_taken.append(piece)
        self.execute_move(current_square, new_square)

    def check_draw(self):
        """
        Checks if the game should be a draw due to both teams having 
        insufficient material to result in a checkmate. This is true for
        King vs King, King + Knight vs King, and King + Bishop vs King.
        """

        opponent_pieces = []
        if len(self.board.white_pieces) == 1:  # white only has the king
            opponent_pieces = [type(piece) for piece in self.board.black_pieces]

        if len(self.board.black_pieces) == 1:  # black only has the king
            opponent_pieces = [type(piece) for piece in self.board.white_pieces]

        if (
            len(opponent_pieces) == 0
            or len(opponent_pieces) > 2
            or Pawn in opponent_pieces
            or Rook in opponent_pieces
            or Queen in opponent_pieces
        ):
            return

        self.stalemate = True
        return

    def get_all_moves(self):
        """
        Returns list of all moves (not validated). This is done by iterating
        through each piece on the board and generating moves for each piece.
        """

        moves = []
        for piece in self.board.white_pieces + self.board.black_pieces:
            moves += [
                [(piece.row, piece.column), new_square]
                for new_square in piece.generate_moves()
            ]
            if isinstance(piece, Pawn):
                moves += [
                    [(piece.row, piece.column), new_square]
                    for new_square in piece.get_attacked_squares()
                ]
        return moves

    def get_valid_moves(self):
        """Filters the list of all moves by the ones which are valid"""
        valid_moves = []
        for current_square, new_square in self.get_all_moves():
            if self.validate_move(current_square, new_square):
                valid_moves.append([current_square, new_square])
        return valid_moves


class Pawn(Piece):
    """Piece with value 1."""

    def __init__(self, row, column, colour):
        super().__init__(row, column, 1, colour)
        self.has_moved = False
        self.en_passant_possible = False
        self.__direction = 1 if self.colour else -1

    def generate_moves(self):
        """
        Pawns can move 1 square forward and 2 squares forward if they have not
        yet moved.
        """
        moves = []

        moves.append((self.row - self.__direction, self.column))
        if not self.has_moved:
            moves.append((self.row - 2 * self.__direction, self.column))

        return moves

    def get_attacked_squares(self):
        """
        Pawns can move 1 square forward diagonally when they take an opponent's
        piece.
        """
        moves = []
        new_row = self.row - self.__direction
        if 0 <= new_row < 8:
            if self.column > 0:
                moves.append((new_row, self.column - 1))
            if self.column < 7:
                moves.append((new_row, self.column + 1))

        return moves

    def __str__(self):
        if self.colour:
            return "P"
        return "P'"


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
        if self.colour:
            return "B"
        return "B'"


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
        if self.colour:
            return "N"
        return "N'"


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
        if self.colour:
            return "R"
        return "R'"


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
        if self.colour:
            return "Q"
        return "Q'"


class King(Piece):
    """
    Piece initialised with value 0. If this piece is attacked and there are no
    legal moves, the game is over.
    """

    def __init__(self, row, column, colour):
        super().__init__(row, column, 0, colour)
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
        if self.colour:
            return "K"
        return "K'"


if __name__ == "__main__":
    GAME = Game()
    GAME.board.initialise_board()
    GAME.play()
