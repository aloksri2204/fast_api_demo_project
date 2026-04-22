

## Step 2 ->

# class Products:
#     id : int
#     name: str
#     desc: str
#     price: float
#     quantity: int


#     def __init__(self, id, name, desc, price, quantity):
#         self.id = id
#         self.name = name
#         self.desc = desc
#         self.price = price
#         self.quantity = quantity



## Step 3 - Pydantic approach 
from pydantic import BaseModel

class Products(BaseModel):
    id : int
    name: str
    desc: str
    price: float
    quantity: int