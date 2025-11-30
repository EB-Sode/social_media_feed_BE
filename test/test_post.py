# test/test_posts.py
import pytest
import json
from apps.posts.models import Post, Like, Comment


@pytest.mark.django_db
class TestPostMutations:
    """Test post create, update, delete operations."""
    
    def test_create_post_success(self, authenticated_client, user):
        """Test creating a post."""
        query = """
            mutation CreatePost($content: String!) {
                createPost(content: $content) {
                    post {
                        id
                        content
                        author {
                            username
                        }
                        likesCount
                        commentsCount
                    }
                }
            }
        """
        variables = {"content": "My test post"}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['createPost']['post']['content'] == 'My test post'
        assert data['data']['createPost']['post']['author']['username'] == user.username
        assert data['data']['createPost']['post']['likesCount'] == 0
        
        # Verify in database
        assert Post.objects.filter(content='My test post').exists()
    
    def test_create_post_unauthenticated(self, api_client):
        """Test creating post fails without authentication."""
        query = """
            mutation CreatePost($content: String!) {
                createPost(content: $content) {
                    post { id }
                }
            }
        """
        variables = {"content": "Test"}
        
        response = api_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' in data
        assert 'authentication required' in str(data['errors']).lower()
    
    def test_update_post(self, authenticated_client, post):
        """Test updating own post."""
        query = """
            mutation UpdatePost($postId: ID!, $content: String) {
                updatePost(postId: $postId, content: $content) {
                    post {
                        id
                        content
                    }
                }
            }
        """
        variables = {
            "postId": str(post.id),
            "content": "Updated content"
        }
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['updatePost']['post']['content'] == 'Updated content'
        
        post.refresh_from_db()
        assert post.content == 'Updated content'
    
    def test_update_post_not_owner(self, authenticated_client, other_user, post_factory):
        """Test updating another user's post fails."""
        other_post = post_factory(author=other_user, content="Other's post")
        
        query = """
            mutation UpdatePost($postId: ID!, $content: String) {
                updatePost(postId: $postId, content: $content) {
                    post { id }
                }
            }
        """
        variables = {
            "postId": str(other_post.id),
            "content": "Hacked content"
        }
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' in data
        assert 'permission' in str(data['errors']).lower()
    
    def test_delete_post(self, authenticated_client, post):
        """Test deleting own post."""
        post_id = post.id
        
        query = """
            mutation DeletePost($postId: ID!) {
                deletePost(postId: $postId) {
                    success
                }
            }
        """
        variables = {"postId": str(post_id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['deletePost']['success'] is True
        
        # Verify deleted from database
        assert not Post.objects.filter(id=post_id).exists()


@pytest.mark.django_db
class TestLikeFunctionality:
    """Test liking and unliking posts."""
    
    def test_like_post(self, authenticated_client, user, post):
        """Test liking a post."""
        query = """
            mutation LikePost($postId: ID!) {
                likePost(postId: $postId) {
                    success
                    message
                    post {
                        id
                        likesCount
                        isLikedByUser
                    }
                }
            }
        """
        variables = {"postId": str(post.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['likePost']['success'] is True
        assert data['data']['likePost']['message'] == 'Post liked'
        assert data['data']['likePost']['post']['likesCount'] == 1
        assert data['data']['likePost']['post']['isLikedByUser'] is True
        
        # Verify in database
        assert Like.objects.filter(user=user, post=post).exists()
    
    def test_unlike_post(self, authenticated_client, user, post):
        """Test unliking a post."""
        # First like the post
        Like.objects.create(user=user, post=post)
        
        query = """
            mutation LikePost($postId: ID!) {
                likePost(postId: $postId) {
                    success
                    message
                    post {
                        likesCount
                        isLikedByUser
                    }
                }
            }
        """
        variables = {"postId": str(post.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['likePost']['message'] == 'Post unliked'
        assert data['data']['likePost']['post']['likesCount'] == 0
        assert data['data']['likePost']['post']['isLikedByUser'] is False
        
        # Verify removed from database
        assert not Like.objects.filter(user=user, post=post).exists()


@pytest.mark.django_db
class TestCommentFunctionality:
    """Test commenting on posts."""
    
    def test_create_comment(self, authenticated_client, user, post):
        """Test creating a comment."""
        query = """
            mutation CreateComment($postId: ID!, $content: String!) {
                createComment(postId: $postId, content: $content) {
                    success
                    comment {
                        id
                        content
                        author {
                            username
                        }
                    }
                }
            }
        """
        variables = {
            "postId": str(post.id),
            "content": "Great post!"
        }
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['createComment']['success'] is True
        assert data['data']['createComment']['comment']['content'] == 'Great post!'
        
        # Verify in database
        assert Comment.objects.filter(post=post, content='Great post!').exists()
    
    def test_get_post_comments(self, authenticated_client, post, user, comment_factory):
        """Test getting all comments on a post."""
        comment_factory(post=post, author=user, content="First comment")
        comment_factory(post=post, author=user, content="Second comment")
        
        query = """
            query GetComments($postId: ID!) {
                comments(postId: $postId) {
                    id
                    content
                    author {
                        username
                    }
                }
            }
        """
        variables = {"postId": str(post.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert len(data['data']['comments']) == 2


@pytest.mark.django_db
class TestPostQueries:
    """Test post query operations."""
    
    def test_get_all_posts(self, authenticated_client, user, post_factory):
        """Test getting all posts."""
        post_factory(author=user, content="Post 1")
        post_factory(author=user, content="Post 2")
        
        query = """
            query {
                posts(limit: 10) {
                    id
                    content
                    author {
                        username
                    }
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
        assert len(data['data']['posts']) >= 2
    
    def test_get_single_post(self, authenticated_client, post):
        """Test getting a single post."""
        query = """
            query GetPost($id: ID!) {
                post(id: $id) {
                    id
                    content
                    likesCount
                    commentsCount
                }
            }
        """
        variables = {"id": str(post.id)}
        
        response = authenticated_client.post(
            '/graphql/',
            data=json.dumps({'query': query, 'variables': variables}),
            content_type='application/json'
        )
        
        data = response.json()
        assert 'errors' not in data
        assert data['data']['post']['id'] == str(post.id)