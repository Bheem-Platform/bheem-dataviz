Here's a summary of how to connect Bheem Passport for external authentication in your microservice:

  Key Integration Points

  Base URL

  https://platform.bheem.co.uk/api/v1/auth

  Authentication Options

  1. Traditional Login
  POST /api/v1/auth/login
  Content-Type: application/x-www-form-urlencoded

  username=user@example.com&password=Password123!&company_code=BHM008

  2. Social Login (Google, GitHub, etc.)
  GET /api/v1/auth/oauth/{provider}?company_code=BHM008

  Backend Token Verification (Two Options)

  Option A - Verify JWT locally (faster, requires shared secret):
  JWT_SECRET = "bheem-platform-secret-key-change-in-production"
  JWT_ALGORITHM = "HS256"

  payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

  Option B - Verify with BheemPassport API (simpler, no shared secret needed):
  response = await client.get(
      "https://platform.bheem.co.uk/api/v1/auth/me",
      headers={"Authorization": f"Bearer {token}"}
  )
  user = response.json()  # Returns user_id, email, company_code, etc.

  JWT Token Payload Structure

  {
    "sub": "user_uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "company_id": "company_uuid",
    "company_code": "BHM008",
    "exp": 1700000000,
    "type": "access"
  }

  Company Codes

  - BHM001: BHEEMVERSE INNOVATIONS
  - BHM002: BHEEM CLOUD
  - BHM003-BHM008: Other Bheem services

  Quick Checklist for Your Microservice

  1. Add JWT verification middleware (use Option A or B above)
  2. Extract user info from token (sub, email, company_code)
  3. Implement token refresh using /api/v1/auth/refresh
  4. Configure CORS to allow your microservice domain