from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.db import driver
from app.models.deal import Deal, DealCreate, DealUpdate
from app.utils.search import search_nodes

router = APIRouter()

# -------------------------------
# Create Deal (linked to Opportunity)
# -------------------------------
@router.post("/", response_model=Deal)
def create_deal(deal: DealCreate):
    query = """
    MERGE (d:Deal {id:$id})
    SET d.name=$name, d.stage=$stage, d.value=$value, d.close_date=$close_date
    WITH d
    MATCH (o:Opportunity {id:$opportunity_id})
    MERGE (d)-[:FOR_OPPORTUNITY]->(o)
    RETURN d.id AS id, d.name AS name, d.stage AS stage, d.value AS value,
           d.close_date AS close_date, o.id AS opportunity_id
    """
    with driver.session() as session:
        record = session.run(query, **deal.model_dump()).single()
        if not record:
            raise HTTPException(status_code=404, detail="Opportunity not found for this deal")
        return Deal(**record)

# -------------------------------
# Get All Deals
# -------------------------------
@router.get("/", response_model=List[Deal])
def get_deals():
    query = """
    MATCH (d:Deal)-[:FOR_OPPORTUNITY]->(o:Opportunity)
    RETURN d.id AS id, d.name AS name, d.stage AS stage, d.value AS value,
           d.close_date AS close_date, o.id AS opportunity_id
    """
    with driver.session() as session:
        return [Deal(**r) for r in session.run(query)]

# -------------------------------
# Get Deal by ID
# -------------------------------
@router.get("/{deal_id}", response_model=Deal)
def get_deal(deal_id: str):
    query = """
    MATCH (d:Deal {id:$id})-[:FOR_OPPORTUNITY]->(o:Opportunity)
    RETURN d.id AS id, d.name AS name, d.stage AS stage, d.value AS value,
           d.close_date AS close_date, o.id AS opportunity_id
    """
    with driver.session() as session:
        record = session.run(query, id=deal_id).single()
        if not record:
            raise HTTPException(status_code=404, detail="Deal not found")
        return Deal(**record)

# -------------------------------
# Update Deal
# -------------------------------
@router.patch("/{deal_id}", response_model=Deal)
def update_deal(deal_id: str, deal: DealUpdate):
    fields = ", ".join([f"d.{k}=${k}" for k in deal.model_dump(exclude_unset=True).keys()])
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    query = f"""
    MATCH (d:Deal {{id:$id}})-[:FOR_OPPORTUNITY]->(o:Opportunity)
    SET {fields}
    RETURN d.id AS id, d.name AS name, d.stage AS stage, d.value AS value,
           d.close_date AS close_date, o.id AS opportunity_id
    """
    with driver.session() as session:
        record = session.run(query, **{"id": deal_id, **deal.model_dump(exclude_unset=True)}).single()
        if not record:
            raise HTTPException(status_code=404, detail="Deal not found")
        return Deal(**record)

# -------------------------------
# Optional: Link Deal to Account
# -------------------------------
@router.post("/{deal_id}/link-account/{account_id}")
def link_deal_to_account(deal_id: str, account_id: str):
    query = """
    MATCH (d:Deal {id:$deal_id}), (a:Account {id:$account_id})
    MERGE (d)-[:BELONGS_TO]->(a)
    RETURN d.id AS deal_id, a.id AS account_id
    """
    with driver.session() as session:
        record = session.run(query, deal_id=deal_id, account_id=account_id).single()
        if not record:
            raise HTTPException(status_code=404, detail="Deal or Account not found")
        return {"message": f"Deal {deal_id} linked to Account {account_id}"}


#Search by activity name:
@router.get("/search_name")
def search_users(name: str = Query(..., description="Search Deal by name")):
    try:
        results = search_nodes("Deal",name)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))