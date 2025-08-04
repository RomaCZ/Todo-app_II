from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel


class ContractBase(SQLModel):
    """Base contract model with shared fields"""
    external_id: str = Field(index=True, unique=True)
    title: str = Field(index=True)
    contracting_authority: str
    contract_type: str  # "PRACE" or "SLUZBY"
    price_value: Optional[float] = None
    price_currency: str = "CZK"
    bid_deadline: Optional[datetime] = None
    publication_date: date = Field(index=True)
    nuts_code: Optional[str] = None
    description: Optional[str] = None
    supplier: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    from_sluzby: bool = False
    processed: bool = False


class Contract(ContractBase, table=True):
    """Database contract model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContractCreate(ContractBase):
    """Contract creation model"""
    pass


class ContractRead(ContractBase):
    """Contract read model"""
    id: int
    created_at: datetime
    updated_at: datetime


class ContractUpdate(BaseModel):
    """Contract update model"""
    processed: bool
