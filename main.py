
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import Products

import database_models
from database_connection import engine, session
from sqlalchemy.orm import Session

database_models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"]
    # allow_headers=["X-Requested-With", "Content-Type"]
)

@app.get("/")
def greet():
    return "Welcome to fast api demo project"


# products = [
#     { 
#         "id":1,
#         "name": "Laptop",
#         "desc" : "This is an HP 10th GEN Laptop",
#         "price": "5000",
#         "quantity": 10

#     }
   
# ]


# Step 2 --> This version shows the disadvantages of having this approach that client can update any type of data as its not being validatated

# prod = [
#     Products(1,"DELL Inspiron 22","This is a dell laptop",55000, quantity= 6),
#     Products(2,"HP Pavilion","This is a HP laptop",45000, quantity=11),
#     Products(-5,"A"," ",-1000, quantity='12'),
#         ]



# Step 3 --> Pydantic approach 

prod = [
    Products(id =1, name="DELL Inspiron 22",desc="This is a dell laptop",price=55000, quantity= 6),
    Products(id=2, name="HP Pavilion", desc="This is a HP laptop", price=45000, quantity=11),
    Products(id=3, name="Samsung S25 Ultra", desc="This is a samsung mobile phone", price=125000, quantity=5),
    Products(id=4, name="One plus 12", desc="This is an Oneplus mobile phone", price=95000, quantity=8),
    Products(id=5, name="iphone18", desc="This is an Apple iPhone", price=145000, quantity=10)
]



###-----------------------------------------------------------------From database-----------------------------------------------------------------------###


### Initializing the database instance 

def init_db():
    db = session()
    count = db.query(database_models.Product).count
    if count ==0:
        for product in prod:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()
    
init_db()


### creating an instance to update the data

def get_db():
    db = session()
    try:
        yield db
    except Exception as e:
        print(e)
    finally:
        db.close()



## Getting all products

@app.get("/products/")
def get_products(db: Session = Depends(get_db)): ###This is dependency injection
    db_products = db.query(database_models.Product).all()
    return db_products


# ## Getting a spcific product with id

@app.get("/products/{id}")
def get_product_with_id(id:int,db: Session= Depends(get_db)): ###This is dependency injection
    db_products = db.query(database_models.Product).filter(database_models.Product.id==id).first()
    if db_products:
        return db_products
        
    return "Product Not Found"





# ### Adding a specifc product 

@app.post("/products/")
def add_product(product: Products, db: Session= Depends(get_db)):
    db.add(database_models.Product(**product.model_dump()))
    db.commit()
    return product
    


# ### updating a product

@app.put("/products/{id}")
def update_product(id: int, product: Products,db: Session= Depends(get_db)):
    db_products = db.query(database_models.Product).filter(database_models.Product.id==id).first()
    if db_products:
        db_products.name = product.name
        db_products.desc = product.desc
        db_products.price = product.price
        db_products.quantity = product.quantity
        db.commit()
        return "product added succesfully"
    return f"Product with id {id} not found"






## Deleting this product 

@app.delete("/products/{id}")
def delete_product(id:int, db: Session= Depends(get_db)):
    db_products = db.query(database_models.Product).filter(database_models.Product.id==id).first()
    if db_products:
        db.delete(db_products)
        db.commit()
        return "Product deleted successfully"
    return f"Product with id {id} not found"
            
    




















###-----------------------------------------------------------------From python file-----------------------------------------------------------------------###

# @app.get("/products")
# def get_products():
#     # return "All the products returned"
#     return prod



# ## Getting a spcific product with id

# @app.get("/product/{id}")
# def get_product_with_id(id:int):
#     for product in prod:
#         print(f"product is {product} and its type is {type(product)}")
#         print(product.id)
#         print(f"product.id is {product.id} and its type is {type(product.id)}")
#         print(f"id is {id} and its type is {type(id)}")
#         if product.id == id:
#             return product
        
#     return "Product Not Found"



# ### Adding a specifc product 

# @app.post("/product")
# def add_product(product: Products):
#     prod.append(product)
#     return product


# ### updating a product

# @app.put("/product")
# def update_product(id: int, product: Products):
#     for i in range(len(prod)):
#         if prod[i].id==id:
#             prod[i]=product
#             return "product added succesfully"
#     return f"Product with id {id} not found"



# ## Deleting this product 

# @app.delete("/product")
# def delete_product(id:int):
#     for i in range(len(prod)):
#         if prod[i].id ==id:
#             del prod[i]
#             return "Product deleted successfully"
#     return f"Product with id {id} not found"
            
    