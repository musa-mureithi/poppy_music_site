from django import forms
from django.contrib.auth.models import User
from .models import Musician, Song, Playlist, Comment
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data
class MusicianProfileForm(forms.ModelForm):
    class Meta:
        model = Musician
        fields = ['bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'album', 'release_date', 'audio_file', 'cover_image']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
        }
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'songs']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if not username or not password:
            raise forms.ValidationError("Both fields are required.")

        return cleaned_data
class PasswordResetForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No user with this email address exists.")
        return email
class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, required=True)
    new_password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError("New passwords do not match.")

        return cleaned_data