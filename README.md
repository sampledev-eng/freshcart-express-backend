# Freshcart Express Backend

This project demonstrates a small FastAPI backend for an e‑commerce platform. It now exposes profile management, category APIs, product reviews and order tracking. Docker support and a CI workflow are included.

## Features
- User registration and JWT authentication with refresh token endpoint
- Product CRUD APIs with category filtering and search
- Product reviews and ratings
- Order creation, status updates and tracking
- Minimal test suite using Pytest
- Dockerfile and CI workflow

Run locally with:
```bash
uvicorn app.main:app --reload
```
