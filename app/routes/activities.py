from fastapi import APIRouter, HTTPException
from typing import List
from app.db import driver
from app.models.activity import Activity, ActivityCreate, ActivityUpdate

router = APIRouter()

# -------------------------------
# Create Activity (linked to Lead, Opportunity, or Deal)
# -------------------------------
@router.post("/", response_model=Activity)
def create_activity(activity: ActivityCreate):
    query = """
    MERGE (act:Activity {id:$id})
    SET act.type=$type, act.date=$date, act.notes=$notes
    WITH act
    OPTIONAL MATCH (l:Lead {id:$lead_id})
    OPTIONAL MATCH (o:Opportunity {id:$opportunity_id})
    OPTIONAL MATCH (d:Deal {id:$deal_id})
    FOREACH(ignoreMe IN CASE WHEN l IS NOT NULL THEN [1] ELSE [] END |
        MERGE (act)-[:FOR_LEAD]->(l)
    )
    FOREACH(ignoreMe IN CASE WHEN o IS NOT NULL THEN [1] ELSE [] END |
        MERGE (act)-[:FOR_OPPORTUNITY]->(o)
    )
    FOREACH(ignoreMe IN CASE WHEN d IS NOT NULL THEN [1] ELSE [] END |
        MERGE (act)-[:FOR_DEAL]->(d)
    )
    RETURN act.id AS id, act.type AS type, act.date AS date, act.notes AS notes,
           l.id AS lead_id, o.id AS opportunity_id, d.id AS deal_id
    """
    with driver.session() as session:
        record = session.run(query, **activity.model_dump()).single()
        if not record:
            raise HTTPException(status_code=400, detail="Invalid references for activity")
        return Activity(**record)

# -------------------------------
# Get All Activities
# -------------------------------
@router.get("/", response_model=List[Activity])
def get_activities():
    query = """
    MATCH (act:Activity)
    OPTIONAL MATCH (act)-[:FOR_LEAD]->(l:Lead)
    OPTIONAL MATCH (act)-[:FOR_OPPORTUNITY]->(o:Opportunity)
    OPTIONAL MATCH (act)-[:FOR_DEAL]->(d:Deal)
    RETURN act.id AS id, act.type AS type, act.date AS date, act.notes AS notes,
           l.id AS lead_id, o.id AS opportunity_id, d.id AS deal_id
    """
    with driver.session() as session:
        return [Activity(**r) for r in session.run(query)]

# -------------------------------
# Get Activity by ID
# -------------------------------
@router.get("/{activity_id}", response_model=Activity)
def get_activity(activity_id: str):
    query = """
    MATCH (act:Activity {id:$id})
    OPTIONAL MATCH (act)-[:FOR_LEAD]->(l:Lead)
    OPTIONAL MATCH (act)-[:FOR_OPPORTUNITY]->(o:Opportunity)
    OPTIONAL MATCH (act)-[:FOR_DEAL]->(d:Deal)
    RETURN act.id AS id, act.type AS type, act.date AS date, act.notes AS notes,
           l.id AS lead_id, o.id AS opportunity_id, d.id AS deal_id
    """
    with driver.session() as session:
        record = session.run(query, id=activity_id).single()
        if not record:
            raise HTTPException(status_code=404, detail="Activity not found")
        return Activity(**record)

# -------------------------------
# Update Activity
# -------------------------------
@router.patch("/{activity_id}", response_model=Activity)
def update_activity(activity_id: str, activity: ActivityUpdate):
    fields = ", ".join([f"act.{k}=${k}" for k in activity.model_dump(exclude_unset=True).keys()])
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    query = f"""
    MATCH (act:Activity {{id:$id}})
    SET {fields}
    OPTIONAL MATCH (act)-[:FOR_LEAD]->(l:Lead)
    OPTIONAL MATCH (act)-[:FOR_OPPORTUNITY]->(o:Opportunity)
    OPTIONAL MATCH (act)-[:FOR_DEAL]->(d:Deal)
    RETURN act.id AS id, act.type AS type, act.date AS date, act.notes AS notes,
           l.id AS lead_id, o.id AS opportunity_id, d.id AS deal_id
    """
    with driver.session() as session:
        record = session.run(query, **{"id": activity_id, **activity.model_dump(exclude_unset=True)}).single()
        if not record:
            raise HTTPException(status_code=404, detail="Activity not found")
        return Activity(**record)
