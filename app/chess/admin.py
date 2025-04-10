from django.contrib import admin
from .models import ChessGame, ChessMove

@admin.register(ChessGame)
class ChessGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'white_player', 'black_player', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('white_player__username', 'black_player__username')

@admin.register(ChessMove)
class ChessMoveAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'move_number', 'player', 'move_notation', 'created_at')
    list_filter = ('game', 'player')
    search_fields = ('move_notation', 'player__username')
