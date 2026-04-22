# FastAPI Demo Project

A demonstration project showcasing a full-stack application with a FastAPI backend and a React frontend for managing products. The backend uses SQLAlchemy with PostgreSQL for data persistence, and the frontend provides a user interface for CRUD operations.

## Features

- **Backend (FastAPI)**:
  - RESTful API for product management
  - CRUD operations: Create, Read, Update, Delete products
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
- `GET /products/` - Retrieve all products
- `GET /products/{id}` - Retrieve a specific product by ID
- `POST /products/` - Create a new product
- `PUT /products/{id}` - Update an existing product
- `DELETE /products/{id}` - Delete a product

## Usage

1. Start both the backend and frontend servers as described above.
2. Open your browser and navigate to `http://localhost:3000`.
3. Use the interface to view, add, edit, and delete products.

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