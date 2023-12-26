from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.core.config import settings
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from backend.app.models.user import User
from backend.app.models.todo import Todo
from backend.app.models.vvz import SearchResult
from backend.app.api.v1.router import router



@asynccontextmanager
async def app_init(app: FastAPI):
    """ Initialize crucial application services """
    
    db_client = AsyncIOMotorClient(settings.MONGO_CONNECTION_STRING, uuidRepresentation="standard")
    await init_beanie(
        database=db_client.todolist,
        document_models=[
            User,
            Todo,
            SearchResult,
            ]
    )
    await les()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=app_init
)

app.include_router(router, prefix=settings.API_V1_STR)



async def les():
    import json
    from pymongo.errors import DuplicateKeyError 

    json_string = """
    [
    {
        "createdAt": "2023-12-18T12:01:19+01:00",
        "createdBy": {
            "email": "vladimira.zitkova01@kraj-lbc.cz",
            "id": "b6f54904-63df-4738-9325-7ce88f9586ed",
            "name": "VLADIMÍRA ZÍTKOVÁ"
        },
        "data": {
            "datumOdeslaniTed": "2023-12-18T13:17:34+01:00",
            "datumPrijetiVvz": "2023-12-18T13:12:25+01:00",
            "datumUverejneniTed": "2023-12-22T09:00:00+01:00",
            "datumUverejneniVvz": "2023-12-20T14:00:39+01:00",
            "druhFormulare": "F02",
            "evCisloTed": "2023/S 247-779685",
            "evCisloZakazkyVvz": "Z2023-058305",
            "lhutaNabidkyZadosti": "2024-01-25T10:00:00+01:00",
            "lhutaUverejneniTed": "2023-12-20T14:00:00+01:00",
            "lhutaUverejneniVvz": "2023-12-21T23:59:00+01:00",
            "nazevZakazky": "Výstavba pavilonu učeben Gymnázia F. X. Šaldy, Liberec 11, Partyzánská 530, příspěvková organizace",
            "souvisejiciFormSchemaId": "5a208f03-d409-43cf-a6fd-51b2579c485c",
            "uverejnitTed": true,
            "uverejnitVvz": true,
            "uzivatelskyNazevFormulare": "F02 Oznámení o zahájení zadávacího řízení",
            "verzeXsd": "R2.0.9.S05",
            "zadavatele": [
                {
                    "ico": "70891508",
                    "nazev": "Liberecký kraj"
                }
            ],
            "zakazkaZrusena": false,
            "zdrojPodani": {
                "id": "WEB-fgxvso",
                "typ": "WEB",
                "uzivatelVvzLogin": "fgxvso"
            }
        },
        "formSchema": "/api/form_schemas/9c65adb0-e9be-4489-93fc-e4e1f1b526d1",
        "id": "a7b78a6a-dd67-4646-b09b-670407858fec",
        "organizationData": {
            "addresses": null,
            "attributes": null,
            "contacts": null,
            "description": null,
            "id": "5d01949c-1bf9-4aaf-88fd-55e2d885399c",
            "identifications": null,
            "name": "Liberecký kraj"
        },
        "owner": {
            "email": "vladimira.zitkova01@kraj-lbc.cz",
            "id": "b6f54904-63df-4738-9325-7ce88f9586ed",
            "name": "VLADIMÍRA ZÍTKOVÁ"
        },
        "publicId": "4XJKLQhMRMcMmNEI9fBkOPFNoePbUhz3",
        "submissionVersion": "/api/submission_versions/ca6fdeb5-b263-4b6f-bd7c-4f1097089d92",
        "updatedAt": "2023-12-22T09:01:37+01:00",
        "updatedBy": {
            "id": "b6dee6f2-1d53-44e4-80c6-63e85e545649",
            "name": "vvz-uloziste-formularu-bridge"
        },
        "variableId": "F2023-058305",
        "workflowPlaceCode": "UVEREJNENO_VVZ"
    },
    {
        "createdAt": "2023-12-14T15:20:15+01:00",
        "createdBy": {
            "email": "richard.zetek@ethanolenergy.cz",
            "id": "740f667d-2703-41d9-9d2e-a8fb5c0ca184",
            "name": "RICHARD ZETEK"
        },
        "data": {
            "datumOdeslaniTed": "2023-12-18T13:04:49+01:00",
            "datumPrijetiVvz": "2023-12-18T13:04:47+01:00",
            "datumUverejneniTed": "2023-12-22T09:00:00+01:00",
            "datumUverejneniVvz": "2023-12-20T14:00:18+01:00",
            "druhFormulare": "F02",
            "evCisloTed": "2023/S 247-777173",
            "evCisloZakazkyVvz": "Z2023-058296",
            "lhutaNabidkyZadosti": "2024-02-29T12:00:00+01:00",
            "lhutaUverejneniTed": "2023-12-20T14:00:00+01:00",
            "lhutaUverejneniVvz": "2023-12-21T23:59:00+01:00",
            "nazevZakazky": "VYUŽITÍ ENERGETICKÉHO POTENCIÁLU VEDLEJŠÍCH PROUDŮ V ETHANOL ENERGY a.s.",
            "souvisejiciFormSchemaId": "5a208f03-d409-43cf-a6fd-51b2579c485c",
            "uverejnitTed": true,
            "uverejnitVvz": true,
            "uzivatelskyNazevFormulare": "F02 Oznámení o zahájení zadávacího řízení",
            "verzeXsd": "R2.0.9.S05",
            "zadavatele": [
                {
                    "ico": "25502492",
                    "nazev": "Ethanol Energy a.s."
                }
            ],
            "zakazkaZrusena": false,
            "zdrojPodani": {
                "id": "WEB-frfsgv",
                "typ": "WEB",
                "uzivatelVvzLogin": "frfsgv"
            }
        },
        "formSchema": "/api/form_schemas/9c65adb0-e9be-4489-93fc-e4e1f1b526d1",
        "id": "20d14814-a2e2-4cf7-827b-f52c5d668187",
        "organizationData": {
            "addresses": null,
            "attributes": null,
            "contacts": null,
            "description": null,
            "id": "4a13b33d-2c2f-4053-9a4a-4b22615a3c71",
            "identifications": null,
            "name": "Ethanol Energy a.s."
        },
        "owner": {
            "email": "richard.zetek@ethanolenergy.cz",
            "id": "740f667d-2703-41d9-9d2e-a8fb5c0ca184",
            "name": "RICHARD ZETEK"
        },
        "publicId": "O1Nrw2rDy7S8TZX3ZJgqOx8ROjwgfv8t",
        "submissionVersion": "/api/submission_versions/0d5f2e0e-87ba-4b6b-ad5c-3b0724c79cec",
        "updatedAt": "2023-12-22T09:01:42+01:00",
        "updatedBy": {
            "id": "b6dee6f2-1d53-44e4-80c6-63e85e545649",
            "name": "vvz-uloziste-formularu-bridge"
        },
        "variableId": "F2023-058296",
        "workflowPlaceCode": "UVEREJNENO_VVZ"
    },
    {
        "createdAt": "2023-12-18T09:11:36+01:00",
        "createdBy": {
            "email": "vladimira.zitkova01@kraj-lbc.cz",
            "id": "b6f54904-63df-4738-9325-7ce88f9586ed",
            "name": "VLADIMÍRA ZÍTKOVÁ"
        },
        "data": {
            "datumOdeslaniTed": "2023-12-18T09:19:24+01:00",
            "datumPrijetiVvz": "2023-12-18T09:19:21+01:00",
            "datumUverejneniTed": "2023-12-22T09:00:00+01:00",
            "datumUverejneniVvz": "2023-12-20T14:00:10+01:00",
            "druhFormulare": "F02",
            "evCisloTed": "2023/S \r\n247-781346",
            "evCisloZakazkyVvz": "Z2023-058183",
            "lhutaNabidkyZadosti": "2024-01-26T10:00:00+01:00",
            "lhutaUverejneniTed": "2023-12-20T14:00:00+01:00",
            "lhutaUverejneniVvz": "2023-12-21T23:59:00+01:00",
            "nazevZakazky": "Hudební kulturně kreativní centrum Lidové sady, Liberec – stavební práce",
            "souvisejiciFormSchemaId": "5a208f03-d409-43cf-a6fd-51b2579c485c",
            "uverejnitTed": true,
            "uverejnitVvz": true,
            "uzivatelskyNazevFormulare": "F02 Oznámení o zahájení zadávacího řízení",
            "verzeXsd": "R2.0.9.S05",
            "zadavatele": [
                {
                    "ico": "70891508",
                    "nazev": "Liberecký kraj"
                }
            ],
            "zakazkaZrusena": false,
            "zdrojPodani": {
                "id": "WEB-fgxvso",
                "typ": "WEB",
                "uzivatelVvzLogin": "fgxvso"
            }
        },
        "formSchema": "/api/form_schemas/9c65adb0-e9be-4489-93fc-e4e1f1b526d1",
        "id": "7f431bfd-327f-41f6-9e03-e9d39c0804fe",
        "organizationData": {
            "addresses": null,
            "attributes": null,
            "contacts": null,
            "description": null,
            "id": "5d01949c-1bf9-4aaf-88fd-55e2d885399c",
            "identifications": null,
            "name": "Liberecký kraj"
        },
        "owner": {
            "email": "vladimira.zitkova01@kraj-lbc.cz",
            "id": "b6f54904-63df-4738-9325-7ce88f9586ed",
            "name": "VLADIMÍRA ZÍTKOVÁ"
        },
        "publicId": "mO1vw8dePSpAYmN75TANbFV0FzLHG2K8",
        "submissionVersion": "/api/submission_versions/f6b26713-16e1-448d-a48a-14e671e4b14d",
        "updatedAt": "2023-12-22T09:01:08+01:00",
        "updatedBy": {
            "id": "b6dee6f2-1d53-44e4-80c6-63e85e545649",
            "name": "vvz-uloziste-formularu-bridge"
        },
        "variableId": "F2023-058183",
        "workflowPlaceCode": "UVEREJNENO_VVZ"
    }
]
    """

    json_object = json.loads(json_string, strict=False)



    todo = SearchResult(**json_object[0])

    try:
        await todo.insert()
    except DuplicateKeyError:
        print('Error inserting duplicate _id')





