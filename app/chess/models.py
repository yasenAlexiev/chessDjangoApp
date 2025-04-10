from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ChessGame(models.Model):
    WHITE = 'W'
    BLACK = 'B'
    COLOR_CHOICES = [
        (WHITE, 'White'),
        (BLACK, 'Black'),
    ]

    PENDING = 'P'
    IN_PROGRESS = 'I'
    WHITE_WON = 'WW'
    BLACK_WON = 'BW'
    DRAW = 'D'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (WHITE_WON, 'White Won'),
        (BLACK_WON, 'Black Won'),
        (DRAW, 'Draw'),
    ]

    white_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_games')
    black_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_games')
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    current_fen = models.CharField(max_length=100, default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')  # Starting position in FEN notation

    def __str__(self):
        return f"Game {self.id}: {self.white_player} vs {self.black_player}"

class ChessMove(models.Model):
    game = models.ForeignKey(ChessGame, on_delete=models.CASCADE, related_name='moves')
    move_number = models.PositiveIntegerField()
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    move_notation = models.CharField(max_length=10)  # e.g., "e2e4", "Nf3", etc.
    fen_after_move = models.CharField(max_length=100)  # FEN notation after the move
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['game', 'move_number']

    def __str__(self):
        return f"Move {self.move_number} in Game {self.game.id}: {self.move_notation}"
