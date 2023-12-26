from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class CreatedBy(BaseModel):
    email: EmailStr = None
    id: UUID
    name: str

class ZdrojPodani(BaseModel):
    id: str
    typ: str 
    uzivatelVvzLogin: str

class Zadavatele(BaseModel):
    ico: str
    nazev: str
    
class Data(BaseModel):
    datumOdeslaniTed: datetime = None
    datumPrijetiVvz: datetime
    datumUverejneniTed: datetime = None
    datumUverejneniVvz: datetime
    druhFormulare: str
    evCisloTed: str = None
    evCisloZakazkyVvz: str
    lhutaNabidkyZadosti: datetime = None
    lhutaUverejneniTed: datetime = None
    lhutaUverejneniVvz: datetime
    nazevZakazky: str
    souvisejiciFormSchemaId: UUID
    uverejnitTed: bool
    uverejnitVvz: bool
    uzivatelskyNazevFormulare: str = None
    verzeXsd: str
    zadavatele: list[Zadavatele]
    zakazkaZrusena: bool
    zdrojPodani: ZdrojPodani
    
class OrganizationData(BaseModel):
    addresses: dict | None
    attributes: dict | None
    contacts: dict | None
    description: str | None
    id: UUID
    identifications: dict | None
    name: str

class SearchResultSchema(BaseModel):
    createdAt: datetime 
    createdBy: CreatedBy
    data: Data
    formSchema: str
    id: UUID
    organizationData: OrganizationData
    owner: CreatedBy
    publicId: str
    submissionVersion: str
    updatedAt: datetime
    updatedBy: CreatedBy
    variableId: str
    workflowPlaceCode: str
