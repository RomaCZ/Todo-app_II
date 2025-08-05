"""HTML generation service for manual processing interface."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.models.contract import Contract


class HTMLGeneratorService:
    """Service for generating manual processing HTML interface."""
    
    def __init__(self):
        # Get templates path
        self.templates_path = Path(__file__).parent.parent / "templates"
    
    def generate_manual_processing_page(
        self, 
        contracts: List[Contract],
        search_date: Optional[str] = None
    ) -> HTMLResponse:
        """Generate the manual processing HTML page with contracts."""
        
        if search_date is None:
            search_date = datetime.now().strftime("%d/%m/%Y")
        
        # Read template file
        template_path = self.templates_path / "manual_processing.html"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace template variables
        html_content = html_content.replace("{{search_date}}", search_date)
        
        return HTMLResponse(content=html_content)
    
    def _contract_to_dict(self, contract: Contract) -> Dict[str, Any]:
        """Convert Contract model to dictionary format for HTML generation."""
        
        # Format price value
        price_text = None
        if contract.price_value:
            price_text = f"{contract.price_value:,.2f} {contract.price_currency}"
        
        # Map contract fields to the format expected by the original HTML generator
        contract_dict = {
            "id": contract.id,
            "external_id": contract.external_id,
            "evidencni_cislo": contract.external_id,
            "nazev_vz": contract.title,
            "zadavatel": contract.contracting_authority,
            "predp_hodnota_bez_dph": price_text,
            "lhuta_pro_nabidky": contract.bid_deadline.strftime("%d/%m/%Y") if contract.bid_deadline else None,
            "datum_uverejneni": contract.publication_date.strftime("%d/%m/%Y") if contract.publication_date else None,
            "typ_formulare": self._determine_form_type(contract),
            "druh_formulare": self._determine_form_type(contract),
            "druh_zakazky": self._determine_contract_type(contract),
            "rizeni": self._determine_procedure_type(contract),
            "url": self._generate_source_url(contract),
            "komentar": self._get_comment(contract),
            "created_at": contract.created_at.isoformat() if contract.created_at else None,
            "updated_at": contract.updated_at.isoformat() if contract.updated_at else None,
            "processing_status": "zpracováno" if contract.processed else "nezpracováno",
            
            # Additional fields for compatibility
            "misto_zakazky_nuts_parsed": self._extract_location(contract),
            "predp_hodnota_popis": "hodnota je předpokládaná" if contract.price_value else None,
            "popis": contract.description,
            "dodavatel": contract.supplier,
            "kontakt": self._format_contact(contract),
        }
        
        return contract_dict
    
    def _determine_contract_type(self, contract: Contract) -> str:
        """Determine contract type based on available data."""
        if contract.contract_type == "PRACE":
            return "Stavební práce"
        elif contract.contract_type == "SLUZBY":
            return "Služby"
        elif contract.from_sluzby:
            return "Služby"
        else:
            return "Stavební práce"
    
    def _determine_form_type(self, contract: Contract) -> str:
        """Determine form type based on contract data."""
        if contract.from_sluzby:
            return "Služby - formulář"
        elif contract.contract_type == "PRACE":
            return "Stavební práce - formulář"
        else:
            return "Formulář veřejné zakázky"
    
    def _determine_procedure_type(self, contract: Contract) -> str:
        """Determine procedure type."""
        # This could be enhanced based on other contract fields
        return "Otevřené řízení"  # Default
    
    def _generate_source_url(self, contract: Contract) -> Optional[str]:
        """Generate source URL for the contract."""
        # This would typically be the VVZ URL, but we might not have it stored
        # You could construct it from external_id if you know the pattern
        return f"https://ves.cz/contract/{contract.external_id}" if contract.external_id else None
    
    def _get_comment(self, contract: Contract) -> str:
        """Get comment for the contract."""
        # Since the original model doesn't have a comment field, we can use description
        return contract.description if contract.description else "Neuvedeno"
    
    def _format_contact(self, contract: Contract) -> Optional[str]:
        """Format contact information."""
        contact_parts = []
        if contract.contact_person:
            contact_parts.append(contract.contact_person)
        if contract.contact_email:
            contact_parts.append(contract.contact_email)
        if contract.contact_phone:
            contact_parts.append(contract.contact_phone)
        
        return "; ".join(contact_parts) if contact_parts else None
    
    def _extract_location(self, contract: Contract) -> Optional[str]:
        """Extract location information from contract."""
        # This could be enhanced to parse location from title or other fields
        if contract.title:
            # Simple heuristic to extract location
            title_upper = contract.title.upper()
            if "PRAHA" in title_upper:
                return "HLAVNÍ MĚSTO PRAHA"
            elif "BRNO" in title_upper:
                return "JIHOMORAVSKÝ KRAJ"
            # Add more location mapping as needed
        
        return None
    
    def get_form_fields_for_type(self, contract_type: str) -> List[Dict[str, Any]]:
        """Get form fields configuration for a specific contract type."""
        
        form_stavebni_prace = [
            {"text": "Evidenční číslo: ", "key": "evidencni_cislo"},
            {"text": "Místo zakázky: ", "key": "misto_zakazky_nuts_parsed", 
             "class": "misto_zakazky_nuts_parsed", "class_parent": "hidden_whole"},
            {"text": "Druh zakazky: ", "key": "druh_zakazky", "class_parent": "hidden_whole"},
            {"text": "Typ formuláře: ", "key": "typ_formulare"},
            {"text": "Druh formuláře: ", "key": "druh_formulare"},
            {"text": "Zadavatel: ", "key": "zadavatel"},
            {"text": "Název VZ: ", "key": "nazev_vz", "class": "nazev_vz"},
            {"text": "Předp. hodnota bez DPH: ", "key": "predp_hodnota_bez_dph", "class": "price"},
            {"text": "predp_hodnota_popis: ", "key": "predp_hodnota_popis", "class_parent": "hidden_whole"},
            {"text": "Druh řízení: ", "key": "rizeni", "class": "rizeni"},
            {"text": "Lhůta pro nabídky/žádosti: ", "key": "lhuta_pro_nabidky", "class": "date"},
            {"text": "Datum uveřejnění: ", "key": "datum_uverejneni"}
        ]
        
        form_predbezne_oznameni = [
            {"text": "Evidenční číslo: ", "key": "evidencni_cislo"},
            {"text": "Místo zakázky: ", "key": "misto_zakazky_nuts_parsed",
             "class": "misto_zakazky_nuts_parsed", "class_parent": "hidden_whole"},
            {"text": "Druh zakazky: ", "key": "druh_zakazky", "class_parent": "hidden_whole"},
            {"text": "Druh řízení: ", "key": "druh_formulare", "class": "druh_rizeni"},
            {"text": "Typ formuláře: ", "key": "typ_formulare"},
            {"text": "Zadavatel: ", "key": "zadavatel"},
            {"text": "Název VZ: ", "key": "nazev_vz", "class": "nazev_vz"},
            {"text": "Předp. hodnota bez DPH: ", "key": "predp_hodnota_bez_dph", "class": "price"},
            {"text": "predp_hodnota_popis: ", "key": "predp_hodnota_popis", "class_parent": "hidden_whole"},
            {"text": "Předpokládané datum zahájení zadávacího řízení: ",
             "key": "lhuta_pro_nabidky", "class": "date"},
            {"text": "Datum uveřejnění: ", "key": "datum_uverejneni"}
        ]
        
        form_sluzby = [
            {"text": "Evidenční číslo: ", "key": "evidencni_cislo"},
            {"text": "Místo zakázky: ", "key": "misto_zakazky_nuts_parsed",
             "class": "misto_zakazky_nuts_parsed", "class_parent": "hidden_whole"},
            {"text": "Druh zakazky: ", "key": "druh_zakazky",
             "class": "druh_zakazky", "class_parent": "hidden_whole"},
            {"text": "Typ formuláře: ", "key": "typ_formulare"},
            {"text": "Druh formuláře: ", "key": "druh_formulare"},
            {"text": "Zadavatel: ", "key": "zadavatel"},
            {"text": "Název VZ: ", "key": "nazev_vz", "class": "nazev_vz"},
            {"text": "Předp. hodnota bez DPH: ", "key": "predp_hodnota_bez_dph", "class": "price"},
            {"text": "predp_hodnota_popis: ", "key": "predp_hodnota_popis", "class_parent": "hidden_whole"},
            {"text": "Druh řízení: ", "key": "rizeni", "class": "rizeni"},
            {"text": "Lhůta pro nabídky/žádosti: ", "key": "lhuta_pro_nabidky", "class": "date"},
            {"text": "Datum uveřejnění: ", "key": "datum_uverejneni"}
        ]
        
        form_dict = {
            "Stavební práce": form_stavebni_prace,
            "Předběžné oznámení": form_predbezne_oznameni,
            "Služby": form_sluzby,
        }
        
        return form_dict.get(contract_type, form_stavebni_prace)
