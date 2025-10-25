from fastapi import APIRouter, HTTPException
from typing import List
from app.db import driver
from app.models.account import Account, AccountCreate, AccountUpdate

router = APIRouter()

# -------------------------------
# Create Account
# -------------------------------
@router.post("/", response_model=Account)
def create_account(account: AccountCreate):
    query = """
    MERGE (a:Account {id:$id})
    SET a.name=$name, a.industry=$industry, a.size=$size, a.revenue=$revenue
    RETURN a.id AS id, a.name AS name, a.industry AS industry, a.size AS size, a.revenue AS revenue
    """
    with driver.session() as session:
        record = session.run(query, **account.model_dump()).single()
        return Account(**record)

# -------------------------------
# Get All Accounts
# -------------------------------
@router.get("/", response_model=List[Account])
def get_accounts():
    query = "MATCH (a:Account) RETURN a.id AS id, a.name AS name, a.industry AS industry, a.size AS size, a.revenue AS revenue"
    with driver.session() as session:
        return [Account(**r) for r in session.run(query)]

# -------------------------------
# Get Account by ID
# -------------------------------
@router.get("/{account_id}", response_model=Account)
def get_account(account_id: str):
    query = """
    MATCH (a:Account {id:$id})
    RETURN a.id AS id, a.name AS name, a.industry AS industry, a.size AS size, a.revenue AS revenue
    """
    with driver.session() as session:
        record = session.run(query, id=account_id).single()
        if not record:
            raise HTTPException(status_code=404, detail="Account not found")
        return Account(**record)

# -------------------------------
# Update Account
# -------------------------------
@router.patch("/{account_id}", response_model=Account)
def update_account(account_id: str, account: AccountUpdate):
    fields = ", ".join([f"a.{k}=${k}" for k in account.model_dump(exclude_unset=True).keys()])
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    query = f"""
    MATCH (a:Account {{id:$id}})
    SET {fields}
    RETURN a.id AS id, a.name AS name, a.industry AS industry, a.size AS size, a.revenue AS revenue
    """
    with driver.session() as session:
        record = session.run(query, **{"id": account_id, **account.model_dump(exclude_unset=True)}).single()
        if not record:
            raise HTTPException(status_code=404, detail="Account not found")
        return Account(**record)

# -------------------------------
# Optional: Link Lead to Account
# -------------------------------
@router.post("/{account_id}/link-lead/{lead_id}")
def link_lead_to_account(account_id: str, lead_id: str):
    query = """
    MATCH (a:Account {id:$account_id}), (l:Lead {id:$lead_id})
    MERGE (l)-[:BELONGS_TO]->(a)
    RETURN a.id AS account_id, l.id AS lead_id
    """
    with driver.session() as session:
        record = session.run(query, account_id=account_id, lead_id=lead_id).single()
        if not record:
            raise HTTPException(status_code=404, detail="Account or Lead not found")
        return {"message": f"Lead {lead_id} linked to Account {account_id}"}
