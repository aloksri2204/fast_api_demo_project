
from fastapi import Depends, FastAPI, HTTPException, status   # Importing of FastAPI request handling and HTTP exception utilities.
from fastapi.middleware.cors import CORSMiddleware            # CORS middleware so the React frontend can call this API.
from sqlalchemy.orm import Session                            # SQLAlchemy session support for database operations.

import database_models                                        # Local database models, auth helpers, and Pydantic request/response schemas.
                                                            #This module wires together authentication, product routes, database seeding,
                                                            #  and shared response formatting for the demo application.
from database_connection import engine, session
database_models.Base.metadata.create_all(bind=engine)    # Creates all tables on startup if they don't exist. Safe to call repeatedly.


from auth import (
    ROLE_PERMISSIONS,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    require_read_access,
    require_write_access,
)

from models import CreateUserRequest, LoginRequest, LoginResponse, Products, UserResponse




app = FastAPI()


## Allows the React frontend (on port 3000) to make cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def greet():
    """Return a simple welcome message for the API root."""
    return "Welcome to fast api demo project"



### Hardcoding some products to seed the database on startup. In a real application, you might load this from a file or external service instead.
prod = [
    Products(
        id=1,
        name="DELL Inspiron 22",
        desc="This is a dell laptop",
        price=55000,
        quantity=6,
    ),
    Products(
        id=2,
        name="HP Pavilion",
        desc="This is a HP laptop",
        price=45000,
        quantity=11,
    ),
    Products(
        id=3,
        name="Samsung S25 Ultra",
        desc="This is a samsung mobile phone",
        price=125000,
        quantity=5,
    ),
    Products(
        id=4,
        name="One plus 12",
        desc="This is an Oneplus mobile phone",
        price=95000,
        quantity=8,
    ),
    Products(
        id=5,
        name="iphone18",
        desc="This is an Apple iPhone",
        price=145000,
        quantity=10,
    ),
]

def init_db():
    """Seed the product table with demo data when it is empty.model_dump() converts a Pydantic model to a plain dict for unpacking into the SQLAlchemy model constructor.
        Check product count
            ↓
        If 0 → insert predefined list
            ↓
        Commit to DB
    """

    db = session()
    try:
        product_count = db.query(database_models.Product).count()
        if product_count == 0:
            for product in prod:
                db.add(database_models.Product(**product.model_dump()))
            db.commit()
    finally:
        db.close()


init_db()


def get_db():
    """Creates a database session for each request."""
    db = session()
    try:
        yield db
    finally:
        db.close()


def user_to_response(current_user) -> UserResponse:
    """Convert an authenticated user object into the API response model."""
    return UserResponse(
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        permissions=list(current_user.permissions),
    )


def db_user_to_response(user: database_models.User) -> UserResponse:
    """Convert a database user row into the API response model."""
    return UserResponse(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        permissions=list(ROLE_PERMISSIONS.get(user.role, tuple())),
    )


@app.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Validate credentials and return a signed bearer token."""
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return LoginResponse(
        access_token=create_access_token(user),
        user=db_user_to_response(user),
    )


@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: CreateUserRequest, db: Session = Depends(get_db)):
    """Register a new user when the allowlist and role rules pass."""
    user = create_user(
        db=db,
        username=payload.username,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role,
    )
    return db_user_to_response(user)


@app.get("/auth/me", response_model=UserResponse)
def get_logged_in_user(current_user=Depends(get_current_user)):
    """Return details for the currently authenticated user."""
    return user_to_response(current_user)


@app.get("/products/")
def get_products(
    db: Session = Depends(get_db),
    current_user=Depends(require_read_access),
):
    """Return all products for users with read access."""
    return db.query(database_models.Product).all()


@app.get("/products/{id}")
def get_product_with_id(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_read_access),
):
    """Return one product by id for users with read access."""
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if db_product:
        return db_product

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Product with id {id} not found",
    )


@app.post("/products/")
def add_product(
    product: Products,
    db: Session = Depends(get_db),
    current_user=Depends(require_write_access),
):
    """Create a product for users with write access."""
    existing_product = db.query(database_models.Product).filter(
        database_models.Product.id == product.id
    ).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with id {product.id} already exists",
        )

    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product


@app.put("/products/{id}")
def update_product(
    id: int,
    product: Products,
    db: Session = Depends(get_db),
    current_user=Depends(require_write_access),
):
    """Update a product by id for users with write access."""
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found",
        )

    db_product.name = product.name
    db_product.desc = product.desc
    db_product.price = product.price
    db_product.quantity = product.quantity
    db.commit()
    return "Product updated successfully"


@app.delete("/products/{id}")
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_write_access),
):
    """Delete a product by id for users with write access."""
    db_product = db.query(database_models.Product).filter(
        database_models.Product.id == id
    ).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found",
        )

    db.delete(db_product)
    db.commit()
    return "Product deleted successfully"
