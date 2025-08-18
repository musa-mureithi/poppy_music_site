from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
import re
from .models import Song
import requests
import urllib.parse
from .models import Song, Comment, Like, Musician
from .forms import CommentForm
from django.db.models import Prefetch
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Song, Comment
from django.db.models.signals import post_save
from django.dispatch import receiver
from user_agents import parse

# from django.urls import reverse
# from django.contrib.auth.decorators import login_required


# Create your views here.
def index(request):
    return render( request, "index.html")

def register(request):
    if request.method == "POST":
        Username = request.POST.get("username")
        email = request.POST.get("email")
        password =request.POST.get("password")
        password2 = request.POST.get("password2")
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email Already Used")
                return redirect("register")
            elif User.objects.filter(username=Username).exists():
                messages.error(request, "Username Already Used")
                return redirect("register")
            elif len(password) < 6:
                messages.error(request, "Password is Too Short")
                return redirect("register")
            elif not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
                messages.error(request, "Password Not Strong")
                return redirect("register")
            else:
                User.objects.create_user(username=Username, email=email, password=password)
                messages.success(request, "Registration Success")
                return redirect("login")
        else:
            messages.error(request, "Passwords Do Not Match")
            return redirect("register")

    return render (request, "register.html")    
    


def user_login(request):
    if request.method == "POST":
        Username = request.POST.get("username")
        password = request.POST.get("password")
        User = auth.authenticate(username=Username, password=password)
        
        if User is not None:
            auth.login(request, User)

            # ⬇️ New: Extract User-Agent and parse it
            ua_string = request.META.get('HTTP_USER_AGENT', '')
            user_agent = parse(ua_string)

            # Log or print the device and OS info
            print("Device:", user_agent.device.family)
            print("OS:", user_agent.os.family)
            print("OS Version:", user_agent.os.version)

            return redirect('index')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect("login")

    return render(request, "login.html")


def logout (request):
    auth.logout(request)
    return redirect("index")     

@login_required
def musician(request):
    # Ensure a musician profile exists
    musician, created = Musician.objects.get_or_create(
        user=request.user,
        defaults={'name': request.user.username}
    )

    if request.method == "POST":
        bio = request.POST.get("bio")
        profile_picture = request.FILES.get("profile_picture")

        if not bio:
            messages.error(request, "Bio cannot be empty.")
            return redirect("musician")

        musician.bio = bio
        if profile_picture:
            musician.profile_picture = profile_picture
        musician.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("musician")

    return render(request, "musician.html", {"musician": musician})

@receiver(post_save, sender=User)
def create_musician(sender, instance, created, **kwargs):
    if created:
        Musician.objects.create(user=instance, name=instance.username)


def song(request):
    if request.method =="POST":
        title = request.POST.get("title")
        artist = request.POST.get("artist")
        album = request.POST.get("album")
        release_date = request.POST.get("release_date")
        audio_file = request.FILES.get("audio_file")
        cover_image = request.FILES.get("cover_image")

        if not title or not artist or not audio_file:
            messages.error(request, "Title, Artist, and Audio file are required.")
            return redirect("song")

        # Assuming you have a Song model
        song = song(
            title=title,
            artist=artist,
            album=album,
            release_date=release_date,
            audio_file=audio_file,
            cover_image=cover_image
        )
        song.save()

        messages.success(request, "Song added successfully.")
        return redirect("song")
    return render(request, "song.html")


def song_list(request):
    song = Song.objects.all().prefetch_related(
        Prefetch(
            'comments',
            queryset=Comment.objects.select_related('user').order_by('-created_at')[:3],
            to_attr='recent_comments'
        )
    )
    liked_songs = []
    if request.user.is_authenticated:
        liked_songs = Like.objects.filter(user=request.user).values_list('song_id', flat=True)
    return render(request, 'song_list.html', {
        'songs': song,
        'liked_songs': liked_songs,
    })




