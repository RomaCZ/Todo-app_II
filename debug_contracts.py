import asyncio
from app.core.database import get_session
from app.models.contract import Contract
from app.services.html_generator import HTMLGeneratorService
from sqlalchemy import select

async def debug_contracts():
    """Debug contract data conversion"""
    
    async for session in get_session():
        try:
            # Get first contract
            query = select(Contract).limit(1)
            result = await session.execute(query)
            contract = result.scalar_one_or_none()
            
            if contract:
                print("Contract data:")
                print(f"ID: {contract.id}")
                print(f"External ID: {contract.external_id}")
                print(f"Title: {contract.title}")
                print(f"Publication Date: {contract.publication_date}")
                print(f"Bid Deadline: {contract.bid_deadline}")
                print(f"Contract Type: {contract.contract_type}")
                print(f"Price Value: {contract.price_value}")
                print(f"Description: {contract.description}")
                
                # Try to convert to dict
                html_generator = HTMLGeneratorService()
                try:
                    contract_dict = html_generator._contract_to_dict(contract)
                    print("\nConversion successful!")
                    print(f"Converted keys: {list(contract_dict.keys())}")
                except Exception as e:
                    print(f"\nConversion failed: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("No contracts found in database")
                
        except Exception as e:
            print(f"Database error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(debug_contracts())
