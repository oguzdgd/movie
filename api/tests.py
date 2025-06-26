from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase # API testleri için daha kullanışlı
from rest_framework import status
from django.contrib.auth.models import User
from .models import Movie

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

    def test_get_movie_list_unauthenticated(self):
        """Kimlik doğrulaması olmadan film listesinin alınabildiğini test et."""
        url = reverse('api:movie-list-create') # URL'i ismiyle al (daha güvenli)
        response = self.client.get(url, format='xml') # DRF'nin test istemcisi
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Yanıtın XML olup olmadığını da kontrol edebiliriz
        self.assertEqual(response.accepted_media_type, 'application/xml')

    def test_get_movie_detail(self):
        """Belirli bir filmin detaylarının doğru bir şekilde alınıp alınmadığını test et."""
        url = reverse('api:movie-detail', kwargs={'movie_id': self.movie.movie_id})
        response = self.client.get(url, format='xml')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Yanıtın içinde film başlığının geçip geçmediğini kontrol edelim
        self.assertIn(b'<title>Test Movie</title>', response.content)

    def test_create_movie_unauthorized(self):
        """Yetkisiz bir kullanıcının (giriş yapmış ama admin olmayan) film oluşturamadığını test et."""
        url = reverse('api:movie-list-create')
        # Önce kullanıcıyı login yapıp token alalım (DRF test client ile kolay)
        self.client.force_authenticate(user=self.user)
        
        xml_data = """
        <movie id="test002">
            <title>Unauthorized Movie</title>
            <year>2025</year>
        </movie>
        """
        response = self.client.post(url, data=xml_data, content_type='application/xml')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_movie_authorized(self):
        """Yetkili bir admin kullanıcısının film oluşturabildiğini test et."""
        url = reverse('api:movie-list-create')
        # Admin kullanıcı ile authenticate ol
        self.client.force_authenticate(user=self.admin)
        
        xml_data = """
        <movie id="test002">
            <title>Authorized Movie</title>
            <year>2025</year>
        </movie>
        """
        response = self.client.post(url, data=xml_data, content_type='application/xml')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Veritabanında gerçekten oluşmuş mu diye kontrol et
        self.assertTrue(Movie.objects.filter(movie_id='test002').exists())

    def test_delete_movie_authorized(self):
        """Yetkili bir admin kullanıcısının film silebildiğini test et."""
        url = reverse('api:movie-detail', kwargs={'movie_id': self.movie.movie_id})
        # Admin kullanıcı ile authenticate ol
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Veritabanından gerçekten silinmiş mi diye kontrol et
        self.assertFalse(Movie.objects.filter(movie_id=self.movie.movie_id).exists())
