from rest_framework import serializers
from .models import Movie, WatchedMovie, Comment
from django.contrib.auth.models import User

# --- Kullanıcı Serializer'ları ---
class UserSerializer(serializers.ModelSerializer):
    """Sadece temel kullanıcı bilgilerini göstermek için."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserRegisterSerializer(serializers.ModelSerializer):
    """Kullanıcı kaydı için. Şifreyi de alır ama asla geri döndürmez."""
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}} # Şifre sadece yazılabilir olsun

    def create(self, validated_data):
        # create_user metodu şifreyi otomatik olarak hash'ler.
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

# --- Film Serializer'ı ---
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__' # Modeldeki tüm alanları dahil et

# --- Yorum Serializer'ı ---
class CommentSerializer(serializers.ModelSerializer):
    # Yorum listelerken yazarın adını da görmek için.
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'movie', 'author', 'author_username', 'body', 'created_at']
        # Yorum oluştururken yazar bilgisi request'ten alınacağı için read_only yapıyoruz.
        read_only_fields = ('author','movie')

# --- İzlenenler Listesi Serializer'ı ---
class WatchedMovieSerializer(serializers.ModelSerializer):
    # Listenen filmin başlığını göstermek için.
    movie_title = serializers.CharField(source='movie.title', read_only=True)

    class Meta:
        model = WatchedMovie
        fields = ['id', 'user', 'movie', 'movie_title', 'watched_date', 'user_rating']
        read_only_fields = ('user',)