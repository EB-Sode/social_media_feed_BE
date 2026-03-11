# Social Media Feed — Backend API

A production-grade social media backend I built to deepen my understanding of scalable system design, async task processing, and GraphQL API architecture. The system handles core social interactions — posting, liking, commenting, following, and real-time notifications — with a focus on clean architecture and performance.

🔗 **Live API:** `https://social-media-feed-be.onrender.com`
🔗 **Frontend (Next.js):** `https://social-media-feed-app-five.vercel.app/`
🔗 **GraphQL Playground:** `https://social-media-feed-be.onrender.com/graphql/` *(interactive, try queries live)*

---

## What I Built & Why

I wanted to go beyond basic CRUD and tackle the real problems that come with social platforms: feed ranking, notification fanout, image uploads, and background job processing. I chose a social media feed because it forces you to make concrete decisions about performance — a naive feed query joining posts, likes, comments, and follower relationships at scale is immediately painful.

The project pushed me to learn how to move expensive work off the request cycle (Celery), cache hot data (Redis), and design a GraphQL schema that doesn't produce N+1 queries by default.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend Framework | Django 4.x | Mature ORM, strong ecosystem, great for rapid iteration |
| API Style | GraphQL (Graphene-Django) | Feed queries are complex — clients request exactly what they need |
| Auth | JWT (SimpleJWT) | Stateless, works cleanly with decoupled Next.js frontend |
| Database | PostgreSQL (Neon) | Relational integrity for social graph; Neon for serverless branching |
| Cache / Queue Broker | Redis | Feed caching + Celery task broker |
| Async Tasks | Celery + Celery Beat | Notification emails run off the main request cycle |
| Image Storage | Cloudinary | Managed CDN, automatic resizing, avoids serving media from Django |
| Containerization | Docker + Docker Compose | Consistent dev/prod environment; single-command local setup |
| Web Server | Nginx + Gunicorn + Supervisord | Production-grade process management inside the container |
| CI/CD | GitHub Actions | Linting, test suite runs on every push |
| Deployment | Render (backend) + Vercel (frontend) | Zero-infrastructure hosting with Docker support on Render |

---

## Core Features

**User Management**
- Signup, login, logout with JWT access + refresh token flow
- Custom user model extending `AbstractUser` with bio, location, profile image, cover image
- Profile updates and image uploads via Cloudinary

**Posts & Interactions**
- Create, update, delete posts with optional image upload
- Like / unlike toggle (idempotent — safe to call twice)
- Comments with full CRUD
- All mutations enforce ownership — you can only edit or delete your own content

**Social Graph**
- Follow / unfollow users
- Followers, following counts with `is_following` / `is_followed_by` context per request
- Duplicate-follow prevention via `unique_together` constraint

**Feed Algorithm**
- Pulls posts from followed users + own posts
- Annotates with engagement score: `likes × 3 + comments × 2`
- Ordered by recency with engagement as a secondary signal
- Paginated via `limit` / `offset`

**Notifications**
- Generated on: likes, comments, follows, mentions
- Deduplication on `like` and `follow` types — no notification spam
- Async email delivery via Celery task (non-blocking)
- Mark as read / mark all as read mutations

**Search**
- Search users by username or bio
- Search posts by content
- Search hashtags
- Single `search` query with a `type` filter (`users`, `posts`, `hashtags`, `all`)

---

## Architecture

```
social_media_feed_BE/
├── apps/
|   |-- common/         #JWT user authentication
│   ├── users/          # Auth, profiles
│   ├── posts/          # Posts, likes, comments
│   ├── follows/        # Follow relationships + stats
│   ├── notifications/  # Notification model, async email tasks
│   └── search/         # Cross-entity search
├── social_media_feed/
│   ├── schema.py       # Root GraphQL schema (composes all app schemas)
│   ├── settings.py
│   └── urls.py
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── nginx.conf
│   ├── supervisord.conf
│   └── entrypoint.sh
└── tests/
    ├── test_users.py
    ├── test_posts.py
    └── test_follows.py
```

The major apps follow the same internal structure:
- `models.py` — data layer only
- `services.py` — all business logic lives here, not in mutations
- `mutations.py` — thin layer that calls services and returns GraphQL types
- `schema.py` — query resolvers
- `types.py` — GraphQL type definitions

This separation means business logic is fully testable without going through the GraphQL layer.

---

## Key Technical Decisions

**GraphQL over REST**

The feed query is inherently complex — a single screen needs post content, author details, like counts, comment counts, and whether the current user liked each post. With REST that's multiple requests or an over-fetching endpoint. GraphQL lets the client declare exactly what it needs in one round trip.

Tradeoff I'm aware of: N+1 queries are harder to spot in GraphQL than in REST. I use `select_related` and `prefetch_related` on hot paths, and the next iteration would add DataLoader to fully solve resolver-level N+1s.

**Services Layer Pattern**

