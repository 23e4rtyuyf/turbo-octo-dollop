from typing import List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from app.db.database import get_db, RoutingRuleDB

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


class RoutingRule(BaseModel):
    category: str
    destination_type: str  # email, slack, webhook, discard
    destination_target: str
    enabled: bool = True


class RoutingRuleResponse(RoutingRule):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: str


@router.get("/", response_model=List[RoutingRuleResponse])
async def list_rules(org_id: str = "default", db: Session = Depends(get_db)):
    """List all routing rules for an organization."""
    rules = db.query(RoutingRuleDB).filter(RoutingRuleDB.organization_id == org_id).all()
    return rules


@router.post("/", response_model=RoutingRuleResponse)
async def create_rule(rule: RoutingRule, org_id: str = "default", db: Session = Depends(get_db)):
    """Create a new routing rule."""
    # Check if rule for this category already exists
    existing = db.query(RoutingRuleDB).filter(
        RoutingRuleDB.category == rule.category,
        RoutingRuleDB.organization_id == org_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Rule for category '{rule.category}' already exists.")

    db_rule = RoutingRuleDB(
        category=rule.category,
        destination_type=rule.destination_type,
        destination_target=rule.destination_target,
        enabled=rule.enabled,
        organization_id=org_id,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.put("/{rule_id}", response_model=RoutingRuleResponse)
async def update_rule(rule_id: int, rule: RoutingRule, db: Session = Depends(get_db)):
    """Update an existing routing rule."""
    db_rule = db.query(RoutingRuleDB).filter(RoutingRuleDB.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    db_rule.destination_type = rule.destination_type
    db_rule.destination_target = rule.destination_target
    db_rule.enabled = rule.enabled
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.delete("/{rule_id}")
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a routing rule."""
    db_rule = db.query(RoutingRuleDB).filter(RoutingRuleDB.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(db_rule)
    db.commit()
    return {"message": "Rule deleted"}
