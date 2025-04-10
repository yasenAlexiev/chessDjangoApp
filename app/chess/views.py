from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import ChessGame, ChessMove
from django.contrib.auth.models import User
from django.db import models

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
    if request.method == 'POST':
        opponent_username = request.POST.get('opponent')
        try:
            opponent = User.objects.get(username=opponent_username)
            game = ChessGame.objects.create(
                white_player=request.user,
                black_player=opponent,
                status=ChessGame.PENDING
            )
            return redirect('chess:play_game', game_id=game.id)
        except User.DoesNotExist:
            return render(request, 'chess/create_game.html', {
                'error': 'Opponent not found'
            })
    
    return render(request, 'chess/create_game.html')

@login_required
def play_game(request, game_id):
    game = get_object_or_404(ChessGame, id=game_id)
    
    # Check if user is part of this game
    if request.user not in [game.white_player, game.black_player]:
        return redirect('game_list')
    
    # Get all moves for this game
    moves = game.moves.all().order_by('move_number')
    
    return render(request, 'chess/play_game.html', {
        'game': game,
        'moves': moves,
        'is_white': request.user == game.white_player
    })

@login_required
@require_http_methods(['POST'])
def make_move(request, game_id):
    game = get_object_or_404(ChessGame, id=game_id)
    
    # Check if it's the user's turn
    if request.user not in [game.white_player, game.black_player]:
        return JsonResponse({'error': 'Not part of this game'}, status=403)
    
    move_notation = request.POST.get('move')
    fen_after_move = request.POST.get('fen')
    
    if not move_notation or not fen_after_move:
        return JsonResponse({'error': 'Invalid move data'}, status=400)
    
    # Create the move
    move = ChessMove.objects.create(
        game=game,
        move_number=game.moves.count() + 1,
        player=request.user,
        move_notation=move_notation,
        fen_after_move=fen_after_move
    )
    
    # Update game status if needed (you might want to add game end detection logic here)
    game.current_fen = fen_after_move
    game.save()
    
    return JsonResponse({
        'success': True,
        'move': {
            'id': move.id,
            'notation': move.move_notation,
            'player': move.player.username,
            'created_at': move.created_at.isoformat()
        }
    })

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
