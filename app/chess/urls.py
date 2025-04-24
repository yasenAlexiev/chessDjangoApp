from django.urls import path
from . import views

app_name = 'chess'

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('create/', views.create_game, name='create_game'),
    path('game/<int:game_id>/', views.play_game, name='play_game'),
    path('game/<int:game_id>/move/', views.make_move, name='make_move'),
    path('game/<int:game_id>/history/', views.game_history, name='game_history'),
    path('game/<int:game_id>/state/', views.get_game_state, name='get_game_state'),
]