# test/test_follows.py
import pytest
import json
from apps.follows.models import Follow
from apps.notifications.models import Notification


@pytest.mark.django_db
class TestFollowMutations:
    """Test follow/unfollow operations."""
    
    def test_follow_user(self, authenticated_client, user, other_user):
        """Test following another user."""
        query = """
            mutation FollowUser($userId: ID!) {
                followUser(userId: $userId) {
                    success
                    follow {
                        id
                        follower {
                            username
                        }
                        followed {
                            username
                        }
                    }
                }
            }
        """
        variables = {"userId": str(other_user.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['followUser']['success'] is True
        assert data['data']['followUser']['follow']['follower']['username'] == user.username
        assert data['data']['followUser']['follow']['followed']['username'] == other_user.username
        
        # Verify in database
        assert Follow.objects.filter(follower=user, followed=other_user).exists()
        
        # Verify notification was created
        assert Notification.objects.filter(
            recipient=other_user,
            sender=user,
            notification_type='follow'
        ).exists()
    
    def test_follow_self_fails(self, authenticated_client, user):
        """Test following yourself fails."""
        query = """
            mutation FollowUser($userId: ID!) {
                followUser(userId: $userId) {
                    success
                }
            }
        """
        variables = {"userId": str(user.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' in data
        assert 'cannot follow yourself' in str(data['errors']).lower()
    
    def test_follow_duplicate_fails(self, authenticated_client, user, other_user):
        """Test following same user twice fails."""
        # First follow
        Follow.objects.create(follower=user, followed=other_user)
        
        query = """
            mutation FollowUser($userId: ID!) {
                followUser(userId: $userId) {
                    success
                }
            }
        """
        variables = {"userId": str(other_user.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' in data
        assert 'already following' in str(data['errors']).lower()
    
    def test_unfollow_user(self, authenticated_client, user, other_user):
        """Test unfollowing a user."""
        # First follow
        Follow.objects.create(follower=user, followed=other_user)
        
        query = """
            mutation UnfollowUser($userId: ID!) {
                unfollowUser(userId: $userId) {
                    success
                }
            }
        """
        variables = {"userId": str(other_user.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['unfollowUser']['success'] is True
        
        # Verify removed from database
        assert not Follow.objects.filter(follower=user, followed=other_user).exists()


@pytest.mark.django_db
class TestFollowQueries:
    """Test follow query operations."""
    
    def test_get_followers(self, authenticated_client, user, other_user, follow_factory):
        """Test getting a user's followers."""
        # other_user follows user
        follow_factory(follower=other_user, followed=user)
        
        query = """
            query GetFollowers($userId: ID!) {
                followers(userId: $userId) {
                    id
                    follower {
                        id
                        username
                    }
                }
            }
        """
        variables = {"userId": str(user.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert len(data['data']['followers']) == 1
        assert data['data']['followers'][0]['follower']['username'] == other_user.username
    
    def test_get_following(self, authenticated_client, user, other_user, follow_factory):
        """Test getting who a user is following."""
        # user follows other_user
        follow_factory(follower=user, followed=other_user)
        
        query = """
            query GetFollowing($userId: ID!) {
                following(userId: $userId) {
                    id
                    followed {
                        id
                        username
                    }
                }
            }
        """
        variables = {"userId": str(user.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert len(data['data']['following']) == 1
        assert data['data']['following'][0]['followed']['username'] == other_user.username
    
    def test_follow_stats(self, authenticated_client, user, other_user, user_factory, follow_factory):
        """Test getting follow statistics."""
        user3 = user_factory(username="user3", email="user3@example.com")
        
        # other_user follows user
        follow_factory(follower=other_user, followed=user)
        # user3 follows user
        follow_factory(follower=user3, followed=user)
        # user follows other_user
        follow_factory(follower=user, followed=other_user)
        
        query = """
            query GetFollowStats($userId: ID!) {
                followStats(userId: $userId) {
                    followersCount
                    followingCount
                    isFollowing
                    isFollowedBy
                }
            }
        """
        variables = {"userId": str(user.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['followStats']['followersCount'] == 2
        assert data['data']['followStats']['followingCount'] == 1
    
    def test_is_following(self, authenticated_client, user, other_user, follow_factory):
        """Test checking if current user follows another user."""
        follow_factory(follower=user, followed=other_user)
        
        query = """
            query IsFollowing($userId: ID!) {
                isFollowing(userId: $userId)
            }
        """
        variables = {"userId": str(other_user.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['isFollowing'] is True