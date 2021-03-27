"""AI"""
import random
from chess_engine import King, Queen, Pawn


class AI:
    """AI"""

    WHITE_CHECKMATE = 10000
    BLACK_CHECKMATE = -10000
    STALEMATE = 0
    DEPTH = 2

    def __init__(self):
        self.minimax_best_moves = []

    def evaluate_board(self, board, white_checkmate, black_checkmate, draw):
        """
        Returns the score for the board based on the pieces of the two players.
        White pieces are worth positive points and black pieces are worth
        negative points.
        """

        score = 0
        if white_checkmate:
            return self.WHITE_CHECKMATE
        if black_checkmate:
            return self.BLACK_CHECKMATE
        if draw:
            return self.STALEMATE
        for piece in board.white_pieces + board.black_pieces:
            score += piece.get_value()

        return score

    def get_random_move(self, valid_moves):
        """Returns a random valid move."""
        return random.choice(valid_moves)

    def get_greedy_ai_move(self, gamestate):
        """Returns the best valid move for the current board state"""
        multiplier = 1 if gamestate.ai_colour else -1
        best_moves = []
        best_score = self.BLACK_CHECKMATE
        for move in gamestate.get_valid_moves():
            # Execute the move
            (current_row, current_column), (new_row, new_column) = move
            current_piece = gamestate.board.board[current_row][current_column]
            piece_at_new_square = gamestate.board.board[new_row][new_column]

            gamestate.board.board[current_row][current_column] = None
            gamestate.board.board[new_row][new_column] = current_piece

            if piece_at_new_square:
                if piece_at_new_square.colour:
                    gamestate.board.white_pieces.remove(piece_at_new_square)
                else:
                    gamestate.board.black_pieces.remove(piece_at_new_square)

            # Evaluate the new board state
            score = (
                self.evaluate_board(
                    gamestate.board,
                    gamestate.white_checkmate,
                    gamestate.black_checkmate,
                    gamestate.stalemate,
                )
                * multiplier
            )

            # Undo the move
            gamestate.board.board[current_row][current_column] = current_piece
            gamestate.board.board[new_row][new_column] = piece_at_new_square

            if piece_at_new_square:
                if piece_at_new_square.colour:
                    gamestate.board.white_pieces.append(piece_at_new_square)
                else:
                    gamestate.board.black_pieces.append(piece_at_new_square)

            # Check if best move
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        if best_moves:
            return self.get_random_move(best_moves)
        return self.get_random_move(gamestate.get_valid_moves())

    def get_ai_move_minimax(self, gamestate, depth, current_player):
        """Performs the minimax algorithm to find the best move for the AI."""
        multiplier = 1 if current_player else -1
        # Base case
        if depth == 0:
            return (
                self.evaluate_board(
                    gamestate.board,
                    gamestate.white_checkmate,
                    gamestate.black_checkmate,
                    gamestate.stalemate,
                )
                * multiplier
            )

        best_score = self.BLACK_CHECKMATE
        for move in gamestate.get_valid_moves():
            # Execute the move
            (current_row, current_column), (new_row, new_column) = move
            current_piece = gamestate.board.board[current_row][current_column]
            piece_at_new_square = gamestate.board.board[new_row][new_column]

            gamestate.board.board[current_row][current_column] = None
            gamestate.board.board[new_row][new_column] = current_piece

            if isinstance(current_piece, King):
                if current_player:
                    gamestate.white_king_location = (new_row, new_column)
                else:
                    gamestate.black_king_location = (new_row, new_column)

            elif isinstance(current_piece, Pawn):
                if current_piece.colour and new_row == 0:
                    new_piece = Queen(new_row, new_column, True)
                    gamestate.board.white_pieces.remove(current_piece)
                    gamestate.board.white_pieces.append(new_piece)
                    gamestate.board.board[new_row][new_column] = new_piece
                    
                elif not current_piece.colour and new_row == 7:
                    new_piece = Queen(new_row, new_column, False)
                    gamestate.board.black_pieces.remove(current_piece)
                    gamestate.board.black_pieces.append(new_piece)
                    gamestate.board.board[new_row][new_column] = new_piece
                
            gamestate.current_player_colour = not gamestate.current_player_colour

            if current_piece is None:
                return self.BLACK_CHECKMATE

            current_piece.row = new_row
            current_piece.column = new_column

            if piece_at_new_square:
                if piece_at_new_square.colour:
                    gamestate.board.white_pieces.remove(piece_at_new_square)
                else:
                    gamestate.board.black_pieces.remove(piece_at_new_square)

            gamestate.is_checkmate_or_stalemate()
            gamestate.check_draw()

            score = -1 * self.get_ai_move_minimax(
                gamestate, depth - 1, not current_player
            )

            # Undo the move
            gamestate.board.board[current_row][current_column] = current_piece
            gamestate.board.board[new_row][new_column] = piece_at_new_square

            if isinstance(current_piece, King):
                if current_player:
                    gamestate.white_king_location = (current_row, current_column)
                else:
                    gamestate.black_king_location = (current_row, current_column)

            elif isinstance(current_piece, Pawn):
                if current_piece.colour and new_row == 0:
                    gamestate.board.white_pieces.append(current_piece)
                    gamestate.board.white_pieces.remove(new_piece)
                elif not current_piece.colour and new_row == 7:
                    gamestate.board.black_pieces.append(current_piece)
                    gamestate.board.black_pieces.remove(new_piece)

            gamestate.current_player_colour = not gamestate.current_player_colour

            current_piece.row = current_row
            current_piece.column = current_column

            if piece_at_new_square:
                if piece_at_new_square.colour:
                    gamestate.board.white_pieces.append(piece_at_new_square)
                else:
                    gamestate.board.black_pieces.append(piece_at_new_square)

            gamestate.white_checkmate = False
            gamestate.black_checkmate = False
            gamestate.stalemate = False

            # Check if best score
            if score > best_score:
                best_score = score
                if depth == self.DEPTH:
                    self.minimax_best_moves = [move]

            elif score == best_score and depth == self.DEPTH:
                self.minimax_best_moves.append(move)

        return best_score
