import random

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
piece_scores = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.2, 0.2, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.5, 0.5, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wp": pawn_scores,
                         "bp": pawn_scores[::-1]}


def find_random_move(valid_moves):

    return random.choice(valid_moves)

def find_best_move_min_max_no_recursion(gs, valid_moves): # min max without recursion

    turn_multiplier = 1 if gs.white_to_move else -1
    opp_min_max_score = CHECKMATE #the opponents minimum max available score
    best_player_move = None
    random.shuffle(valid_moves)

    for player_move in valid_moves:
        gs.make_move(player_move)
        opp_moves = gs.get_valid_moves()
        if gs.stalemate:
            opp_max_score = STALEMATE
        elif gs.checkmate:
            opp_max_score = -CHECKMATE
        else:
            opp_max_score = -CHECKMATE
            for opp_move in opp_moves:
                gs.make_move(opp_move)
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_board(gs.board)
                if score > opp_max_score:
                    opp_max_score = score
                gs.undo_move()
        if opp_max_score < opp_min_max_score:
            opp_min_max_score = opp_max_score
            best_player_move = player_move
        gs.undo_move()
    return best_player_move

#  helper function to make first recursive call

def find_best_move(gs, valid_moves, return_queue):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    #find_move_min_max(gs, valid_moves, DEPTH, gs.white_to_move)
    #find_move_nega_max(gs, valid_moves, DEPTH, 1 if gs.white_to_move else -1)
    find_move_nega_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    return_queue.put(next_move)


    return next_move

def find_move_min_max(gs, valid_moves, depth, white_to_move): # find best move with min max with recursion
    global next_move


    if depth == 0:
        return score_board(gs.board)

    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs, next_moves, depth - 1, False) # False = not white_to_move (switch to blacks turn)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()

        return max_score
    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_min_max(gs, next_moves, depth - 1, True) # True = white_to_move  (switch to whites turn)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score

def find_move_nega_max(gs, valid_moves, depth, turn_multiplier):

    global next_move


    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = - CHECKMATE

    for move in valid_moves:
        gs.make_move(move)

        next_moves = gs.get_valid_moves()
        score = - find_move_nega_max(gs, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move

        gs.undo_move()
    return max_score


def find_move_nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):

    global next_move


    if depth == 0:
        return turn_multiplier * score_board(gs)
    # move ordering - implement later
    max_score = - CHECKMATE

    for move in valid_moves:
        gs.make_move(move)

        next_moves = gs.get_valid_moves()
        score = - find_move_nega_max_alpha_beta(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move

                print('MOVE: ', end= '')
                print(move)
                print('SCORE: ', end ='')
                print(round(score,4))
        gs.undo_move()
        if max_score > alpha: #pruning
            alpha = max_score

        if alpha >= beta:
            break

    return max_score



def score_board(gs):
    '''
    Score the board. A positive score is good for white, a negative score is good for black
    '''

    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    elif gs.stalemate:
        return STALEMATE # draw

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != '--':
                piece_position_score = 0
                if piece[1] != 'K':
                    piece_position_score = piece_position_scores[piece][row][col]
                if piece[0] == 'w':
                    score += piece_scores[piece[1]] + piece_position_score
                if piece[0] == 'b':
                    score -= piece_scores[piece[1]] + piece_position_score
            if piece == 'wp':
                if col > 0:
                    if gs.board[row+1][col-1] == 'wp':
                        score += 0.5
                if col < 7:
                    if gs.board[row + 1][col + 1] == 'wp':
                        score += 0.5

            if piece == 'bp':
                if col > 0:
                    if gs.board[row-1][col-1] == 'bp':
                        score -= 0.5
                if col < 7:
                    if gs.board[row-1][col+1] == 'bp':
                        score -= 0.5

    for i in range(8):
        occ_bp = 0
        occ_wp = 0
        for j in range(8):
            if gs.board[i][j] == 'bp':
                occ_bp += 1
            if gs.board[i][j] == 'wp':
                occ_wp += 1

        if occ_wp > 1:  #having more than one pawn on the same file is usually bad
            score -= 1
        if occ_bp > 1:
            score += 1

    if gs.white_has_castled:
        score += 2
    elif gs.black_has_castled:
        score -= 2



    return score





