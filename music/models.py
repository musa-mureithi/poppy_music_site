from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField

GENRE_CHOICES = [
    ('rock', 'Rock'),
    ('pop', 'Pop'),
    ('jazz', 'Jazz'),
    ('hiphop', 'Hip Hop'),
    ('classical', 'Classical'),
    ('other', 'Other'),
]

class Musician(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='other')

    def __str__(self):
        return self.name

class Album(models.Model):
    musician = models.ForeignKey(Musician, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField(max_length=100)
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} ({self.year})"

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    album = models.CharField(max_length=200, blank=True, null=True)
    release_date = models.DateField(default=timezone.now)
    audio_file = CloudinaryField(resource_type="raw", folder="songs/")
    cover_image = models.ImageField(upload_to='cover_images/', blank=True, null=True)

    def __str__(self):
        return self.title

# Add the following to enable backend actions via API
from rest_framework import serializers, viewsets

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
class Playlist(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(Musician, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Comment(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} on {self.song.title}"
class Like(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('song', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.song.title}"
    
