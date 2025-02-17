from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from users.models import User
from posts.models import Post
import json

class SecurityTest(TestCase):
    def setUp(self):
        # Create groups
        self.admin_group = Group.objects.create(name='Admin')
        self.regular_group = Group.objects.create(name='Regular')

        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='Admin123!'
        )
        self.admin_user.groups.add(self.admin_group)
        self.admin_token = Token.objects.create(user=self.admin_user)

        self.regular_user = User.objects.create_user(
            username='user_test',
            email='user@test.com',
            password='User123!'
        )
        self.regular_user.groups.add(self.regular_group)
        self.regular_token = Token.objects.create(user=self.regular_user)

        # Create another regular user for testing post ownership
        self.other_user = User.objects.create_user(
            username='other_test',
            email='other@test.com',
            password='Other123!'
        )
        self.other_user.groups.add(self.regular_group)
        
        # Create test post owned by other_user
        self.test_post = Post.objects.create(
            content='Test post content',
            author=self.other_user  # Post is owned by other_user
        )

        # Setup API client
        self.client = APIClient()

    def test_https_required(self):
        """Test that non-HTTPS requests are redirected"""
        response = self.client.get('/users/user-list/', secure=False, follow=True)
        self.assertEqual(response.redirect_chain[0][1], 301)  # Redirects to HTTPS

    def test_secure_cookies(self):
        """Test that cookies have secure attributes"""
        response = self.client.post('/users/login/', 
            data={
                'username': 'user_test',
                'password': 'User123!'
            },
            secure=True,
            follow=True
        )
        
        # Check if token is in response
        self.assertIn('token', response.data)

    def test_password_encryption(self):
        """Test that passwords are not stored in plaintext"""
        user = User.objects.get(username='user_test')
        # Check that password is hashed
        self.assertNotEqual(user.password, 'User123!')
        # Check that password verification works
        self.assertTrue(user.check_password('User123!'))

    def test_role_based_access(self):
        """Test role-based permissions"""
        # Regular user trying to delete another user's post
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.regular_token.key}')
        response = self.client.delete(f'/posts/posts/{self.test_post.id}/', secure=True)
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Admin user should be able to delete any post
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.delete(f'/posts/posts/{self.test_post.id}/', secure=True)
        self.assertEqual(response.status_code, 204)  # Successful deletion

    def test_token_authentication(self):
        """Test token authentication"""
        # Request without token
        response = self.client.get('/posts/posts/', secure=True)
        self.assertEqual(response.status_code, 401)  # Unauthorized

        # Request with valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.regular_token.key}')
        response = self.client.get('/posts/posts/', secure=True)
        self.assertEqual(response.status_code, 200)  # Success
