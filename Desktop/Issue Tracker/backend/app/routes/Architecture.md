# Issue Tracker – Architecture Overview

## Stack Choice

I chose FastAPI for rapid backend development because it provides:
- Automatic request validation using Pydantic
- Built-in Swagger documentation
- Clean dependency injection support

SQLAlchemy ORM was used to manage database models and relationships cleanly.

SQLite was selected for speed of setup given the 3-hour constraint. Since SQLAlchemy abstracts the database layer, switching to PostgreSQL would require minimal configuration changes.

---

## Project Structure

backend/
└── app/
    ├── main.py
    ├── database.py
    ├── models.py
    ├── schemas.py
    └── routes/

### Design Philosophy

- `database.py` handles DB connection and session management.
- `models.py` defines database schema and relationships.
- `schemas.py` defines request and response validation models.
- `routes/` contains API logic separated by domain (projects, users, issues).
- `main.py` only initializes the app and registers routers.

This separation ensures modularity and easier maintenance.

---

## Database Design

### Entities

1. Project  
   One project can have multiple issues.

2. User  
   A user can be assigned multiple issues and can write multiple comments.

3. Issue  
   Belongs to a project and is assigned to a user.  
   Uses ENUM types for `priority` and `status` to prevent invalid values.

4. Comment  
   Linked to both Issue and User.

### Design Decisions

- ENUM types were used instead of strings to enforce domain constraints.
- Indexed fields for filtering (project_id, status, priority, assignee_id).
- `created_at` and `updated_at` fields for basic auditability.
- Offset-based pagination implemented for scalability.

---

## API Design

### Filtering

The `/issues` endpoint supports:
- project_id
- priority
- status
- assignee_id
- search (title & description)

Filtering is applied dynamically to a base SQLAlchemy query to avoid redundant endpoints.

### Pagination

Implemented using:
- limit
- offset

Response includes:
- total
- limit
- offset
- data

This supports scalable frontend rendering and page navigation.

---

## Additional Features

- `/issues/stats` endpoint to return count of issues by status for dashboard display.
- `/issues/export` endpoint to export all issues as CSV.
- Proper HTTP status codes (201 for creation, 404 for missing resources).
- Server-side validation of foreign key references before database commits.

---

## What I Would Improve With More Time

- Add authentication and role-based access control.
- Add sorting support to issue listing.
- Replace hard deletes with soft delete strategy.
- Add unit tests for routes and services.
- Introduce Docker for consistent deployment.
- Add WebSocket support for real-time dashboard updates.