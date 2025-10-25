from fastapi import APIRouter, HTTPException
from typing import List
from app.db import driver
from app.models.user import User, UserCreate, UserUpdate

router = APIRouter()

# Create User
@router.post("/", response_model=User)
def create_user(user: UserCreate):
    query = """
    MERGE (u:User {id:$id})
    ON CREATE SET u.name=$name, u.role=$role, u.region=$region, u.email=$email
    ON MATCH SET u.name=$name, u.role=$role, u.region=$region, u.email=$email
    RETURN u.id AS id, u.name AS name, u.role AS role, u.region AS region, u.email AS email
    """
    with driver.session() as session:
        result = session.run(query, **user.model_dump())
        record = result.single()
        return User(**record)

# Get All Users
@router.get("/", response_model=List[User])
def get_users():
    query = "MATCH (u:User) RETURN u.id AS id, u.name AS name, u.role AS role, u.region AS region, u.email AS email"
    with driver.session() as session:
        result = session.run(query)
        users = [User(**record) for record in result]
        return users

# Get User by ID
@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    query = "MATCH (u:User {id:$id}) RETURN u.id AS id, u.name AS name, u.role AS role, u.region AS region, u.email AS email"
    with driver.session() as session:
        result = session.run(query, id=user_id)
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="User not found")
        return User(**record)

# Update User
@router.patch("/{user_id}", response_model=User)
def update_user(user_id: str, user: UserUpdate):
    fields = ", ".join([f"u.{k}=${k}" for k in user.model_dump(exclude_unset=True).keys()])
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    query = f"""
    MATCH (u:User {{id:$id}})
    SET {fields}
    RETURN u.id AS id, u.name AS name, u.role AS role, u.region AS region, u.email AS email
    """
    with driver.session() as session:
        result = session.run(query, **{"id": user_id, **user.dict(exclude_unset=True)})
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="User not found")
        return User(**record)
