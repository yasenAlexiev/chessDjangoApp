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
    move_history = models.TextField(default='[]')  # Store move history as JSON string
    current_turn = models.CharField(max_length=5, default='white')  # Track whose turn it is

    def __str__(self):
        return f"Game {self.id}: {self.white_player} vs {self.black_player}"


class ChessMove(models.Model):
    game = models.ForeignKey(ChessGame, on_delete=models.CASCADE, related_name='moves')
    move_number = models.PositiveIntegerField()  # Move number in the game
    from_square = models.CharField(max_length=2)  # Starting square (e.g., "e2")
    to_square = models.CharField(max_length=2)  # Ending square (e.g., "e4")
    piece = models.CharField(max_length=10)  # Piece moved (e.g., "pawn", "knight")
    captured_piece = models.CharField(max_length=10, null=True, blank=True)  # Captured piece, if any
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Move {self.move_number}: {self.piece} from {self.from_square} to {self.to_square}"

