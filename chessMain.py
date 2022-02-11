import SmartMoveFinder, chessEngine
import pygame as p
import sys
import time
from multiprocessing import Process, Queue

DIMENSION = 8
BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 300
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
GAME_STATUS_HEIGHT = BOARD_HEIGHT // 4
GAME_STATUS_WIDTH = BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


'''
Responsible for all the graphics within a current game state
'''
def draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font):
    draw_board(screen)
    hightlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)
    draw_move_log(screen, gs, move_log_font)
    draw_game_state_status(screen, gs, move_log_font)

'''
Draw the squares on the board. The top left square is always lights
'''
def draw_board(screen):
    colors = [p.Color("Light Green"), p.Color("Dark Green")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

''' 
Highlight square selected and moves for piece selected
'''

def hightlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transperancy -> 0 transparent, 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # hightlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))



def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece  != '--':
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_game_state_status(screen, gs, font):
    game_state_status_rect = p.Rect(0, BOARD_HEIGHT, GAME_STATUS_WIDTH, GAME_STATUS_HEIGHT)
    p.draw.rect(screen, p.Color('Light Yellow'), game_state_status_rect)
    Header1 = "Top engine moves"

    check_text = f"In check?  {'YES' if (gs.in_check_flag) else 'NO'}"
    checkmate_text = f"Checkmate? {'YES' if gs.checkmate else 'NO'}"
    stalemate_text =  f"Stalemate? {'YES' if gs.stalemate else 'NO'}"
    text_object1 = font.render(check_text, False, p.Color('Red') if gs.in_check_flag else p.Color('Green'))
    text_object2 = font.render(checkmate_text, False, p.Color('Red') if gs.checkmate else p.Color('Green'))
    text_object3 = font.render(stalemate_text, False, p.Color('Red') if gs.stalemate else p.Color('Green'))

    padding = 5
    textY = padding
    text_location1 = game_state_status_rect.move(padding, textY)
    text_location2 = game_state_status_rect.move(padding, textY * 4)
    text_location3 = game_state_status_rect.move(padding, textY * 8)

    screen.blit(text_object1, text_location1)
    screen.blit(text_object2, text_location2)
    screen.blit(text_object3, text_location3)


def draw_move_log(screen, gs, font):

    move_log_rect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('Black'), move_log_rect)
    move_log = gs.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i //2 + 1) + ". " + str(move_log[i]) + " "
        if i + 1 < len(move_log): # make sure black made a move
            move_string += str(move_log[i+1]) + " "
        move_texts.append(move_string)
    moves_per_row = 3
    padding = 5
    textY = padding
    line_spacing = 2
    for i in range(0, len(move_texts), moves_per_row):
        text = ""

        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i+j]



        text_object = font.render(text, True, p.Color('White'))
        text_location = move_log_rect.move(padding, textY)
        screen.blit(text_object, text_location)
        textY += text_object.get_height() + line_spacing
    #text_object = font.render(text, 0, p.Color('Black'))
    #screen.blit(text_object, text_location.move(2,2))


def animate_move(move, screen, board, clock):
    colors = [p.Color("white"), p.Color("gray")]

    print('Animate: ')
    print(move)

    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 10
    frame_count = (abs(dR)+abs(dC)) * frames_per_square
    for frame in range(frame_count+1):
        r, c = (move.start_row + dR*frame/frame_count, move.start_col + dC*frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from the ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            if move.is_en_passant_move:
                en_passant_row = move.end_row + 1 if move.piece_moved[0] == 'b' else move.end_row -1
                end_square = p.Rect(move.end_col * SQ_SIZE, en_passant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)

            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw the move
        if move.piece_moved != '--':
            screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(300)

# highlight square selected and possible moves for piece selected





def draw_end_game_text(screen, text):
    font = p.font.SysFont('Helvetica', 32, True, False)
    text_object = font.render(text, 0, p.Color('Black'))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2, BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Black'))
    screen.blit(text_object, text_location.move(2,2))


def main():

    p.init()
    screen = p.display.set_mode((BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT + GAME_STATUS_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False #flag variable for when a move is made
    animate = False #flag variable for when we should animate a move
    load_images()
    running = True
    sq_selected = () #tuple : (row, col)
    player_clicks = [] # two tuples: [(6, 4), (4,4)] from -> to
    game_over = False
    ai_thinking = False
    move_undone = False
    move_finder_process = None
    move_log_font = p.font.SysFont('Arial', 15, False, False)


    player_one = False    # True if human is playing white, False if computer is playing
    player_two = False # True if human is playing black, False if computer is playing


    while running:

        human_turn = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sq_selected == (row,col) or col >= 8 or row >= 8: #the user clicked the same square twice or user clicked mouse log
                        sq_selected = () # deselect
                        player_clicks = [] # clear clicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected) #append for both 1st and 2nd clicks
                    if len(player_clicks) == 2 and human_turn:
                        move = chessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = () # reset user clicks
                                player_clicks = [] # clear clicks
                        if not move_made:
                            player_clicks = [sq_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True

                if e.key == p.K_r:
                    gs = chessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = False



        # AI move finder logic

        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True

                return_queue = Queue() # used to pass data between threads
                move_finder_process = Process(target = SmartMoveFinder.find_best_move, args = (gs, valid_moves, return_queue))
                move_finder_process.start() # call the find_best_move(gs, valid_moves, return_queue)

            if not move_finder_process.is_alive():
                print('Done thinking!')
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = SmartMoveFinder.find_random_move(valid_moves)
                gs.make_move(ai_move)
                move_made = True
                animate = True
                ai_thinking = False



        if move_made:
            if animate:
                animate_move(gs.move_log[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            print('FEN: ', gs.board_to_fen(gs.board))

        draw_game_state(screen, gs, valid_moves, sq_selected, move_log_font)

        if gs.checkmate:
            game_over = True
            draw_end_game_text(screen, 'Stalemate' if gs.stalemate else 'Black wins by checkmate' if gs.white_to_move else 'White wins by checkmate')
        if  gs.draw_by_insufficient_material:
            game_over = True
            draw_end_game_text(screen, 'Draw by insufficient material')
        clock.tick(MAX_FPS)
        p.display.flip()



if __name__ == "__main__":



    main()

# FIX LIST:

# En passant to the right doesn't work
# Castling is still an issue
# some out of range-problems
# AI sucks :)
# checks with knights stops the game without checkmate or stalemate or anything. Only the black knight?

# empty range for randrage when length of valid moves is 1 or 0 (?) when using the random move
# king can be captured by knight, same problem as two above?
# chekmate with rooks gives empty range