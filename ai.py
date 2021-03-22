"""AI"""
import random

random.seed(7)


class AI:
    """AI"""

    WHITE_CHECKMATE = 10000
    BLACK_CHECKMATE = -10000
    STALEMATE = 0

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
                if piece_at_new_square:
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
