from rest_framework import serializers
from . models import Music, Artist, Album, Genre
class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio', 'profile_picture']
class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'release_date', 'cover_image']
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']
class MusicSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Music
        fields = ['id', 'title', 'artist', 'album', 'release_date', 'audio_file', 'cover_image', 'genres']
    read_only_fields = ['id', 'release_date']
    def create(self, validated_data):
        genres_data = validated_data.pop('genres', [])
        music = Music.objects.create(**validated_data)
        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(**genre_data)
            music.genres.add(genre)
        return music
    def update(self, instance, validated_data):
        genres_data = validated_data.pop('genres', [])
        instance.title = validated_data.get('title', instance.title)
        instance.artist = validated_data.get('artist', instance.artist)
        instance.album = validated_data.get('album', instance.album)
        instance.audio_file = validated_data.get('audio_file', instance.audio_file)
        instance.cover_image = validated_data.get('cover_image', instance.cover_image)
        instance.save()

        # Update genres
        if genres_data:
            instance.genres.clear()
            for genre_data in genres_data:
                genre, created = Genre.objects.get_or_create(**genre_data)
                instance.genres.add(genre)

        return instance
    def validate(self, data):
        if not data.get('title'):
            raise serializers.ValidationError("Title is required.")
        if not data.get('artist'):
            raise serializers.ValidationError("Artist is required.")
        if not data.get('audio_file'):
            raise serializers.ValidationError("Audio file is required.")
        return data
from .models import Music, Artist, Album, Genre
class MusicDetailSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Music
        fields = ['id', 'title', 'artist', 'album', 'release_date', 'audio_file', 'cover_image', 'genres']
        read_only_fields = ['id', 'release_date']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['artist'] = ArtistSerializer(instance.artist).data
        representation['album'] = AlbumSerializer(instance.album).data
        representation['genres'] = GenreSerializer(instance.genres.all(), many=True).data
        return representation
class ArtistDetailSerializer(serializers.ModelSerializer):
    music = MusicSerializer(many=True, read_only=True)

    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio', 'profile_picture', 'music']
        read_only_fields = ['id']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['music'] = MusicSerializer(instance.music.all(), many=True).data
        return representation
class AlbumDetailSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    music = MusicSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'release_date', 'cover_image', 'music']
        read_only_fields = ['id']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['artist'] = ArtistSerializer(instance.artist).data
        representation['music'] = MusicSerializer(instance.music.all(), many=True).data
        return representation
class GenreDetailSerializer(serializers.ModelSerializer):
    music = MusicSerializer(many=True, read_only=True)

    class Meta:
        model = Genre
        fields = ['id', 'name', 'music']
        read_only_fields = ['id']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['music'] = MusicSerializer(instance.music.all(), many=True).data
        return representation
from .models import Music, Artist, Album, Genre
class MusicListSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Music
        fields = ['id', 'title', 'artist', 'album', 'release_date', 'audio_file', 'cover_image', 'genres']
        read_only_fields = ['id', 'release_date']
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['artist'] = ArtistSerializer(instance.artist).data
        representation['album'] = AlbumSerializer(instance.album).data
        representation['genres'] = GenreSerializer(instance.genres.all(), many=True).data
        return representation