from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from app.config import settings

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EmailLog(Base):
    """Persistent log of all processed emails."""
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    recipient = Column(String)
    subject = Column(String)
    body_preview = Column(Text)
    category = Column(String, index=True)
    confidence = Column(Float)
    reasoning = Column(Text)
    routed_to = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    organization_id = Column(String, index=True, default="default")


class RoutingRuleDB(Base):
    """Persistent routing rules."""
    __tablename__ = "routing_rules"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, unique=True, index=True)
    destination_type = Column(String)
    destination_target = Column(String)
    enabled = Column(Boolean, default=True)
    organization_id = Column(String, index=True, default="default")


class APIKey(Base):
    """API keys for authentication."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    name = Column(String)
    organization_id = Column(String, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    is_active = Column(Boolean, default=True)


class Organization(Base):
    """Multi-tenant organization support."""
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    plan = Column(String, default="free")  # free, pro, business, enterprise
    stripe_customer_id = Column(String, nullable=True)
    email_quota = Column(Integer, default=100)  # emails per month
    emails_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
