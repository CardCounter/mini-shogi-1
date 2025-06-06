import numpy as np
import hashlib

BOARD_SIZE = 5
WHOS_TURN = {0: 'BLACK', 1: 'WHITE'}
BLACK, WHITE = 1, 0  # black (first) K, white k
EMPTY = 0

# row, col, repeat
MOVE_DICT = {
    1: [(-1,0,0),(-1,-1,0),(0,-1,0),(1,-1,0),(1,0,0),(1,1,0),(0,1,0),(-1,1,0)], # K
    2: [(0,-1,0),(-1,-1,0),(-1,0,0),(-1,1,0),(0,1,0),(1,0,0)], # G
    3: [(-1,-1,0),(-1,0,0),(-1,1,0),(1,-1,0),(1,1,0)], # S
    4: [(-1,-1,1),(-1,1,1),(1,-1,1),(1,1,1)], # B
    5: [(0,-1,1),(-1,0,1),(0,1,1),(1,0,1)], # R
    6: [(1,0,0)], # P

    # promoted
    7: [(0,-1,0),(-1,-1,0),(-1,0,0),(-1,1,0),(0,1,0),(1,0,0)], # +S
    8: [(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1),(-1,0,0),(0,1,0),(1,0,0),(0,-1,0)], # +B
    9: [(-1,0,1),(0,-1,1),(1,0,1),(0,-1,1),(-1,1,0),(1,1,0),(1,-1,0),(-1,-1,0)], # +R
    10: [(0,-1,0),(-1,-1,0),(-1,0,0),(-1,1,0),(0,1,0),(1,0,0)], # +P

    -1: [(-1,0,0),(-1,1,0),(0,1,0),(1,1,0),(1,0,0),(1,-1,0),(0,-1,0),(-1,-1,0)],
    -2: [(0,1,0),(1,1,0),(1,0,0),(1,-1,0),(0,-1,0),(-1,0,0)],
    -3: [(1,-1,0),(1,0,0),(1,1,0),(-1,-1,0),(-1,1,0)],
    -4: [(1,-1,1),(1,1,1),(-1,1,1),(-1,-1,1)],
    -5: [(0,-1,1),(1,0,1),(0,1,1),(1,0,1)],
    -6: [(-1,0,0)],

    -7: [(0,1,0),(1,1,0),(1,0,0),(1,-1,0),(0,-1,0),(-1,0,0)],
    -8: [(-1,1,1),(1,1,1),(1,-1,1),(-1,-1,1),(-1,0,0),(0,1,0),(1,0,0),(0,-1,0)],
    -9: [(-1,0,1),(0,1,1),(1,0,1),(0,1,1),(-1,1,0),(1,1,0),(1,-1,0),(-1,-1,0)],
    -10: [(0,1,0),(1,1,0),(1,0,0),(1,-1,0),(0,-1,0),(-1,0,0)],
}

PROMOTION_MAP = {
    3: 7,
    4: 8,
    5: 9,
    6: 10,

    -3: -7,
    -4: -8,
    -5: -9,
    -6: -10
}
UNPROMOTION_MAP = {v: k for k, v in PROMOTION_MAP.items()}
PROMOTION_SET = {7, 8, 9, 10, -7, -8, -9, -10}

PIECE_TO_CHAR_MAP = {
    0: '.',

    1: 'K',
    2: 'G',
    3: 'S',
    4: 'B',
    5: 'R',
    6: 'P',
    7: '+S',
    8: '+B',
    9: '+R',
    10: '+P',

    -1: 'k',
    -2: 'g',
    -3: 's',
    -4: 'b',
    -5: 'r',
    -6: 'p',
    -7: '+s',
    -8: '+b',
    -9: '+r',
    -10: '+p'
}

WORKING_PIECES = {
    0: {1,2,3,4,5,6,7,8,9,10},
    1: {-1,-2,-3,-4,-5,-6,-7,-8,-9,-10}
}

WHICH_COLOUR_IS_PIECE = {
    True: 0,
    False: 1
}