def song_detail(request, song_id):
    song = get_object_or_404(Song, id=song_id)

    # Fetch Apple Music info
    query = f"{song.title} {song.artist}"
    encoded_query = urllib.parse.quote_plus(query)

    response = requests.get(f"https://itunes.apple.com/search?term={encoded_query}&entity=song&limit=1")

    apple_data = None
    if response.status_code == 200:
        results = response.json().get("results", [])
        if results:
            result = results[0]
            apple_data = {
                "track_name": result.get("trackName"),
                "artist_name": result.get("artistName"),
                "album_name": result.get("collectionName"),
                "genre": result.get("primaryGenreName"),
                "release_date": result.get("releaseDate")[:10],
                "apple_music_url": result.get("trackViewUrl"),
                "artwork": result.get("artworkUrl100"),
            }

    # Handle comment form
    if request.method == "POST" and "comment_submit" in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.song = song
            comment.save()
            return redirect("song_detail", song_id=song.id)
    else:
        comment_form = CommentForm()

    # Handle likes
    liked = False
    if request.user.is_authenticated:
        liked = Like.objects.filter(song=song, user=request.user).exists()
        if request.method == "POST" and "like_submit" in request.POST and not liked:
            Like.objects.create(song=song, user=request.user)
            liked = True

    comments = song.comments.all().order_by("-created_at")
    like_count = song.likes.count()

    return render(request, "song_detail.html", {
        "songs": song,
        "apple_data": apple_data,
        "comment_form": comment_form,
        "comments": comments,
        "liked": liked,
        "like_count": like_count
    })

@login_required
def like_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    user = request.user

    existing_like = Like.objects.filter(song=song, user=user).first()

    if existing_like:
        existing_like.delete()
        liked = False
    else:
        Like.objects.create(song=song, user=user)
        liked = True

    like_count = Like.objects.filter(song=song).count()

    return JsonResponse({
        'success': True,
        'like_count': like_count,
        'liked': liked,
    })


def playlist(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        owner = request.user.musician  # Assuming the user is authenticated and has a Musician profile
        songs = request.POST.getlist("songs")  # Assuming you have a way to select multiple songs

        if not name:
            messages.error(request, "Playlist name cannot be empty.")
            return redirect("playlist")

        # Assuming you have a Playlist model
        playlist = Playlist(name=name, description=description, owner=owner)
        playlist.save()

        for song_id in songs:
            song = Song.objects.get(id=song_id)
            playlist.songs.add(song)

        messages.success(request, "Playlist created successfully.")
        return redirect("playlist")

    return render(request, "playlist.html")
def search(request):
    query = request.GET.get("q", "")
    if query:
        songs = Song.objects.filter(title__icontains=query)
    else:
        songs = Song.objects.none()  # No results if no query

    return render(request, "search_results.html", {"songs": songs, "query": query})
def about(request):
    return render(request, "about.html")

def comment(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    comments = song.comments.all()  # Assuming you have a related_name 'comments' in your Comment model
    return render(request, "comment.html", {"song": song, "comments": comments})


@login_required
def add_comment(request, song_id):
    song= get_object_or_404(Song, id=song_id)
    content = request.POST.get('content')
    if content:
        comment = Comment.objects.create(
            song=song,
            user=request.user,
            content=content
        )
        return JsonResponse({
            'success': True,
            'username': comment.user.username,
            'content': comment.content,
        })
    return JsonResponse({'success': False})

@login_required
def comment_song(request, song_id):
    if request.method == 'POST':
        song = get_object_or_404(Song, id=song_id)
        content = request.POST.get('content', '').strip()

        if content:
            comment = Comment.objects.create(
                song=song,
                user=request.user,
                content=content
            )
            return JsonResponse({
                'success': True,
                'username': request.user.username,
                'content': comment.content,
            })
        else:
            return JsonResponse({'success': False, 'error': 'Empty comment'}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
@login_required
def song_cover(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    if request.method == 'POST':
        cover_image = request.FILES.get('cover_image')
        if cover_image:
            song.cover_image = cover_image
            song.save()
            messages.success(request, "Cover image updated successfully.")
        else:
            messages.error(request, "No cover image provided.")
        return redirect('song_detail', song_id=song.id)
    return render(request, 'song_cover.html', {'song': song})

       

