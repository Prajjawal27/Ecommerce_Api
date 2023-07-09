from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

class Product(BaseModel):
    name: str
    price: float
    quantity: int

class UserAddress(BaseModel):
    city: str
    country: str
    zipCode: str

class Item(BaseModel):
    productId: int
    boughtQuantity: int
    totalAmount: float

class Order(BaseModel):
    orderId: str 
    timestamp: datetime
    items: list[Item]
    userAddress: UserAddress


client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["Ecommerce_database"]
products_collection = db["products"]
orders_collection = db["orders"]

@app.on_event("startup")
async def startup():
    products = [
        {"name": "TV", "price": 499.99, "quantity": 10},
        {"name": "Laptop", "price": 899.99, "quantity": 5},
        {"name": "Smartphone", "price": 299.99, "quantity": 20},
    ]
    await products_collection.insert_many(products)

@app.get("/products")
async def list_products():
    products = []
    async for product in products_collection.find({}, {"_id": 0}):
        products.append(product)
    return products

@app.post("/orders")
async def create_order(order: Order):
    order_id = str(datetime.now().timestamp()) # Generate a unique ID for the order
    order_dict = order.dict()
    order_dict["orderId"] = order_id
    await orders_collection.insert_one(order_dict)
    return {"orderId": order_id, "message": "Order created successfully"}

@app.get("/orders")
async def list_orders(limit: int = 10, offset: int = 0):
    orders = []
    async for order in orders_collection.find({}, {"_id": 0}).skip(offset).limit(limit):
        orders.append(order)
    return orders

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    order = await orders_collection.find_one({"orderId": order_id}, {"_id": 0})
    if order:
        return order
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.put("/products/{product_id}")
async def update_product(product_id: str, quantity: int):
    result = await products_collection.update_one(
        {"_id": product_id},
        {"$set": {"quantity": quantity}}
    )
    if result.modified_count == 1:
        return {"message": "Product updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")





 