BLACK_START = [1, 2, 3, 4, 5]
WHITE_START = [-5, -4, -3, -2, -1]

class piece:
    def __init__(self, piece: int, row, col):
        self.piece = piece
        self.row = row
        self.col = col
        self.moves = MOVE_DICT[self.piece]
        self.can_be_promoted = 0 # 1 if move will enter promotion zone, or if piece is in pz and moves within it, or if piece is in pz and moves out of it

    def isBlack(self):
        return self.piece > 0
    
    def promote_piece(self):
        try:
            if self.can_be_promoted:
                self.piece = PROMOTION_MAP[self.piece]
                self.moves = MOVE_DICT[self.piece]
                self.can_be_promoted = 0
        except Exception:
            print('unable to promote (did you promote K or G?)')

    def capture_piece(self): ## use on piece
        if self.piece in PROMOTION_SET: self.piece = UNPROMOTION_MAP[self.piece]
        self.piece = self.piece * -1

        self.row = None
        self.col = None
        self.moves = MOVE_DICT[self.piece]
        self.can_be_promoted = 0
        # then dont forget to add this piece to the hand of the opponent, addToOpponentsHand(self.piece), just check the piece
        # colour and add it to corresponding hand

class Board:
    def __init__(self):
        self.row = BOARD_SIZE
        self.col = BOARD_SIZE
        self.pieces_on_board = []
        self.board = self._initialize_board()
        self.hand = [[], []] # BLACK, WHITE

    def _initialize_board(self):
        board = np.zeros((self.row, self.col))
        for i in range(BOARD_SIZE):
            board[0, i] = piece(WHITE_START[i], 0, i)
            board[BOARD_SIZE-1, i] = piece(BLACK_START[i], BOARD_SIZE-1, i)

            self.pieces_on_board.append(board[0, i])
            self.pieces_on_board.append(board[BOARD_SIZE-1, i])
            
        board[1, BOARD_SIZE-1] = piece(-6, 1, BOARD_SIZE-1)
        board[3, 0] = piece(6, 3, 0)

        self.pieces_on_board.append(board[1, BOARD_SIZE-1])
        self.pieces_on_board.append(board[3, 0])

        return board
    
    def print_board(self):
        temp = []
        
        for row in range(self.board.shape[0]):
            temp_row = []
            for col in range(self.board.shape[1]):
                temp_row.append(PIECE_TO_CHAR_MAP[self.board[row, col]])

            temp.append(temp_row)

        print(np.array(temp))

    def out_of_bounds(self, row, col):
        if row < 0 or row > self.row-1 or col < 0 or col > self.col-1: return True
        return False
    
    # def valid_moves(self, piece, turn): # turn gives which player is moving, # eventually want possible move list to be list of (piece, (move))

