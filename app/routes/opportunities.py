from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.db import driver
from app.models.opportunity import Opportunity, OpportunityCreate, OpportunityUpdate
from app.utils.search import search_nodes

router = APIRouter()

# -------------------------------
# Create Opportunity
# -------------------------------
@router.post("/", response_model=Opportunity)
def create_opportunity(opportunity: OpportunityCreate):
    query = """
    MERGE (o:Opportunity {id:$id})
    SET o.name=$name, o.stage=$stage, o.estimated_value=$estimated_value, 
        o.probability=$probability, o.expected_close_date=$expected_close_date
    WITH o
    MATCH (l:Lead {id:$lead_id})
    MERGE (o)-[:FOR_LEAD]->(l)
    RETURN o.id AS id, o.name AS name, o.stage AS stage,
           o.estimated_value AS estimated_value, o.probability AS probability,
           o.expected_close_date AS expected_close_date, l.id AS lead_id
    """
    with driver.session() as session:
        record = session.run(query, **opportunity.model_dump()).single()
        if not record:
            raise HTTPException(status_code=404, detail="Lead not found for this opportunity")
        return Opportunity(**record)

# -------------------------------
# Get All Opportunities
# -------------------------------
@router.get("/", response_model=List[Opportunity])
def get_opportunities():
    query = """
    MATCH (o:Opportunity)-[:FOR_LEAD]->(l:Lead)
    RETURN o.id AS id, o.name AS name, o.stage AS stage,
           o.estimated_value AS estimated_value, o.probability AS probability,
           o.expected_close_date AS expected_close_date, l.id AS lead_id
    """
    with driver.session() as session:
        return [Opportunity(**r) for r in session.run(query)]

# -------------------------------
# Get Opportunity by ID
# -------------------------------
@router.get("/{opportunity_id}", response_model=Opportunity)
def get_opportunity(opportunity_id: str):
    query = """
    MATCH (o:Opportunity {id:$id})-[:FOR_LEAD]->(l:Lead)
    RETURN o.id AS id, o.name AS name, o.stage AS stage,
           o.estimated_value AS estimated_value, o.probability AS probability,
           o.expected_close_date AS expected_close_date, l.id AS lead_id
    """
    with driver.session() as session:
        record = session.run(query, id=opportunity_id).single()
        if not record:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        return Opportunity(**record)

# -------------------------------
# Update Opportunity
# -------------------------------
@router.patch("/{opportunity_id}", response_model=Opportunity)
def update_opportunity(opportunity_id: str, opportunity: OpportunityUpdate):
    fields = ", ".join([f"o.{k}=${k}" for k in opportunity.model_dump(exclude_unset=True).keys()])
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    query = f"""
    MATCH (o:Opportunity {{id:$id}})-[:FOR_LEAD]->(l:Lead)
    SET {fields}
    RETURN o.id AS id, o.name AS name, o.stage AS stage,
           o.estimated_value AS estimated_value, o.probability AS probability,
           o.expected_close_date AS expected_close_date, l.id AS lead_id
    """
    with driver.session() as session:
        record = session.run(query, **{"id": opportunity_id, **opportunity.model_dump(exclude_unset=True)}).single()
        if not record:
            raise HTTPException(status_code=404, detail="Opportunity not found")
        return Opportunity(**record)

# -------------------------------
# Optional: Link Opportunity to Account
# -------------------------------
@router.post("/{opportunity_id}/link-account/{account_id}")
def link_opportunity_to_account(opportunity_id: str, account_id: str):
    query = """
    MATCH (o:Opportunity {id:$opportunity_id}), (a:Account {id:$account_id})
    MERGE (o)-[:BELONGS_TO]->(a)
    RETURN o.id AS opportunity_id, a.id AS account_id
    """
    with driver.session() as session:
        record = session.run(query, opportunity_id=opportunity_id, account_id=account_id).single()
        if not record:
            raise HTTPException(status_code=404, detail="Opportunity or Account not found")
        return {"message": f"Opportunity {opportunity_id} linked to Account {account_id}"}
    
#Search by activity name:
@router.get("/search_name")
def search_users(name: str = Query(..., description="Search Opportunities by name")):
    try:
        results = search_nodes("Activity",name)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    
