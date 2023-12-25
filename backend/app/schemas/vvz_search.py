from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class CreatedBy(BaseModel):
    email: EmailStr 
    id: UUID
    name: str

class UpdatedBy(CreatedBy):
    email: EmailStr = None

class ZdrojPodani(BaseModel):
    id: str
    typ: str 
    uzivatelVvzLogin: str

class Zadavatele(BaseModel):
    ico: str
    nazev: str
    
class Data(BaseModel):
    datumOdeslaniTed: datetime
    datumPrijetiVvz: datetime
    datumUverejneniTed: datetime 
    datumUverejneniVvz: datetime
    druhFormulare: str
    evCisloTed: str
    evCisloZakazkyVvz: str
    lhutaNabidkyZadosti: datetime
    lhutaUverejneniTed: datetime
    lhutaUverejneniVvz: datetime
    nazevZakazky: str
    souvisejiciFormSchemaId: UUID
    uverejnitTed: bool
    uverejnitVvz: bool
    uzivatelskyNazevFormulare: str
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

class Result(BaseModel):
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
    updatedBy: UpdatedBy
    variableId: str
    workflowPlaceCode: str
