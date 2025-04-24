from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ChessGame, ChessMove
from django.contrib.auth.models import User
from django.db import models
import json
from django.views.decorators.csrf import csrf_exempt

def fen_to_board(fen):
    """Convert FEN string to board state"""
    # Initialize an 8x8 board with None values
    board = [[None for _ in range(8)] for _ in range(8)]
    
    # Split the FEN string to get the position part
    parts = fen.split()
    position = parts[0]
    
    # Parse the position string
    row = 0
    col = 0
    for char in position:
        if char == '/':
            # Move to the next row
            row += 1
            col = 0
        elif char.isdigit():
            # Skip empty squares
            col += int(char)
        else:
            # Place the piece
            if row < 8 and col < 8:  # Ensure we're within bounds
                # Convert the piece to the correct format (e.g., 'P' -> 'wP', 'p' -> 'bP')
                if char.isupper():
                    piece = 'w' + char
                else:
                    piece = 'b' + char.upper()
                board[row][col] = piece
                col += 1
    
    return board

def board_to_fen(board):
    """Convert board state to FEN string"""
    fen = []
    for row in board:
        empty = 0
        row_fen = ''
        for piece in row:
            if piece is None:
                empty += 1
            else:
                if empty > 0:
                    row_fen += str(empty)
                    empty = 0
                row_fen += piece
        if empty > 0:
            row_fen += str(empty)
        fen.append(row_fen)
    return '/'.join(fen)

# Create your views here.

@login_required
def game_list(request):
    # Get games where the user is either white or black player
    games = ChessGame.objects.filter(
        models.Q(white_player=request.user) | 
        models.Q(black_player=request.user)
    ).order_by('-created_at')
    
    return render(request, 'chess/game_list.html', {
        'games': games
    })

@login_required
def create_game(request):
    """
    Display the form to create a new game (GET) or handle game creation (POST).
    """
    if request.method == 'POST':
        try:
            opponent_username = request.POST.get('opponent')
            black_player = get_object_or_404(User, username=opponent_username)
            white_player = request.user
            game = ChessGame.objects.create(
                white_player=white_player,
                black_player=black_player,
                status=ChessGame.IN_PROGRESS
            )
            # Redirect to the game play page after creating the game
            return redirect('chess:play_game', game_id=game.id)
        except Exception as e:
            return render(request, 'chess/create_game.html', {
                'error': str(e)
            })
    # Render the form for GET requests
    return render(request, 'chess/create_game.html')

@login_required
def play_game(request, game_id):
    game = get_object_or_404(ChessGame, id=game_id)
    
    # Check if user is part of this game
    if request.user not in [game.white_player, game.black_player]:
        return redirect('game_list')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            if 'currentFEN' in data:
                game.current_fen = data['currentFEN']
                if 'moveHistory' in data:
                    game.move_history = json.dumps(data['moveHistory'])
                if 'currentTurn' in data:
                    game.current_turn = data['currentTurn']
                if 'status' in data:
                    game.status = data['status']
                game.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Game state updated successfully',
                    'currentTurn': game.current_turn,
                    'status': game.status
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Missing FEN data'
                }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    # Get all moves for this game
    moves = game.moves.all().order_by('move_number')
    
    # Convert FEN to board state
    board = fen_to_board(game.current_fen)
    
    # Get the move history
    move_history = []
    if game.move_history:
        try:
            move_history = json.loads(game.move_history)
        except:
            move_history = []
    
    # Convert the board to a JSON-serializable format
    board_json = json.dumps(board)
    
    return render(request, 'chess/play_game.html', {
        'game': game,
        'moves': moves,
        'is_white': request.user == game.white_player,
        'board': board_json,
        'move_history': json.dumps(move_history)
    })

@login_required
@require_http_methods(['POST'])
def make_move(request, game_id):
    game = get_object_or_404(ChessGame, id=game_id)
    
    # Check if it's the user's turn
    if request.user not in [game.white_player, game.black_player]:
        return JsonResponse({'error': 'Not part of this game'}, status=403)
    
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        from_row = data.get('from_row')
        from_col = data.get('from_col')
        to_row = data.get('to_row')
        to_col = data.get('to_col')
        
        if None in (from_row, from_col, to_row, to_col):
            return JsonResponse({'error': 'Missing move coordinates'}, status=400)
        
        # Get the current board state
        board = fen_to_board(game.current_fen)
        
        # Get the piece being moved
        piece = board[from_row][from_col]
        if not piece:
            return JsonResponse({'error': 'No piece at source position'}, status=400)
        
        # Check if it's the player's piece
        is_white_piece = piece[0] == 'w'
        is_white_player = request.user == game.white_player
        if is_white_piece != is_white_player:
            return JsonResponse({'error': 'Not your piece'}, status=400)
        
        # Check if it's the player's turn
        if (is_white_player and game.current_turn != 'white') or (not is_white_player and game.current_turn != 'black'):
            return JsonResponse({'error': 'Not your turn'}, status=400)
        
        # Make the move
        board[to_row][to_col] = piece
        board[from_row][from_col] = None
        
        # Convert board back to FEN
        new_fen = board_to_fen(board)
        
        # Create the move
        move = ChessMove.objects.create(
            game=game,
            move_number=game.moves.count() + 1,
            player=request.user,
            move_notation=f"{chr(from_col + 97)}{8 - from_row}{chr(to_col + 97)}{8 - to_row}",
            fen_after_move=new_fen
        )
        
        # Update game status
        game.current_fen = new_fen
        # Switch the turn
        game.current_turn = 'black' if game.current_turn == 'white' else 'white'
        game.save()
        
        return JsonResponse({
            'success': True,
            'board': board,
            'move': {
                'id': move.id,
                'notation': move.move_notation,
                'player': move.player.username,
                'created_at': move.created_at.isoformat()
            },
            'currentTurn': game.current_turn
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def game_history(request, game_id):
    game = get_object_or_404(ChessGame, id=game_id)
    
    # Check if user is part of this game
    if request.user not in [game.white_player, game.black_player]:
        return redirect('game_list')
    moves = game.moves.all().order_by('move_number')
    
    return render(request, 'chess/game_history.html', {
        'game': game,
        'moves': moves
    })

@login_required
def get_game_state(request, game_id):
    """
    Retrieve the current state of the game.
    """
    try:
        game = get_object_or_404(ChessGame, id=game_id)
        return JsonResponse({
            'success': True,
            'currentFEN': game.current_fen,
            'moveHistory': json.loads(game.move_history),
            'currentTurn': game.current_turn
        })
    except ChessGame.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Game not found.'})
