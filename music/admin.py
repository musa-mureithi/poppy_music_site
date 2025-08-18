from django.contrib import admin
from django.urls import path, include
from .models import Musician, Song, Playlist, Comment, Like



# Register your models here.
@admin.register(Musician)
class MusicianAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username',)
@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'release_date')
    search_fields = ('title', 'artist__user__username')
    list_filter = ('release_date',)
@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    search_fields = ('name', 'owner__user__username')
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('song', 'user', 'created_at')
    search_fields = ('song__title', 'user__username')
@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('song', 'user')
    search_fields = ('song__title', 'user__username')
    
    