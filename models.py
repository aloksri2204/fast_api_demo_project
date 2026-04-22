"""Pydantic models used for validating API payloads."""

from pydantic import BaseModel

class Products(BaseModel):
    """Validated product schema used by create and update endpoints."""

    id: int
    name: str
    desc: str
    price: float
    quantity: int
