"""FastAPI application exposing CRUD endpoints for product management."""

import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import database_models
from database_connection import engine, session
from models import Products

database_models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def _load_allowed_origins():
    """Load allowed CORS origins from the environment configuration."""
    configured_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]


ALLOWED_ORIGINS = _load_allowed_origins()
LOCAL_ORIGIN_REGEX = (
    r"^https?://"
    r"(localhost|127\.0\.0\.1|host\.docker\.internal|backend|frontend|(?:\d{1,3}\.){3}\d{1,3})"
    r"(:\d+)?$"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=LOCAL_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def greet():
    """Return a simple welcome response for health checks and quick testing."""
    return "Welcome to fast api demo project"


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
    """Seed the database with demo records when the table is empty."""
    db = session()
    try:
        count = db.query(database_models.Product).count()
        if count == 0:
            for product in prod:
                db.add(database_models.Product(**product.model_dump()))
            db.commit()
    finally:
        db.close()


init_db()


def get_db():
    """Yield a database session for the duration of a request."""
    db = session()
    try:
        yield db
    finally:
        db.close()


@app.get("/products/")
def get_products(db: Session = Depends(get_db)):
    """Return all products currently stored in the database."""
    db_products = db.query(database_models.Product).all()
    return db_products


@app.get("/products/{id}")
def get_product_with_id(id: int, db: Session = Depends(get_db)):
    """Return a single product by identifier, if it exists."""
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        return db_product
    return "Product Not Found"


@app.post("/products/")
def add_product(product: Products, db: Session = Depends(get_db)):
    """Create a new product record from the provided payload."""
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product


@app.put("/products/{id}")
def update_product(id: int, product: Products, db: Session = Depends(get_db)):
    """Update the stored product fields for the given identifier."""
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db_product.name = product.name
        db_product.desc = product.desc
        db_product.price = product.price
        db_product.quantity = product.quantity
        db.commit()
        return "product added succesfully"
    return f"Product with id {id} not found"


@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    """Delete a product record when the identifier exists."""
    db_product = db.query(database_models.Product).filter(database_models.Product.id == id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product deleted successfully"
    return f"Product with id {id} not found"
