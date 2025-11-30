# social_media_feed_BE 📌 Social Media Backend — ProDev Backend Engineering Capstone

A fully-featured social media backend built using Django, GraphQL, PostgreSQL, Docker, and CI/CD pipelines.
The backend powers real-time social interactions such as posting, liking, following, commenting, and receiving notifications.

This project demonstrates your ability to design scalable backend systems, implement clean architecture, and apply modern backend engineering practices.

## Project Features
*** 1. User Management ***

- Signup, login, logout

- JWT authentication (GraphQL middleware)

- User profile (bio, profile image, join date)

- Follow / Unfollow users

*** 2. Posts & Interactions ***

- Create, update, delete posts

- Upload images (optional: S3 or local media)

- Like/unlike posts

- Comment on posts

- View feed of posts from followed users

*** 3. Social Graph ***

- Track followers and following

- Suggest users to follow (optional)

- Count followers, following, and engagement

*** 4. Notifications ***

- Receive notifications for:

- New likes

- New comments

- New followers

- Mark as read/unread

*** 5. GraphQL API ***

- Built using Graphene-Django:

- Query exactly the data you need

- Mutations for all core actions

- GraphQL playground enabled for testing

- Pagination & filtering

*** 6. Infrastructure ***

- Fully containerized with Docker

- Multi-stage Dockerfile

- docker-compose for local development

- Automatic database migrations

*** 7. CI/CD Pipeline ***

Linting + formatting checks

Automated tests

Auto-build Docker containers

Deployment-ready configuration

Optional: GH Actions / Render / Railway

## Project Architecture
social_media_backend/
│
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD workflow file
│
├── docker/
│   ├── Dockerfile                # Docker image instructions
│   └── docker-compose.yml        # Multi-service container setup
│
├── manage.py
│
├── requirements.txt              # All dependencies
│
├── .env                          # Environment variables (DB, SECRET_KEY, etc.)
│
├── social_media_feed/                       # Django project config folder
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py               # Core settings (load from .env)
│   ├── urls.py                   # Root URL router (GraphQL endpoint)
│   ├── schema.py                 # Root GraphQL schema combining app schemas
│   └── wsgi.py
│
├── apps/                         # All business logic apps
│   ├── __init__.py
│   │
│   ├── users/                    # Handles user management and auth
│   │   ├── __init__.py
│   │   ├── models.py             # User model (CustomUser)
│   │   ├── schema.py             # GraphQL resolvers for user queries/mutations
│   │   ├── serializers.py        # If you ever need DRF compatibility
│   │   ├── mutations.py          # Separate user mutations if preferred
│   │   ├── signals.py            # Profile creation, etc.
│   │   ├── types.py
│   │   └── admin.py
│   │
│   ├── posts/                    # Manages posts, comments, and likes
│   │   ├── __init__.py
│   │   ├── models.py             # Post, Comment, Like models
│   │   ├── schema.py             # Post queries & mutations
│   │   ├── mutations.py
│   │   ├── services.py           # Helper functions (e.g., fetch_feed())
│   │   ├── types.py
│   │   └── admin.py
│   │
│   ├── follows/                  # Manages following relationships
│   │   ├── __init__.py
│   │   ├── models.py             # Follow model (follower -> followed)
│   │   ├── schema.py             # Follow mutations (follow/unfollow)
│   │   ├── services.py
│   │   ├── types.py
│   │   └── admin.py
        
│   │
│   └── notifications/ (optional) # If you later add async updates
│       ├── models.py
│       ├── tasks.py              # Celery async tasks (send notifications)
│       ├── schema.py
│       └── services.py
│
├── scripts/                      # Utility scripts
│   ├── entrypoint.sh             # For Docker setup
│   └── init_db.sh
│
└── tests/
    ├── __init__.py
    ├── test_users.py
    ├── test_posts.py
    └── test_follows.py


### Why this architecture?

- Modular apps → scalable and maintainable

- GraphQL schemas are split per app → clean separation of concerns

- settings/base.py → avoids mixing dev & prod config

- services.py pattern → keeps business logic out of views/mutations

## Database
Entities

User – profile + authentication

Post – text/image posts by users

Like – relationship between user & post

Comment – user’s response to a post

Follow – follower → followed relationship

Notification – interactions that notify a user

## Tech Stack
- Layer	Technology
- Backend Framework	Django / Django Graphene
- API Style	GraphQL
- Auth	JWT Authentication
- Database	PostgreSQL
- Containerization	Docker & Docker Compose
- CI/CD	GitHub Actions (or GitLab CI / Render Deploy)
- Storage	Local media / S3 (optional)
- Deployment	Render, Railway, AWS, or Docker VPS

## Setup & Installation

1. Clone the repository
git clone <repository_url>
cd social_media_feed_BE

2. Create environment variables
DEBUG=1
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://...

3. Run with Docker
docker-compose up --build

4. Apply migrations
docker-compose exec web python manage.py migrate

5. Open GraphQL Playground
http://localhost:8000/graphql/

## GraphQL Example

***Use this to query mutation names***
{
  "query": "query { __schema { mutationType { fields { name } } } }"
}

Query: Get posts from followed users
query {
  feed {
    id
    content
    author {
      username
    }
    likesCount
    comments {
      content
    }
  }
}

Mutation: Create a Post
mutation {
  createPost(content: "My first post!") {
    post {
      id
      content
    }
  }
}

## Testing

- Run unit tests with:

- docker-compose exec web pytest

## Core Backend Concepts Demonstrated

- Clean architecture & modular Django apps

- GraphQL schema design

- Database modeling & ERD translation

- Authentication & authorization

- CI/CD pipelines

- Dockerized environments

- Business logic separation using services.py

- Production-ready Django configuration

## Why This Project Stands Out

*** This capstone shows: ***

- Real backend engineering skills

- Understanding of distributed systems

- API design with modern GraphQL patterns

- Knowledge of containerization & CI/CD

- Ability to structure production-grade projects