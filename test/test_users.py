# test/test_users.py
import pytest
import json
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserAuthentication:
    """Test user signup, login, and authentication."""
    
    def test_signup_success(self, api_client):
        """Test successful user signup."""
        query = """
            mutation Signup($username: String!, $email: String!, $password: String!) {
                signup(username: $username, email: $email, password: $password) {
                    user {
                        id
                        username
                        email
                    }
                    token
                    refreshToken
                }
            }
        """
        variables = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
        
        response = api_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['signup']['user']['username'] == 'newuser'
        assert data['data']['signup']['token'] is not None
        assert data['data']['signup']['refreshToken'] is not None
        
        # Verify user was created in database
        assert User.objects.filter(username='newuser').exists()
    
    def test_signup_duplicate_username(self, api_client, user):
        """Test signup fails with duplicate username."""
        query = """
            mutation Signup($username: String!, $email: String!, $password: String!) {
                signup(username: $username, email: $email, password: $password) {
                    user { id }
                }
            }
        """
        variables = {
            "username": user.username,  # Already exists
            "email": "different@example.com",
            "password": "SecurePass123!"
        }
        
        response = api_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' in data
        assert 'already exists' in str(data['errors']).lower()
    
    def test_login_success(self, api_client, user):
        """Test successful login."""
        query = """
            mutation Login($username: String!, $password: String!) {
                login(username: $username, password: $password) {
                    user {
                        id
                        username
                    }
                    token
                    refreshToken
                }
            }
        """
        variables = {
            "username": user.username,
            "password": "testpass123"
        }
        
        response = api_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['login']['user']['username'] == user.username
        assert data['data']['login']['token'] is not None
    
    def test_login_invalid_credentials(self, api_client, user):
        """Test login fails with wrong password."""
        query = """
            mutation Login($username: String!, $password: String!) {
                login(username: $username, password: $password) {
                    user { id }
                }
            }
        """
        variables = {
            "username": user.username,
            "password": "wrongpassword"
        }
        
        response = api_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' in data
    
    def test_get_current_user(self, authenticated_client, user):
        """Test getting current user info (me query)."""
        query = """
            query {
                me {
                    id
                    username
                    email
                }
            }
        """
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['me']['username'] == user.username
    
    def test_update_profile(self, authenticated_client, user):
        """Test updating user profile."""
        query = """
            mutation UpdateProfile($bio: String, $email: String) {
                updateProfile(bio: $bio, email: $email) {
                    user {
                        id
                        bio
                        email
                    }
                }
            }
        """
        variables = {
            "bio": "Updated bio text",
            "email": "updated@example.com"
        }
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['updateProfile']['user']['bio'] == 'Updated bio text'
        
        # Verify in database
        user.refresh_from_db()
        assert user.bio == 'Updated bio text'


@pytest.mark.django_db
class TestUserQueries:
    """Test user query operations."""
    
    def test_get_all_users(self, authenticated_client, user, other_user):
        """Test getting all users."""
        query = """
            query {
                users {
                    id
                    username
                }
            }
        """
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert len(data['data']['users']) >= 2
    
    def test_search_users(self, authenticated_client, user_factory):
        """Test searching users by username."""
        user_factory(username="john_doe")
        user_factory(username="jane_smith")
        
        query = """
            query SearchUsers($query: String!) {
                searchUsers(query: $query) {
                    username
                }
            }
        """
        variables = {"query": "john"}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        usernames = [u['username'] for u in data['data']['searchUsers']]
        assert 'john_doe' in usernames
        assert 'jane_smith' not in usernames