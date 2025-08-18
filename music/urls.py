from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.user_login, name="login"), 
    path("logout", views.logout, name="logout"),
    path("musician/", views.musician, name="musician"),  # Include musician-related URLs
    path("song/", views.song, name="song"),  # Include song-related URLs
    path("songs/", views.song_list, name="song_list"),
    path("playlist/", views.playlist, name="playlist"),  # Include playlist-related URLs
    path('songs/<int:song_id>/', views.song_detail, name="song_detail"),
    path('songs/<int:song_id>/like/', views.like_song, name='like_song'),
    path("search/", views.search, name="search_results"),
    path("comment/<int:song_id>/", views.add_comment, name="add_comment"),
    path('songs/<int:song_id>/comment/', views.comment_song, name='comment_song'),
    path("song_cover/<int:song_id>/", views.song_cover, name="song_cover"),
]