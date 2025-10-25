from fastapi import APIRouter, HTTPException
from typing import List
from app.db import driver
from app.models.lead import Lead, LeadCreate, LeadUpdate

router = APIRouter()

# Create Lead
@router.post("/", response_model=Lead)
def create_lead(lead: LeadCreate):
    query = """
    MERGE (l:Lead {id:$id})
    ON CREATE SET l.name=$name, l.email=$email, l.source=$source, l.status=$status, l.score=$score, l.value=$value
    ON MATCH SET l.name=$name, l.email=$email, l.source=$source, l.status=$status, l.score=$score, l.value=$value
    WITH l
    OPTIONAL MATCH (u:User {id:$assigned_to})
    OPTIONAL MATCH (a:Account {id:$account_id})
    FOREACH (_ IN CASE WHEN u IS NOT NULL THEN [1] ELSE [] END |
        MERGE (l)-[:ASSIGNED_TO]->(u)
    )
    FOREACH (_ IN CASE WHEN a IS NOT NULL THEN [1] ELSE [] END |
        MERGE (l)-[:BELONGS_TO]->(a)
    )
    RETURN l.id AS id, l.name AS name, l.email AS email, l.source AS source,
           l.status AS status, l.score AS score, l.value AS value,
           $assigned_to AS assigned_to, $account_id AS account_id
    """
    with driver.session() as session:
        result = session.run(query, **lead.model_dump())
        record = result.single()
        return Lead(**record)

# Get All Leads
@router.get("/", response_model=List[Lead])
def get_leads():
    query = """
    MATCH (l:Lead)
    OPTIONAL MATCH (l)-[:ASSIGNED_TO]->(u:User)
    OPTIONAL MATCH (l)-[:BELONGS_TO]->(a:Account)
    RETURN l.id AS id, l.name AS name, l.email AS email, l.source AS source,
           l.status AS status, l.score AS score, l.value AS value,
           u.id AS assigned_to, a.id AS account_id
    """
    with driver.session() as session:
        result = session.run(query)
        leads = [Lead(**record) for record in result]
        return leads

# Get Lead by ID
@router.get("/{lead_id}", response_model=Lead)
def get_lead(lead_id: str):
    query = """
    MATCH (l:Lead {id:$id})
    OPTIONAL MATCH (l)-[:ASSIGNED_TO]->(u:User)
    OPTIONAL MATCH (l)-[:BELONGS_TO]->(a:Account)
    RETURN l.id AS id, l.name AS name, l.email AS email, l.source AS source,
           l.status AS status, l.score AS score, l.value AS value,
           u.id AS assigned_to, a.id AS account_id
    """
    with driver.session() as session:
        result = session.run(query, id=lead_id)
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Lead not found")
        return Lead(**record)

# Update Lead
@router.patch("/{lead_id}", response_model=Lead)
def update_lead(lead_id: str, lead: LeadUpdate):
    fields = ", ".join([f"l.{k}=${k}" for k in lead.model_dump(exclude_unset=True).keys()])
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    query = f"""
    MATCH (l:Lead {{id:$id}})
    SET {fields}
    RETURN l.id AS id, l.name AS name, l.email AS email, l.source AS source,
           l.status AS status, l.score AS score, l.value AS value
    """
    with driver.session() as session:
        result = session.run(query, **{"id": lead_id, **lead.model_dump(exclude_unset=True)})
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Lead not found")
        return Lead(**record)
