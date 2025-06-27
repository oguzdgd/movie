from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase # API testleri için daha kullanışlı
from rest_framework import status
from django.contrib.auth.models import User
from .models import Movie, Comment, WatchedMovie

class MovieAPITests(APITestCase):
    # Bu sınıf, filmlerle ilgili API testlerini gruplayacak

    def setUp(self):
        """Her test fonksiyonundan önce çalışacak olan hazırlık metodu."""
        # Testler için örnek bir film oluşturalım
        self.movie = Movie.objects.create(
            movie_id='test001',
            title='Test Movie',
            year=2024,
            director='Test Director',
            plot='A movie for testing purposes.',
            rating=8.0
        )
        # Testler için bir normal kullanıcı ve bir admin kullanıcı oluşturalım
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.admin = User.objects.create_superuser(username='adminuser', password='password123', email='admin@test.com')

  
    def test_get_movie_list(self): # Adını daha genel yapalım
        """Film listesinin alınabildiğini test et."""
        url = reverse('api:movie-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF XML Renderer varsayılan olarak <root><list-item>... yapısını kullanır
        # Bu yüzden içeriği kontrol etmek biraz daha karmaşık olabilir, şimdilik durum kodu yeterli.

    def test_get_movie_detail(self):
        """Belirli bir filmin detaylarının alınabildiğini test et."""
        url = reverse('api:movie-detail', kwargs={'movie_id': self.movie.movie_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF Response nesnesi XML'e render edildiği için .content kullanmalıyız
        self.assertIn(b'<title>Test Movie</title>', response.content)

    def test_create_movie_unauthorized(self):
        """Yetkisiz bir kullanıcının (giriş yapmış ama admin olmayan) film oluşturamadığını test et."""
        url = reverse('api:movie-list-create')
        self.client.force_authenticate(user=self.user)
        
        # DRF Serializer'ın beklediği veri formatı bir sözlüktür.
        # Test client'ı bunu otomatik olarak XML'e çevirecektir.
        data = {
            "movie_id": "test002",
            "title": "Unauthorized Movie",
            "year": 2025
        }
        response = self.client.post(url, data, format='xml')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_movie_authorized(self):
        """Yetkili bir admin kullanıcısının film oluşturabildiğini test et."""
        url = reverse('api:movie-list-create')
        self.client.force_authenticate(user=self.admin)
        
        data = {
            "movie_id": "test002",
            "title": "Authorized Movie",
            "year": 2025
        }
        response = self.client.post(url, data, format='xml')
        # Hatanın ne olduğunu görmek için (eğer hala hata verirse)
        # if response.status_code != status.HTTP_201_CREATED:
        #     print(response.data) # DRF Response nesnesi .data özelliğine sahiptir
            
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Movie.objects.filter(movie_id='test002').exists())

    def test_delete_movie_authorized(self):
        """Yetkili bir admin kullanıcısının film silebildiğini test et."""
        url = reverse('api:movie-detail', kwargs={'movie_id': self.movie.movie_id})
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Movie.objects.filter(movie_id=self.movie.movie_id).exists())


# -----------------------------------------------------------------------------
#                   KULLANICI VE KİMLİK DOĞRULAMA TESTLERİ
# -----------------------------------------------------------------------------
class UserAuthAPITests(APITestCase):

    def test_user_registration(self):
        """Yeni bir kullanıcının başarılı bir şekilde kaydolabildiğini test et."""
        url = reverse('api:register-user')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123"
        }
        response = self.client.post(url, data, format='xml')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Yanıtta token'ın gelip gelmediğini kontrol et
        self.assertIn('token', response.data)
        # Veritabanında kullanıcı oluşmuş mu?
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_login(self):
        """Mevcut bir kullanıcının giriş yapıp token alabildiğini test et."""
        # Önce bir kullanıcı oluşturalım
        User.objects.create_user(username='loginuser', password='password123')
        
        url = reverse('api:api-token-auth') # DRF'nin hazır login view'ı
        data = {
            "username": "loginuser",
            "password": "password123"
        }
        # DRF'nin login view'ı JSON ile daha iyi çalışır, formatı belirtelim
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


# -----------------------------------------------------------------------------
#                   İZLENENLER LİSTESİ VE YORUM TESTLERİ
# -----------------------------------------------------------------------------
class InteractionAPITests(APITestCase):

    def setUp(self):
        """Bu test sınıfı için gerekli olan kullanıcı ve film nesnelerini oluştur."""
        self.user = User.objects.create_user(username='interactionuser', password='password123')
        self.movie = Movie.objects.create(movie_id='interaction001', title='Interaction Movie')
        # Test istemcisini bu kullanıcı ile authenticate edelim.
        # Bu, her test metodunda tekrar tekrar authenticate olmamızı engeller.
        self.client.force_authenticate(user=self.user)

    def test_add_movie_to_watched_list(self):
        """Giriş yapmış bir kullanıcının izlenenler listesine film ekleyebildiğini test et."""
        url = reverse('api:watched-list')
        data = {
            "movie": self.movie.movie_id, # Modelin ID'sini gönderiyoruz
            "user_rating": "8.5"
        }
        response = self.client.post(url, data, format='xml')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Veritabanında kayıt oluşmuş mu diye kontrol edelim
        self.assertTrue(WatchedMovie.objects.filter(user=self.user, movie=self.movie).exists())
        
    def test_get_watched_list(self):
        """Giriş yapmış bir kullanıcının kendi izlenenler listesini görebildiğini test et."""
        # Önce listeye bir film ekleyelim
        WatchedMovie.objects.create(user=self.user, movie=self.movie)
        
        url = reverse('api:watched-list')
        response = self.client.get(url, format='xml')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Yanıtın içinde eklediğimiz filmin başlığı var mı?
        self.assertIn(b'<movie_title>Interaction Movie</movie_title>', response.content)

    def test_add_comment_to_movie(self):
        """Giriş yapmış bir kullanıcının bir filme yorum yapabildiğini test et."""
        url = reverse('api:comment-list-create', kwargs={'movie_id': self.movie.movie_id})
        data = {
            "body": "This is a test comment."
        }
        response = self.client.post(url, data, format='xml')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['body'], 'This is a test comment.')
        # Veritabanında yorum oluşmuş mu?
        self.assertTrue(Comment.objects.filter(author=self.user, movie=self.movie).exists())

    def test_get_movie_comments(self):
        """Bir filme ait yorumların listelenebildiğini test et."""
        # Önce bir yorum ekleyelim
        Comment.objects.create(author=self.user, movie=self.movie, body="Another test comment.")
        
        url = reverse('api:comment-list-create', kwargs={'movie_id': self.movie.movie_id})
        response = self.client.get(url, format='xml')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'<body>Another test comment.</body>', response.content)
