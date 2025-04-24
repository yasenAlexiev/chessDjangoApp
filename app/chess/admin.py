from django.contrib import admin
from .models import ChessGame

@admin.register(ChessGame)
class ChessGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'white_player', 'black_player', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('white_player__username', 'black_player__username')
