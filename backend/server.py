from __future__ import annotations

import base64
import io
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from bson import ObjectId
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
db_name = os.environ.get("DB_NAME", "tikauditor")

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

app = FastAPI(title="TikTok Auditorium API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("tikauditor")


def oid_str(oid: ObjectId) -> str:
    return str(oid)


class ApiError(BaseModel):
    detail: str
    code: str


class HealthResponse(BaseModel):
    ok: bool
    mongo: bool
    timestamp: datetime


class OrgCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class OrgOut(BaseModel):
    id: str
    name: str
    created_at: datetime


class ProjectCreate(BaseModel):
    org_id: str
    name: str = Field(min_length=2, max_length=120)
    timezone: str = Field(default="UTC")
    language: Literal["ru", "en"] = "ru"


class ProjectOut(BaseModel):
    id: str
    org_id: str
    name: str
    timezone: str
    language: Literal["ru", "en"]
    created_at: datetime


class ManualImportItem(BaseModel):
    type: Literal["account", "video"]
    url: str = Field(min_length=5, max_length=500)


class ManualImportCreate(BaseModel):
    project_id: str
    items: list[ManualImportItem] = Field(default_factory=list)
    csv_base64: str | None = None


class ManualImportOut(BaseModel):
    id: str
    project_id: str
    status: Literal["queued", "done"]
    total_items: int
    created_at: datetime


@api_router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    mongo_ok = False
    try:
        await db.command("ping")
        mongo_ok = True
    except Exception as e:  # noqa: BLE001
        logger.warning("Mongo ping failed: %s", e)

    return HealthResponse(ok=True, mongo=mongo_ok, timestamp=datetime.utcnow())


@api_router.post("/orgs", response_model=OrgOut, responses={400: {"model": ApiError}})
async def create_org(payload: OrgCreate) -> OrgOut:
    now = datetime.utcnow()
    doc = {"name": payload.name.strip(), "created_at": now}
    res = await db.orgs.insert_one(doc)
    return OrgOut(id=oid_str(res.inserted_id), name=doc["name"], created_at=now)


@api_router.get("/orgs", response_model=list[OrgOut])
async def list_orgs(name: str | None = Query(default=None)) -> list[OrgOut]:
    q: dict[str, Any] = {}
    if name:
        q["name"] = name.strip()

    docs = await db.orgs.find(q).sort("created_at", -1).to_list(200)
    return [OrgOut(id=oid_str(d["_id"]), name=d["name"], created_at=d["created_at"]) for d in docs]


@api_router.post(
    "/projects",
    response_model=ProjectOut,
    responses={400: {"model": ApiError}, 404: {"model": ApiError}},
)
async def create_project(payload: ProjectCreate) -> ProjectOut:
    try:
        org_oid = ObjectId(payload.org_id)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid org_id")

    org = await db.orgs.find_one({"_id": org_oid})
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")

    now = datetime.utcnow()
    doc = {
        "org_id": org_oid,
        "name": payload.name.strip(),
        "timezone": payload.timezone,
        "language": payload.language,
        "created_at": now,
    }
    res = await db.projects.insert_one(doc)
    return ProjectOut(
        id=oid_str(res.inserted_id),
        org_id=payload.org_id,
        name=doc["name"],
        timezone=doc["timezone"],
        language=doc["language"],
        created_at=now,
    )


@api_router.get("/projects", response_model=list[ProjectOut])
async def list_projects(org_id: str | None = Query(default=None)) -> list[ProjectOut]:
    q: dict[str, Any] = {}
    if org_id:
        try:
            q["org_id"] = ObjectId(org_id)
        except Exception:  # noqa: BLE001
            raise HTTPException(status_code=400, detail="Invalid org_id")

    docs = await db.projects.find(q).sort("created_at", -1).to_list(500)
    out: list[ProjectOut] = []
    for d in docs:
        out.append(
            ProjectOut(
                id=oid_str(d["_id"]),
                org_id=oid_str(d["org_id"]),
                name=d["name"],
                timezone=d.get("timezone", "UTC"),
                language=d.get("language", "ru"),
                created_at=d["created_at"],
            )
        )
    return out


@api_router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str) -> ProjectOut:
    try:
        pid = ObjectId(project_id)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid project_id")

    d = await db.projects.find_one({"_id": pid})
    if not d:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectOut(
        id=oid_str(d["_id"]),
        org_id=oid_str(d["org_id"]),
        name=d["name"],
        timezone=d.get("timezone", "UTC"),
        language=d.get("language", "ru"),
        created_at=d["created_at"],
    )


def _parse_csv_items(csv_base64: str) -> list[ManualImportItem]:
    try:
        raw = base64.b64decode(csv_base64)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid csv_base64: {e}")

    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    cols = {c.lower(): c for c in df.columns}
    if "url" not in cols:
        raise HTTPException(status_code=400, detail="CSV must contain 'url' column")

    type_col = cols.get("type")
    items: list[ManualImportItem] = []

    for _, row in df.iterrows():
        url_val = row[cols["url"]]
        if not isinstance(url_val, str) or not url_val.strip():
            continue

        t: str = "account"
        if type_col:
            tv = row[type_col]
            if isinstance(tv, str) and tv.strip().lower() in ("account", "video"):
                t = tv.strip().lower()

        items.append(ManualImportItem(type=t, url=url_val.strip()))

    return items


@api_router.post(
    "/imports/manual",
    response_model=ManualImportOut,
    responses={400: {"model": ApiError}, 404: {"model": ApiError}},
)
async def create_manual_import(payload: ManualImportCreate) -> ManualImportOut:
    try:
        pid = ObjectId(payload.project_id)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid project_id")

    project = await db.projects.find_one({"_id": pid})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    items: list[ManualImportItem] = list(payload.items)
    if payload.csv_base64:
        items.extend(_parse_csv_items(payload.csv_base64))

    now = datetime.utcnow()
    doc = {
        "project_id": pid,
        "created_at": now,
        "status": "done",
        "items": [i.model_dump() for i in items],
    }
    res = await db.manual_imports.insert_one(doc)

    return ManualImportOut(
        id=oid_str(res.inserted_id),
        project_id=payload.project_id,
        status="done",
        total_items=len(items),
        created_at=now,
    )


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client() -> None:
    client.close()