class Game:
    def __init__(self):
        self.game_board = Board()
        self.seen_game_states = {}
        self.turn = 0

    def is_loc_edge_promote(self, piece):
        pass

    def is_loc_in_promote(self, piece):
        pass

    def can_piece_promote(self, piece, future_row, future_col): ## True, False, dont, has to.
        pass

    def get_all_piece_moves(self, piece, game_board): # return list of (piece, (move)), move = (row, col, promote_after_move)

        # also check if in check #################

        possible_moves = piece.moves
        current_row = piece.row
        current_col = piece.col
        piece_colour = WHICH_COLOUR_IS_PIECE[piece.piece > 0]
        valid_moves = []

        for move in possible_moves:
            # normal moves
            if move[-1] == 0:
                try_row = current_row + move[0]
                try_col = current_col + move[1]

                if not self.out_of_bounds(try_row, try_col):
                    at_try_loc = game_board.board[try_row, try_col]
                    if at_try_loc == 0 or WHICH_COLOUR_IS_PIECE[at_try_loc.piece > 0] != piece_colour: # enemy colour
                        promote_after_move = self.can_piece_promote(piece, try_row, try_col)

                        if abs(piece.piece) == 6 and promote_after_move: # if pawn, have to promote
                            valid_moves.append((piece, (try_row, try_col, 1))) # 1 = promote after move, 0 ow, used in move_piece()
                        
                        elif promote_after_move: ## if can promote, give both options
                            valid_moves.append((piece, (try_row, try_col, 0))) 
                            valid_moves.append((piece, (try_row, try_col, 1)))

                        else: # cant
                            valid_moves.append((piece, (try_row, try_col, 0))) 

            else: # move[-1] == 1, only for bishop and rook
                try_row = current_row
                try_col = current_col
                
                while True:
                    try_row += move[0]
                    try_col += move[1]

                    if self.out_of_bounds(try_row, try_col):
                        break

                    at_try_loc = game_board.board[try_row, try_col]
                    
                    if WHICH_COLOUR_IS_PIECE[at_try_loc.piece > 0] == piece_colour:
                        break

                    if WHICH_COLOUR_IS_PIECE[at_try_loc.piece > 0] != piece_colour:
                        promote_after_move = self.can_piece_promote(piece, try_row, try_col)
                        if promote_after_move:
                            valid_moves.append((piece, (try_row, try_col, 0))) 
                            valid_moves.append((piece, (try_row, try_col, 1)))
                        else:
                            valid_moves.append((piece, (try_row, try_col, 0))) 

                        break

                    else: # must be in empty
                        promote_after_move = self.can_piece_promote(piece, try_row, try_col)
                        if promote_after_move:
                            valid_moves.append((piece, (try_row, try_col, 0))) 
                            valid_moves.append((piece, (try_row, try_col, 1)))
                        else:
                            valid_moves.append((piece, (try_row, try_col, 0))) 

        return valid_moves

    def get_all_piece_drops(self, piece, game_board): ## already in hand, just need to find empty places to drop
        valid_drops = []

        for row in range(game_board.board.shape[0]):
            for col in range(game_board.board.shape[1]):
                if game_board.board[row, col] == 0:
                    try_row = row
                    try_col = col
                    test_board = game_board.board.copy()

                    if abs(piece.piece) == 6: # pawn cant be dropped into a checkmate
                        test_board[row, col] = piece
                        if not self.is_checknmate(test_board): valid_drops.append((piece, (try_row, try_col, 0)))

    def get_all_valid_moves(self, list_of_moves, game_board): 
        all_actions = list_of_moves

        if self.is_check(game_board):
            pass
            ## filter out all moves that dont get you out of check. can use this for checkmate actually.

        return all_actions

    def is_checkmate(self, board):
        pass

    def is_check(self, board):
        pass

    def is_piece_attacking_enemy_king(self, piece, board): # need to get piece colour to know which king we're attacking
        pass

    def get_all_possible_valid_moves(self):
        current_player = self.turn % 2
        working_pieces_set = WORKING_PIECES[current_player]
        valid_moves = []

        # get all possible valid moves for pieces on board
        for piece in self.game_board.pieces_on_board:
            if piece in working_pieces_set:
                valid_moves.append(self.get_all_piece_moves(piece, self.game_board))

        for drop_piece in self.game_board.hand[current_player]:
            valid_moves.append(self.get_all_piece_drops(drop_piece, self.game_board))

        return self.get_all_valid_moves(valid_moves, self.game_board)









# def hash_to_string(input: str):      comes in later
#     return hashlib.blake2b(input.encode(), digest_size=8, key=b"1").digest()

# def hash_board_state()


"""
check if move is valid
check if take is valid
on turn, check if in check

after move, check if can promote, check if checkmate, whos in checkmate
check if board state has been reached (including same person moving, and same pieces in hand) four times, loss for black.
    => save the board state as stirng, attack black and white hands, attach player to move, all as a string, then hash, store hash in dict? to track how oftern that
    board has been seen

if pawn moves to last rank, force it to promote

check if drop is valid, if pawn check if its in last row, if it gives checkmate only.

"""


if __name__ == '__main__':
    newboard = Board()
    newboard.print_board()











