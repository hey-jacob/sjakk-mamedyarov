import random
import io

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.move_functions = {'p':  self.get_pawn_moves,
                               'R': self.get_rook_moves,
                               'N': self.get_knight_moves,
                               'B': self.get_bishop_moves,
                               'Q': self.get_queen_moves,
                               'K': self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7,4)
        self.black_king_location = (0,4)
        self.in_check_flag = False
        self.checkmate = False
        self.stalemate = False
        self.pins = []
        self.checks = []
        self.en_passant_possible = () #coordinates where e-p possible
        self.en_passant_possible_log = [self.en_passant_possible]
        self.current_castling_rights = CastlingRights(True, True, True, True)
        self.castling_rights_log = [CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                                    self.current_castling_rights.wqs, self.current_castling_rights.bqs)]
        self.draw_by_insufficient_material = False
        self.all_board_positions = [] # to find threefold repetition
        self.white_has_castled = False
        self.black_has_castled = False






    def check_for_pins_and_check(self):
        pins = []
        checks = []
        in_check_flag = False
        if self.white_to_move:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        directions = ((-1,0), (0,-1), (1,0), (0,1), (-1, -1), (-1, 1), (1, -1), (1,1))\

        for j in range(len(directions)):
            d = directions[j]
            possible_pin = () #reset possible pins
            for i in range(1,8):
                end_row = start_row+d[0]*i
                end_col = start_col+d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == ():#1st allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        type = end_piece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B')  or \
                                (i == 1 and type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5)))\
                                or (type == 'Q') or (i == 1 and type == 'K'):
                            if possible_pin == (): #check if blocking
                                in_check_flag = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break

                else:
                    break #off board

        knight_moves = ((-2, 1), (-2, -1), (2, -1), (2, 1), (1, -2), (1, 2), (-1, -2), (-1, 2))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N':
                    in_check_flag = True
                    checks.append((end_row, end_col, m[0], m[1]))


        return in_check_flag, pins, checks



    def make_move(self, move):

        '''
        Takes a move as a paraméter and executes it
        '''
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move) # log move for undoing later / displaying history
        self.white_to_move = not self.white_to_move          # switch turns
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        #pawn promotion
        if move.is_pawn_promotion:
            promoted_piece = random.choice(['Q', 'R', 'B', 'N'])
            promoted_piece = 'Q'
            #promoted_piece = input("Promote to Q, R, B or N: ")
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece
        #en passant
        if move.is_en_passant_move:
            self.board[move.start_row][move.start_col] = '--'

        #update en passant possible variable after piece = p and pawn moved two squares

        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2: #only on two square pawn advances
            self.en_passant_possible = ((move.start_row+move.end_row)//2, move.start_col)
        else:
            self.en_passant_possible = ()

        # castle move

        if move.is_castle_move:
            col_diff = abs(move.end_col - move.start_col)
            if col_diff == 2: # kingside castle move
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = '--'

            elif col_diff == 3:
                self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '--'

            if move.piece_moved == 'wK':
                self.white_has_castled = True
            elif move.piece_moved == 'bK':
                self.black_has_castled = True

        self.en_passant_possible_log.append(self.en_passant_possible)


        # update castling rights

        self.update_castle_rights(move)
        self.castling_rights_log.append((CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.wqs,
                                                    self.current_castling_rights.bks, self.current_castling_rights.bqs)))

        # add to board state to check for threefold repetition

        self.all_board_positions.append(self.board_to_fen(self.board))

    def board_to_fen(self, board):
        # Use StringIO to build string more efficiently than concatenating
        with io.StringIO() as s:
            for row in board:
                empty = 0
                for cell in row:
                    c = cell[0]
                    if c in ('w', 'b'):
                        if empty > 0:
                            s.write(str(empty))
                            empty = 0
                        s.write(cell[1].upper() if c == 'w' else cell[1].lower())
                    else:
                        empty += 1
                if empty > 0:
                    s.write(str(empty))
                s.write('/')
            # Move one position back to overwrite last '/'
            s.seek(s.tell() - 1)
            # If you do not have the additional information choose what to put
            s.write(' w KQkq - 0 1')
            return s.getvalue()


    # undo move
    def undo_move(self):

        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)
            # undo en passant
            if move.is_en_passant_move:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.en_passant_possible_log.pop()

            # undo castling rights
            self.castling_rights_log.pop() #get rid of the new castling rights from the move we are undoing
            new_rights = self.castling_rights_log[-1]
            self.current_castling_rights = CastlingRights( new_rights.wks, new_rights.wqs, new_rights.bks, new_rights.bqs)

            # undo castling move

            if move.is_castle_move:
                if move.end_col - move.start_col == 2: #king side
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1] # move rook
                    self.board[move.end_row][move.end_col - 1] = '--' #empty space where rooks was

                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1] # move rook
                    self.board[move.end_row][move.end_col +1] = '--'

                if move.piece_moved == 'wK':
                    self.white_has_castled = False
                elif move.piece_moved == 'bK':
                    self.black_has_castled = False

        self.checkmate = False
        self.stalemate = False
        self.draw_by_insufficient_material = False
        self.all_board_positions.pop()


    def is_draw_by_insufficient_material(self):
        num_white_bishops = 0
        num_white_knights = 0
        num_black_bishops = 0
        num_black_knights = 0
        num_white_rooks = 0
        num_black_rooks = 0
        num_white_queens = 0
        num_black_queens = 0
        num_white_pawns = 0
        num_black_pawns = 0

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece[0] == 'w':
                    if piece[1] == 'N':
                        num_white_knights += 1
                    elif piece[1] == 'B':
                        num_white_bishops += 1
                    elif piece[1] == 'R':
                        num_white_rooks += 1
                    elif piece[1] == 'Q':
                        num_white_queens += 1
                    elif piece[1] == 'p':
                        num_white_pawns += 1
                else:
                    if piece[1] == 'N':
                        num_black_knights += 1
                    elif piece[1] == 'B':
                        num_black_bishops += 1
                    elif piece[1] == 'R':
                        num_black_rooks += 1
                    elif piece[1] == 'Q':
                        num_black_queens += 1
                    elif piece[1] == 'p':
                        num_black_pawns += 1

        if num_black_pawns > 0 or num_white_pawns > 0:
            return False

        if num_black_rooks > 0 or num_white_rooks > 0:
            return False

        if (((num_white_knights + num_white_bishops) == 1) and ((num_black_bishops +  num_black_knights) == 0)) or (((num_white_knights + num_white_bishops) == 0) and ((num_black_bishops +  num_black_knights) == 1)):
            return True

    def update_castle_rights(self, move):
        """
        Update the castle rights given the move
        """
        if move.piece_captured == "wR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.wqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.wks = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:  # left rook
                self.current_castling_rights.bqs = False
            elif move.end_col == 7:  # right rook
                self.current_castling_rights.bks = False

        if move.piece_moved == 'wK':
            self.current_castling_rights.wqs = False
            self.current_castling_rights.wks = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bqs = False
            self.current_castling_rights.bks = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_rights.bks = False








    #all moves considering checks

    def getValidMoves(self):
        """
        All moves considering checks.
        """
        temp_castle_rights = CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        # advanced algorithm
        moves = []
        self.in_check_flag, self.pins, self.checks = self.check_for_pins_and_check()

        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.get_all_possible_moves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].piece_moved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].end_row,
                                moves[i].end_col) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.get_king_moves(king_row, king_col, moves)
        else:  # not in check - all moves are fine
            moves = self.get_all_possible_moves()
            if self.white_to_move:
                self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)



        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.current_castling_rights = temp_castle_rights
        return moves

    def get_valid_moves(self):
        moves = []
        self.in_check_flag, self.pins, self.checks = self.check_for_pins_and_check()

        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]

        if self.in_check_flag:
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                if piece_checking[1] =='N': #if knight, knight must be captured or king must move
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1,8):
                        valid_square = (king_row + check[2]*i, king_col + check[3]*i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].piece_moved[1] != 'K' : #move doesnt move king so it must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_col, king_row, moves)
        else: #not in check so all move are fine
            moves = self.get_all_possible_moves()

        temp_castle_rights = CastlingRights(self.current_castling_rights.wks, self.current_castling_rights.bks,
                                            self.current_castling_rights.wqs, self.current_castling_rights.bqs)

        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        self.current_castling_rights = temp_castle_rights

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.draw_by_insufficient_material = self.is_draw_by_insufficient_material()

        return moves



    # determine if the current player is in check

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, row, col):
        """
        Determine if enemy can attack the square row col
        """
        self.white_to_move = not self.white_to_move  # switch to opponent's point of view
        opponents_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:  # square is under attack
                return True
        return False








    # all moves without considering checks

    def get_all_possible_moves(self):
        moves = []

        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)



        return moves


    def get_pawn_moves(self, r, c, moves):

        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            enemy_color = 'b'
            king_row, king_col =  self.white_king_location
        else:
            move_amount = 1
            start_row = 1
            enemy_color = 'w'
            king_row, king_col = self.black_king_location


        if self.board[r+move_amount][c] == '--': # one square move
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((r, c), (r+move_amount, c), self.board))
                if not self.white_to_move:
                    if r == start_row and self.board[r+2*move_amount][c] == '--': #two square moves
                        moves.append(Move((r, c), (r+2*move_amount, c), self.board))
                else:
                    if r == start_row and self.board[r+2*move_amount][c] == '--': #two square moves
                        moves.append(Move((r, c), (r+2*move_amount, c), self.board))

        if c - 1 >= 0: #capture to the left

            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[r+ move_amount][c - 1][0] == enemy_color:
                    moves.append(Move((r, c), (r+ move_amount, c - 1), self.board))
                if (r + move_amount, c - 1) == self.en_passant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col < c: # king is left of the pawn
                            #inside between king and pawn; outside range  between pawn border
                            inside_range = range(king_col + 1, c -1)
                            outside_range = range(c + 1, 8)

                        else: # king is right of the pawn
                            inside_range = range(king_col - 1, c, -1)
                            outside_range = range(c-2, -1, -1)

                        for i in inside_range:
                            if self.board[r][i] != '--': # some other piece besides the en-passant pawn is blocking
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemy_color and (square[1] == 'R' or square[1] == 'Q'):
                                attacking_piece = True
                            elif square[0] != '--':
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r, c), (r+ move_amount, c - 1), self.board, is_en_passant_move= True))

        if c + 1 <= 7: # capture to the right
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[r + move_amount][c + 1][0] == enemy_color:
                    moves.append(Move((r, c), (r + move_amount, c + 1), self.board))
                if (r + move_amount, c - 1) == self.en_passant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == r:
                        if king_col > c:  # king is right of the pawn
                            # inside between king and pawn; outside range  between pawn border
                            inside_range = range(king_col + 1, c)
                            outside_range = range(c + 2, 8)

                        else:  # king is right of the pawn
                            inside_range = range(king_col - 1, c + 1, -1)
                            outside_range = range(c - 1, -1, -1)

                        for i in inside_range:
                            if self.board[r][i] != '--':  # some other piece besides the en-passant pawn is blocking
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[r][i]
                            if square[0] == enemy_color and (square[1] == 'R' or square[1] == 'Q'):
                                attacking_piece = True
                            elif square[0] != '--':
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((r, c), (r + move_amount, c - 1), self.board, is_en_passant_move=True))




    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #cant remove queen from pin on rook moves, only remove it from bishops moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1,0), (0,-1), (1,0), (0,1))
        enemy_color = 'b' if self.white_to_move else 'w'

        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction ==(-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                            break
                        else:  # hit friendly piece
                            break
                else: #off the baor
                    break


    def get_bishop_moves(self, r, c, moves):

        piece_pinned = False
        pin_direction = ()

        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1,1)) # four diagonals
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):

                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r,c), (end_row, end_col), self.board))
                            break
                        else:  # hit friendly piece
                            break
                else:
                    break



    def get_knight_moves(self, r, c, moves):
        '''
        Get all the knight moves for the knight located at row col and add the moves to the list.
        '''

        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))

        ally_color = 'w' if self.white_to_move else 'b'
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row <= 7  and 0 <= end_col <= 7:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color:
                        moves.append(Move((r,c), (end_row, end_col), self.board))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)


    def get_king_moves(self, r, c, moves):

        '''
        Get all the king moves for the king located at row col and add the moves to the list
        '''

        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.white_to_move else 'b'

        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:

                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_check()

                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))

                    if ally_color == 'w':
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)


    def get_castle_moves(self, r, c, moves, ally_color):
        if self.in_check():
            return #cannot castle while in check

        if (self.white_to_move and self.current_castling_rights.wks and r == 7) or (not self.white_to_move and self.current_castling_rights.bks and r == 1):
            return self.get_kingside_castle_moves(r, c, moves)

        if (self.white_to_move and self.current_castling_rights.wqs) or (not self.white_to_move and self.current_castling_rights.bqs):
            return self.get_queenside_castle_moves(r, c, moves)

    def get_castle_moves(self, row, col, moves):
        """
        Generate all valid castle moves for the king at (row, col) and add them to the list of moves.
        """
        if self.square_under_attack(row, col):
            return  # can't castle while in check
        if (self.white_to_move and self.current_castling_rights.wks) or (
                not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(row, col, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (
                not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(row, col, moves)


    def get_kingside_castle_moves(self, row, col, moves):
        if self.board[row][col + 1] == '--':
            if self.board[row][col + 2] == '--':
                if not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                    moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))

class CastlingRights:

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():

    rank_to_rows= {'1': 7,
                   '2': 6,
                   '3': 5,
                   '4': 4,
                   '5': 3,
                   '6': 2,
                   '7': 1,
                   '8': 0}

    rows_to_rank = {v: k for k, v in rank_to_rows.items()}

    files_to_cols = {'a': 0,
                     'b': 1,
                     'c': 2,
                     'd': 3,
                     'e': 4,
                     'f': 5,
                     'g': 6,
                     'h': 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}



    def __init__(self, start_sq, end_sq, board, is_en_passant_move = False, is_castle_move = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7)

        #en passant
        self.is_en_passant_move = is_en_passant_move
        if self.is_en_passant_move:
            self.piece_captured = 'wp' if self.piece_moved == 'bp' else 'bp'

        # capture

        self.is_capture = self.piece_captured != '--'

        # castle move

        self.is_castle_move = is_castle_move


        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
    

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)


    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_rank[r]

    # overriding the str() function

    def __str__(self):
        # castle move

        if self.is_castle_move:
            return "O-O" if self.end_col == 6 else "O-O-O"

        end_sq = self.get_rank_file(self.end_row, self.end_col)

        #pawn moves
        if self.piece_moved[1] == 'p':
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_sq + " "
            else:
                return end_sq

        #pawn promotion

        # two of the same type of piece moving to a square, Nbd2 if both knights can move to d2

        # also adding + for check move and # for checkmate

        # piece moves

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += 'x'

        return move_string + end_sq + " "






