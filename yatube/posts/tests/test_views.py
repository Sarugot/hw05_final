from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Group, Post, Follow
from ..forms import PostForm

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.sub_user = User.objects.create_user(username='SubUser')
        cls.notsub_user = User.objects.create_user(username='NotSubUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.other_group = Group.objects.create(
            title='Тестовая группа',
            slug='test_other_slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        posts = list()
        for i in range(13):
            posts.append(Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
                image=uploaded
            ))
        cls.post = posts[0]
        cls.cash_post = posts[12]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        url_names = (
            reverse('posts:index'),
            reverse('posts:group_lists', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': self.user})
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        url_names = (
            reverse('posts:index'),
            reverse('posts:group_lists', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': self.user})
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_index_group_profile_pages_show_correct_context(self):
        url_names = (
            reverse('posts:index'),
            reverse('posts:group_lists', kwargs={'slug': 'test_slug'}),
            reverse('posts:profile', kwargs={'username': self.user})
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                first_object = response.context['page_obj'][0]
                task_author_0 = first_object.author
                task_text_0 = first_object.text
                task_group_0 = first_object.group
                task_image_0 = first_object.image
                self.assertEqual(task_author_0, self.post.author)
                self.assertEqual(task_text_0, self.post.text)
                self.assertEqual(task_group_0, self.post.group)
                self.assertEqual(task_image_0, self.post.image)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            )
        )
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_post_not_in_group(self):
        """Пост не будет показываться на странице другой группы"""
        response = self.authorized_client.get(
            reverse('posts:group_lists', kwargs={'slug': 'test_other_slug'})
        )
        self.assertNotIn(
            self.post, response.context['page_obj']
        )

    def test_index_group_profile_pages_show_correct_context(self):
        url_names = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertIsInstance(response.context.get('form'), PostForm)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = (
            (reverse('posts:index'), 'posts/index.html'),
            (reverse(
                'posts:group_lists',
                kwargs={'slug': 'test_slug'}
            ), 'posts/group_list.html'),
            (reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ), 'posts/profile.html'),
            (reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ), 'posts/post_detail.html'),
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ), 'posts/create_post.html')
        )
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_cash_index_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        base_response = self.authorized_client.get(reverse('posts:index'))
        base_content = base_response.content
        self.cash_post.delete()
        new_response = self.authorized_client.get(reverse('posts:index'))
        new_content = new_response.content
        self.assertEqual(base_content, new_content)
        cache.clear()
        newer_response = self.authorized_client.get(reverse('posts:index'))
        newer_content = newer_response.content
        self.assertNotEqual(newer_content, new_content)

    def test_new_sub(self):
        """Пост не будет показываться на странице другой группы"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': self.sub_user})
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.sub_user,
            ).exists()
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow', kwargs={'username': self.sub_user}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.sub_user,
            ).exists()
        )

    def test_sub_show(self):
        self.sub_post = Post.objects.create(
            author=self.sub_user, text='Тестовый пост'
        )
        self.notsub_post = Post.objects.create(
            author=self.notsub_user, text='Тестовый пост'
        )
        Follow.objects.create(user=self.user, author=self.sub_user)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(
            self.sub_post, response.context['page_obj']
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(
            self.notsub_post, response.context['page_obj']
        )
