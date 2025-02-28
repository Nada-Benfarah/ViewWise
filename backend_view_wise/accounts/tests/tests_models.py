from django.test import TestCase
from accounts.models import User

class UserManagerTest(TestCase):

    def test_create_user_successful(self):
        """Test creating a user with valid details"""
        user = User.objects.create_user(username="testuser", email="test@example.com", password="TestPass123")
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("TestPass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_username(self):
        """Test creating a user without a username raises an error"""
        with self.assertRaises(TypeError):
            User.objects.create_user(username=None, email="test@example.com", password="TestPass123")

    def test_create_user_without_email(self):
        """Test creating a user without an email raises an error"""
        with self.assertRaises(TypeError):
            User.objects.create_user(username="testuser", email=None, password="TestPass123")

    def test_create_superuser_successful(self):
        """Test creating a superuser with valid details"""
        admin_user = User.objects.create_superuser(username="admin", email="admin@example.com", password="AdminPass123")
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)

    def test_create_superuser_without_password(self):
        """Test creating a superuser without a password raises an error"""
        with self.assertRaises(TypeError):
            User.objects.create_superuser(username="admin", email="admin@example.com", password=None)


    def test_tokens_generation(self):
        """Test génération des jetons JWT pour un utilisateur."""
        user = User.objects.create_user(username="jwtuser", email="jwt@example.com", password="jwtpassword")
        tokens = user.tokens()
        self.assertIn('refresh', tokens)
        self.assertIn('access', tokens)
