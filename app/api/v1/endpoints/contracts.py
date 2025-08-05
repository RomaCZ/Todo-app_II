import logging
from datetime import date
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pydantic import BaseModel

from app.core.database import get_session
from app.models.contract import Contract, ContractRead, ContractUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ContractRead])
async def get_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    contract_type: Optional[str] = Query(None, regex="^(PRACE|SLUZBY)$"),
    processed: Optional[bool] = None,
    session: AsyncSession = Depends(get_session)
):
    """Get contracts with filtering"""
    query = select(Contract)
    
    if date_from:
        query = query.where(Contract.publication_date >= date_from)
    if date_to:
        query = query.where(Contract.publication_date <= date_to)
    if contract_type:
        query = query.where(Contract.contract_type == contract_type)
    if processed is not None:
        query = query.where(Contract.processed == processed)
    
    query = query.order_by(Contract.publication_date.desc()).offset(skip).limit(limit)
    
    result = await session.execute(query)
    contracts = result.scalars().all()
    
    # Debug logging
    logger.info(f"Query returned {len(contracts)} contracts")
    if len(contracts) > 0:
        logger.info(f"First contract date: {contracts[0].publication_date}")
    
    return contracts


@router.get("/{contract_id}", response_model=ContractRead)
async def get_contract(
    contract_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get a specific contract"""
    result = await session.get(Contract, contract_id)
    if not result:
        raise HTTPException(status_code=404, detail="Contract not found")
    return result


@router.patch("/{contract_id}", response_model=ContractRead)
async def update_contract(
    contract_id: int,
    contract_update: ContractUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update contract (e.g., mark as processed)"""
    contract = await session.get(Contract, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract.processed = contract_update.processed
    session.add(contract)
    await session.commit()
    await session.refresh(contract)
    
    return contract


@router.get("/debug/all")
async def get_all_contracts_debug(session: AsyncSession = Depends(get_session)):
    """Debug endpoint to see all contracts in database"""
    query = select(Contract).order_by(Contract.created_at.desc()).limit(20)
    result = await session.execute(query)
    contracts = result.scalars().all()
    
    return {
        "total_count": len(contracts),
        "contracts": [
            {
                "id": c.id,
                "title": c.title,
                "publication_date": c.publication_date,
                "contract_type": c.contract_type,
                "external_id": c.external_id
            } for c in contracts
        ]
    }


@router.delete("/clear-all")
async def clear_all_contracts(session: AsyncSession = Depends(get_session)):
    """Clear all contracts from database (for testing)"""
    from sqlalchemy import delete
    
    # Delete all contracts
    delete_stmt = delete(Contract)
    result = await session.execute(delete_stmt)
    await session.commit()
    
    return {
        "message": f"Cleared {result.rowcount} contracts from database"
    }


@router.get("/stats/summary")
async def get_contract_stats(
    session: AsyncSession = Depends(get_session)
):
    """Get contract statistics"""
    total_query = select(Contract)
    total_result = await session.execute(total_query)
    total_contracts = len(total_result.scalars().all())
    
    processed_query = select(Contract).where(Contract.processed == True)
    processed_result = await session.execute(processed_query)
    processed_contracts = len(processed_result.scalars().all())
    
    prace_query = select(Contract).where(Contract.contract_type == "PRACE")
    prace_result = await session.execute(prace_query)
    prace_contracts = len(prace_result.scalars().all())
    
    sluzby_query = select(Contract).where(Contract.contract_type == "SLUZBY")
    sluzby_result = await session.execute(sluzby_query)
    sluzby_contracts = len(sluzby_result.scalars().all())
    
    return {
        "total_contracts": total_contracts,
        "processed_contracts": processed_contracts,
        "unprocessed_contracts": total_contracts - processed_contracts,
        "prace_contracts": prace_contracts,
        "sluzby_contracts": sluzby_contracts
    }


class ContractFieldUpdate(BaseModel):
    """Model for updating individual contract fields"""
    description: Optional[str] = None  # Used as comment
    title: Optional[str] = None
    contracting_authority: Optional[str] = None
    price_value: Optional[float] = None
    bid_deadline: Optional[str] = None  # Date string that will be parsed
    contract_type: Optional[str] = None
    nuts_code: Optional[str] = None
    supplier: Optional[str] = None
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    processed: Optional[bool] = None


@router.patch("/{contract_id}")
async def update_contract_field(
    contract_id: int,
    field_update: ContractFieldUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update specific fields of a contract (for manual processing interface)"""
    
    # Find the contract
    query = select(Contract).where(Contract.id == contract_id)
    result = await session.execute(query)
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    # Update fields that were provided
    update_data = field_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(contract, field):
            setattr(contract, field, value)
    
    session.add(contract)
    await session.commit()
    await session.refresh(contract)
    
    return {"message": "Contract updated successfully", "contract_id": contract_id}
