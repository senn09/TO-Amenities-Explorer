# TO-Amenities-Explorer

A backend REST API that aggregates Toronto Open Data on public amenities (parks, libraries, and recreation facilities) into a single, queryable service.

**Live API:** https://to-amenities-explorer.onrender.com
> **Note:** This API is hosted on Render's free tier, so the server spins down after a period of inactivity. The first request after that may take up to a minute while it starts back up. Subsequent requests will be fast.

## Features
- User registration and login with JWT-based authentication
- Token-protected amenities endpoint
- Local development on SQLite, production on PostgreSQL

## Quick Demo

### Option 1: Postman

**1. Register an account**

1. Create a new request, set the method to `POST`, and enter `https://to-amenities-explorer.onrender.com/register`.
2. Open the **Body** tab, select **raw**, and choose **JSON** from the dropdown.
3. Enter the following and click **Send**:

```json
{
  "username": "demo_user",
  "password": "demo_password"
}
```

**2. Log in to get a token**

1. Create a new `POST` request to `https://to-amenities-explorer.onrender.com/login`.
2. Use the same raw JSON body as above and click **Send**.
3. Copy the token from the response:

```json
{
  "access_token": "<your_token>"
}
```

**3. Use the token to fetch amenities**

1. Create a new `GET` request to `https://to-amenities-explorer.onrender.com/api/amenities`.
2. Open the **Authorization** tab, set the type to **Bearer Token**, and paste your token into the **Token** field.
3. Open the **Params** tab and add `page` = `1` and `per_page` = `10`.
4. Click **Send** to receive a paginated list of amenities.

### Option 2: curl

**1. Register an account**

```bash
curl -X POST https://to-amenities-explorer.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_user", "password": "demo_password"}'
```

**2. Log in to get a token**

```bash
curl -X POST https://to-amenities-explorer.onrender.com/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo_user", "password": "demo_password"}'
```

The response contains your JWT:

```json
{
  "access_token": "<your_token>"
}
```

**3. Use the token to fetch amenities**

```bash
curl "https://to-amenities-explorer.onrender.com/api/amenities?page=1&per_page=10" \
  -H "Authorization: Bearer <your_token>"
```

## API Endpoints

| Method | Endpoint | Auth required | Description |
|--------|----------|---------------|-------------|
| POST | `/register` | No | Create a new user account |
| POST | `/login` | No | Log in and receive a JWT access token |
| GET | `/api/amenities` | Yes | Retrieve Toronto amenities (parks, libraries, recreation facilities) |

Protected endpoints expect the token in the request header:

```
Authorization: Bearer <your_token>
```

### `GET /api/amenities` query parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | `1` | Page number to return |
| `per_page` | integer | `<default>` | Number of results per page (max `<max>`) |

Example request:

```
GET /api/amenities?page=2&per_page=20
```

## Tech Stack
- Flask, a web application framework
- SQLAlchemy for ORM
- JWT for token-based authentication
- SQLite for local development and testing
- PostgreSQL for production
- Render for server hosting