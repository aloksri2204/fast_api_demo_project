# FastAPI Demo Project

A demonstration project showcasing a full-stack application with a FastAPI backend and a React frontend for managing products. The backend uses SQLAlchemy with PostgreSQL for data persistence, and the frontend provides a user interface for CRUD operations.

## Features

- **Backend (FastAPI)**:
  - RESTful API for product management
  - CRUD operations: Create, Read, Update, Delete products
  - Database-backed authentication
  - Password hashing and bearer-token sessions
  - Role-based permissions for read-only and write access
  - Data validation using Pydantic models
  - CORS middleware for frontend integration
  - PostgreSQL database integration with SQLAlchemy

- **Frontend (React)**:
  - User-friendly interface for managing products
  - Real-time CRUD operations
  - Filtering and sorting capabilities
  - Responsive design

## Technologies Used

- **Backend**:
  - FastAPI
  - SQLAlchemy
  - PostgreSQL
  - Pydantic
  - Uvicorn

- **Frontend**:
  - React
  - Axios for API calls
  - React Scripts

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL database server

## Installation

### Backend Setup

1. **Clone the repository** (if applicable) and navigate to the project directory.

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv fastapi_env
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     fastapi_env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source fastapi_env/bin/activate
     ```

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the database**:
   - Ensure PostgreSQL is running.
   - Create a database named `fastapi_db`.
   - Update the database URL in `database_connection.py` if necessary (default: `postgresql://postgres:root@localhost:5432/fastapi_db`).

6. **Create users**:
   - Start the backend and frontend.
   - Open the frontend login page.
   - Switch to the `Register` tab and create users in the database.
   - Registration only works when the entered full name, email, and selected role match an approved combination from `auth.py`.
   - Available roles:
     - `admin` - read and write access
      - `editor` - read and write access
      - `viewer` - read-only access
   - Current approved registrations:
     - `admin`: `("Alok", "aloksri2204@gmail.com")`
     - `admin`: `("Rohit", "rohit@gmail.com")`
     - `viewer`: `("Priya", "priya@example.com")`

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

## Running the Application

### Backend

1. Ensure the virtual environment is activated.
2. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend

1. In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Start the React development server:
   ```bash
   npm start
   ```
   The frontend will be available at `http://localhost:3000`.

## API Endpoints

- `GET /` - Welcome message
- `POST /auth/register` - Create a user in the database
- `POST /auth/login` - Authenticate and return a bearer token
- `GET /auth/me` - Return the logged-in user from the bearer token
- `GET /products/` - Retrieve all products
- `GET /products/{id}` - Retrieve a specific product by ID
- `POST /products/` - Create a new product
- `PUT /products/{id}` - Update an existing product
- `DELETE /products/{id}` - Delete a product

## Method Summary

### `auth.py`

- `_get_secret_key()` - Reads the secret key used to sign and verify bearer tokens.
- `_normalize_full_name()` - Normalizes a name before comparing it against the allowlist.
- `_normalize_email()` - Normalizes an email before validation and storage.
- `_allowed_registration_pairs_for_role()` - Returns the approved name/email pairs for one role.
- `_is_allowed_registration()` - Checks whether a user is allowed to register for a specific role.
- `_urlsafe_b64encode()` - Encodes token parts in URL-safe base64 format.
- `_urlsafe_b64decode()` - Decodes token parts from URL-safe base64 format.
- `hash_password()` - Creates a salted password hash for storing user passwords safely.
- `verify_password()` - Verifies a plain password against the stored password hash.
- `create_access_token()` - Creates a signed bearer token for a logged-in user.
- `decode_access_token()` - Validates and decodes a bearer token.
- `_unauthorized_exception()` - Builds the standard unauthorized response.
- `_forbidden_exception()` - Builds the standard forbidden response.
- `_serialize_user()` - Converts a database user row into the internal auth user format.
- `authenticate_user()` - Authenticates a user by username and password.
- `create_user()` - Registers a user after validating role rules and allowlist rules.
- `get_current_user()` - Reads the bearer token and returns the current user.
- `require_read_access()` - Allows only users with read permission.
- `require_write_access()` - Allows only users with write permission.

### `main.py`

- `greet()` - Returns the root welcome message.
- `init_db()` - Seeds the product table when it is empty.
- `get_db()` - Creates and closes a database session for each request.
- `user_to_response()` - Converts the authenticated user into the API response shape.
- `db_user_to_response()` - Converts a database user row into the API response shape.
- `login()` - Validates login credentials and returns a signed token.
- `register_user()` - Registers a user if the allowlist and role checks pass.
- `get_logged_in_user()` - Returns the details of the currently logged-in user.
- `get_products()` - Returns all products for users with read access.
- `get_product_with_id()` - Returns a single product by id.
- `add_product()` - Creates a new product for users with write access.
- `update_product()` - Updates an existing product for users with write access.
- `delete_product()` - Deletes a product for users with write access.

## Usage

1. Start both the backend and frontend servers as described above.
2. Open your browser and navigate to `http://localhost:3000`.
3. Register a user if the database does not already contain one.
4. Sign in to receive a bearer-token session.
5. Use the interface to view, add, edit, and delete products according to that user's role.

## Project Structure

```
fast_api_demo_project/
├── main.py                 # FastAPI application
├── models.py               # Pydantic models
├── database_connection.py  # Database configuration
├── database_models.py      # SQLAlchemy models
├── requirements.txt        # Python dependencies
├── fastapi_env/            # Virtual environment
└── frontend/               # React frontend
    ├── package.json
    ├── public/
    └── src/
        ├── App.js
        ├── App.css
        └── ...
```

## Troubleshooting

- **Database Connection Issues**: Ensure PostgreSQL is running and the database `fastapi_db` exists. Check the credentials in `database_connection.py`.
- **Port Conflicts**: If ports 8000 or 3000 are in use, modify the configuration accordingly.
- **CORS Errors**: The backend is configured to allow requests from `http://localhost:3000`. Adjust the `allow_origins` in `main.py` if needed.

## Contributing

Feel free to fork the repository and submit pull requests for improvements.

## License

This project is for demonstration purposes. Use at your own discretion.
