import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.contract import Contract, ContractCreate
from app.core.database import async_session
from zakazka.vvz import VvzCrawler
from zakazka.zakazky_III import vvz_zakazka2dict


logger = logging.getLogger(__name__)


class CrawlerService:
    """Service for crawling VVZ data and storing in database"""
    
    def __init__(self):
        self.crawler = VvzCrawler()
    
    async def crawl_contracts(self, date_from: date, date_to: date) -> int:
        """Crawl contracts for a date range and store in database"""
        print(f"CRAWL_CONTRACTS CALLED: {date_from} to {date_to}")
        logger.info(f"Starting crawl for date range: {date_from} to {date_to}")
        
        contracts_found = 0
        
        async with async_session() as session:
            # Crawl PRACE contracts
            prace_contracts = await self._crawl_contract_type(
                session, date_from, date_to, "PRACE"
            )
            contracts_found += prace_contracts
            
            # Crawl SLUZBY contracts  
            sluzby_contracts = await self._crawl_contract_type(
                session, date_from, date_to, "SLUZBY", from_sluzby=True
            )
            contracts_found += sluzby_contracts
            
            await session.commit()
        
        logger.info(f"Crawl completed. Found {contracts_found} new contracts.")
        return contracts_found
    
    async def _crawl_contract_type(
        self, 
        session: AsyncSession, 
        date_from: date, 
        date_to: date, 
        contract_type: str,
        from_sluzby: bool = False
    ) -> int:
        """Crawl contracts of specific type"""
        query = {
            "date_from": date_from,
            "date_to": date_to + timedelta(days=1),
            "druh_vz": contract_type,
        }
        
        try:
            zakazky_list = self.crawler.get_search_results(query, mock=False)
            print(f"Found {len(zakazky_list)} {contract_type} contracts")
            logger.info(f"Found {len(zakazky_list)} {contract_type} contracts")
            
            contracts_saved = 0
            
            for zakazka in zakazky_list:
                try:
                    # Check if contract already exists
                    external_id = zakazka.get('id', str(zakazka))
                    print(f"Zakazka data keys: {list(zakazka.keys()) if isinstance(zakazka, dict) else 'Not a dict'}")
                    print(f"Zakazka sample: {str(zakazka)[:200]}...")
                    logger.info(f"Processing contract {external_id}")
                    
                    existing = await session.execute(
                        select(Contract).where(Contract.external_id == external_id)
                    )
                    existing_contract = existing.scalars().first()
                    if existing_contract:
                        print(f"Contract {external_id} already exists, skipping")
                        logger.info(f"Contract {external_id} already exists, skipping")
                        continue
                    else:
                        print(f"Contract {external_id} is NEW, processing...")
                    
                    # Get detailed contract data
                    print(f"Getting form submissions for {external_id}")
                    logger.info(f"Getting form submissions for {external_id}")
                    form_vvz_id = zakazka["data"]["evCisloZakazkyVvz"]
                    print(f"Form VVZ ID: {form_vvz_id}")
                    form_submissions = self.crawler.get_form_submissions(form_vvz_id=form_vvz_id, mock=False)
                    print(f"Form submissions result: {len(form_submissions) if form_submissions else 'None'}")
                    if not form_submissions:
                        print(f"No form submissions found for {external_id}")
                        logger.info(f"No form submissions found for {external_id}")
                        continue
                    
                    print(f"Getting form detail for {external_id}")
                    logger.info(f"Getting form detail for {external_id}")
                    form_detail = self.crawler.get_form_detail(form_submission=zakazka["id"], mock=False)
                    print(f"Form detail result: {'Found' if form_detail else 'None'}")
                    if not form_detail:
                        print(f"No form detail found for {external_id}")
                        logger.info(f"No form detail found for {external_id}")
                        continue
                    
                    # Convert to structured dictionary
                    logger.info(f"Converting to dict for {external_id}")
                    contract_dict = vvz_zakazka2dict(form_detail[0], form_submissions[0])
                    if not contract_dict:
                        logger.info(f"Failed to convert contract data for {external_id}")
                        continue
                    
                    logger.info(f"Contract dict keys: {list(contract_dict.keys())}")
                    print(f"Contract dict sample data: {dict(list(contract_dict.items())[:15])}")
                    
                    # Create contract model
                    logger.info(f"Creating contract model for {external_id}")
                    contract_data = self._convert_to_contract_model(
                        contract_dict, contract_type, from_sluzby, date_from, external_id
                    )
                    
                    if contract_data:
                        logger.info(f"Contract data created: {contract_data}")
                        contract = Contract(**contract_data)
                        session.add(contract)
                        contracts_saved += 1
                        logger.info(f"Saved contract: {contract_data['title'][:50]}... (pub_date: {contract_data['publication_date']})")
                    else:
                        logger.info(f"Failed to create contract model for {external_id}")
                        
                except Exception as e:
                    logger.error(f"Error processing contract {external_id}: {e}", exc_info=True)
                    # Rollback session on error to prevent further issues
                    await session.rollback()
                    continue
            
            return contracts_saved
            
        except Exception as e:
            logger.error(f"Error crawling {contract_type} contracts: {e}")
            return 0
    
    def _convert_to_contract_model(
        self, 
        contract_dict: Dict[str, Any], 
        contract_type: str,
        from_sluzby: bool,
        publication_date: date,
        external_id: str
    ) -> Dict[str, Any]:
        """Convert crawler result to contract model data"""
        try:
            # Extract price value
            price_value = None
            if contract_dict.get('hodnota'):
                try:
                    price_value = float(contract_dict['hodnota'])
                except (ValueError, TypeError):
                    pass
            
            # Parse bid deadline
            bid_deadline = None
            if contract_dict.get('lhuta_pro_nabidky'):
                try:
                    bid_deadline = datetime.strptime(
                        contract_dict['lhuta_pro_nabidky'], "%d/%m/%Y"
                    )
                except (ValueError, TypeError):
                    pass
            
            return {
                "external_id": external_id,  # Use the zakazka ID which is unique
                "title": contract_dict.get('nazev_vz', ''),
                "contracting_authority": contract_dict.get('zadavatel', ''),
                "contract_type": contract_type,
                "price_value": price_value,
                "price_currency": "CZK",
                "bid_deadline": bid_deadline,
                "publication_date": publication_date,
                "nuts_code": contract_dict.get('nuts_kod'),
                "description": contract_dict.get('popis'),
                "supplier": contract_dict.get('dodavatel'),
                "contact_person": contract_dict.get('kontaktni_osoba'),
                "contact_email": contract_dict.get('email'),
                "contact_phone": contract_dict.get('telefon'),
                "from_sluzby": from_sluzby,
                "processed": False
            }
            
        except Exception as e:
            logger.error(f"Error converting contract data: {e}")
            return None
    
    async def crawl_today(self) -> int:
        """Crawl contracts for today (yesterday to tomorrow range)"""
        today = date.today()
        date_from = today - timedelta(days=1)
        date_to = today + timedelta(days=1)
        
        logger.info(f"Crawling for date range: {date_from} to {date_to} (today is {today})")
        return await self.crawl_contracts(date_from, date_to)


crawler_service = CrawlerService()
