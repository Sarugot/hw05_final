from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exists_at_desired_location(self):
        """URL-адрес доступен неавторизованному пользователю."""
        url_names = [
            '',
            '/group/test_slug/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.id}/',
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = (
            ('', 'posts/index.html'),
            ('/group/test_slug/', 'posts/group_list.html'),
            (f'/profile/{self.user}/', 'posts/profile.html'),
            (f'/posts/{self.post.id}/', 'posts/post_detail.html'),
            ('/create/', 'posts/create_post.html'),
            (f'/posts/{self.post.id}/edit/', 'posts/create_post.html')
        )
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_create_url_exists_at_desired_location(self):
        """Страница create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_edit_url_exists_at_desired_location_authorized(self):
        """Страница posts/<int:post_id>/edit/ доступна авторизованному
        пользователю."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_404(self):
        """Несуществующая страница выдаёт ошибку 404"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_task_detail_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу posts/<int:post_id>/edit/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.client.get(f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_post_comment_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу posts/<int:post_id>/comment/ перенаправит
        анонимного пользователя на страницу логина.
        """
        response = self.client.get(
            f'/posts/{self.post.id}/comment/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
