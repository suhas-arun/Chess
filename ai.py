"""AI"""

class AI:
    """AI"""
    WHITE_CHECKMATE = 10000
    BLACK_CHECKMATE = -10000
    STALEMATE = 0

    def evaluate_board(self, board, white_checkmate, black_checkmate, draw):
        """
        Returns the score for the board based on the net material of the two
        players. White pieces are worth positive points and black pieces are
        worth negative points.
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
    