Business logic lives in `services.py`, not in GraphQL mutations. `toggle_like()`, `create_comment()`, `get_user_feed()`, and `create_notification()` are all plain Python functions. This means they can be called from Celery tasks, management commands, or tests without touching GraphQL at all.

**Async Notifications via Celery**

When a user likes a post or gains a follower, the notification email is dispatched as a Celery task rather than executing synchronously in the mutation. This keeps mutation response time fast regardless of email provider latency. Celery Beat handles any scheduled/recurring tasks.

**Notification Deduplication**

Like and follow notifications use `get_or_create` — if you like the same post twice (or the like/unlike toggles), only one notification is created, not a stream of duplicates. Comment and mention notifications are always created because each one is a distinct event.

**Engagement Score at the Database Level**

Rather than pulling posts into Python and sorting there, the feed algorithm uses Django's `annotate()` + `F()` expressions to compute engagement scores in SQL:

```python
engagement_score = F('likes_count') * 3 + F('comments_count') * 2
```

This keeps sorting logic in one DB round trip instead of a Python sort over a large queryset.

**Cloudinary for Media**

Images are uploaded directly from Django to Cloudinary. The returned `secure_url` is stored as a URL field on the model. This means the app never stores binary data, serves no media files itself, and gets CDN delivery for free.

---

## Data Model

```
CustomUser
  │
  ├──< Post (author)
  │     ├──< Like (user, post)
  │     └──< Comment (author, post)
  │
  ├──< Follow (follower → followed)
  │
  └──< Notification (recipient, sender, type, post?)
```

Key constraints:
- `Like`: `unique_together(user, post)` — prevents double-liking at the DB level
- `Follow`: `unique_together(follower, followed)` — prevents duplicate follows
- `Notification`: deduped at application level for `like` and `follow` types

---

## Setup & Local Development

**Prerequisites:** Docker + Docker Compose

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/social_media_feed_BE
cd social_media_feed_BE

# 2. Set up environment variables
cp .env.example .env
# Fill in your values (see .env.example for required keys)

# 3. Start all services
docker-compose up --build

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. (Optional) Create a superuser
docker-compose exec web python manage.py createsuperuser

# 6. Open GraphQL Playground
open http://localhost:8000/graphql/
```

**Environment variables required:**

```
SECRET_KEY=
DEBUG=
DATABASE_URL=
REDIS_URL=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
CELERY_BROKER_URL=
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

---

## GraphQL Examples

**Sign up and get a token**
```graphql
mutation {
  signup(username: "alice", email: "alice@example.com", password: "secure123") {
    token
    refreshToken
    user { id username }
  }
}
```

**Get your personalized feed**
```graphql
query {
  feed(limit: 10, offset: 0) {
    id
    content
    imageUrl
    createdAt
    author { username profileImage }
    likesCount
    commentsCount
    isLikedByUser
  }
}
```

**Like a post**
```graphql
mutation {
  likePost(postId: "42") {
    success
    message
    post { likesCount isLikedByUser }
  }
}
```

**Follow a user**
```graphql
mutation {
  followUser(userId: "7") {
    success
    follow {
      follower { username }
      followed { username }
    }
  }
}
```

**Search across users, posts, hashtags**
```graphql
query {
  search(q: "django", type: "all", limit: 5) {
    users { username profileImage }
    posts { content createdAt }
    hashtags { name }
  }
}
```

---

## Tests

```bash
# Run the full test suite
docker-compose exec web pytest

# With coverage report
docker-compose exec web pytest --cov=apps --cov-report=term-missing
```

Test coverage includes:
- User signup, login, duplicate detection, profile updates
- Post creation, update, delete, ownership enforcement
- Like toggle (like and unlike)
- Comment CRUD
- Follow / unfollow, duplicate follow prevention, self-follow prevention
- Follow stats queries
- Unauthenticated access rejection across all protected mutations

---

## What I'd Do Differently

**DataLoader for N+1 resolution** — In `PostType`, resolvers like `is_liked_by_user` currently hit the database once per post in a feed. DataLoader would batch these into a single query across the whole feed response.

**Time-decay in the feed ranking** — The current engagement score is computed correctly but recency dominates `ORDER BY`. I'd replace this with a decay formula that blends engagement and age into a single float, closer to how real feed algorithms work.

**Rate limiting on auth mutations** — `LoginMutation` currently has no brute-force protection. I'd add `django-ratelimit` or a Redis-based attempt counter per IP.

**Refresh token rotation** — Currently refresh tokens don't rotate. Enabling `ROTATE_REFRESH_TOKENS` in SimpleJWT settings and blacklisting used tokens on logout would close that gap.

---

## Author

**Blessed Sode**
Backend Engineer · Python / Django / GraphQL
[GitHub](https://github.com/EB-sode) · [LinkedIn](https://linkedin.com/in/blessedsode) · [Portfolio](https://sode.dev)