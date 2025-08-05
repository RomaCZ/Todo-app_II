"""API endpoints for manual processing interface."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.contract import Contract
from app.services.html_generator import HTMLGeneratorService
from sqlalchemy import select

router = APIRouter()


@router.get("/manual-processing", response_class=HTMLResponse)
async def get_manual_processing_page(
    search_date: Optional[str] = Query(None, description="Date range for the page title"),
    limit: Optional[int] = Query(None, description="Limit number of contracts"),
    session: AsyncSession = Depends(get_session)
):
    """
    Generate and serve the manual processing interface.
    
    This endpoint recreates the functionality of the original zakazky_II_html.html
    but serves it dynamically with current contract data from the database.
    """
    try:
        # Fetch contracts from database
        query = select(Contract).order_by(Contract.created_at.desc())
        if limit:
            query = query.limit(limit)
        
        result = await session.execute(query)
        contracts = result.scalars().all()
        
        # Generate HTML using the service
        html_generator = HTMLGeneratorService()
        response = html_generator.generate_manual_processing_page(
            contracts=contracts,
            search_date=search_date
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating manual processing page: {str(e)}")


@router.get("/manual-processing/contract-data")
async def get_contracts_for_manual_processing(
    limit: Optional[int] = Query(100, description="Limit number of contracts"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get contract data in the format expected by the manual processing interface.
    """
    try:
        query = select(Contract).order_by(Contract.created_at.desc())
        if limit:
            query = query.limit(limit)
        
        result = await session.execute(query)
        contracts = result.scalars().all()
        
        # Convert to the format expected by the frontend
        html_generator = HTMLGeneratorService()
        contracts_data = []
        
        for contract in contracts:
            contract_dict = html_generator._contract_to_dict(contract)
            contracts_data.append(contract_dict)
        
        return {
            "contracts": contracts_data,
            "total_count": len(contracts_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching contract data: {str(e)}")


@router.get("/manual-processing/download")
async def download_manual_processing_html(
    search_date: Optional[str] = Query(None, description="Date range for the page title"),
    limit: Optional[int] = Query(None, description="Limit number of contracts"),
    session: AsyncSession = Depends(get_session)
):
    """
    Download the manual processing page as a standalone HTML file.
    
    This recreates the original workflow where a static HTML file was generated
    for offline manual processing.
    """
    try:
        from fastapi.responses import Response
        
        # Fetch contracts from database
        query = select(Contract).order_by(Contract.created_at.desc())
        if limit:
            query = query.limit(limit)
        
        result = await session.execute(query)
        contracts = result.scalars().all()
        
        # Generate HTML using the service
        html_generator = HTMLGeneratorService()
        
        response = html_generator.generate_manual_processing_page(
            contracts=contracts,
            search_date=search_date
        )
        
        # Get the HTML content as string  
        html_content = response.body.decode('utf-8') if hasattr(response, 'body') else response.content.decode('utf-8')
        
        # Return as downloadable file
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename=zakazky_manual_processing_{search_date or 'current'}.html"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating download: {str(e)}")
