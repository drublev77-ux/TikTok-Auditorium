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
import httpx

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


# ─── Audience Avatar Models ───────────────────────────────────────────────────
class AudienceAvatarCreate(BaseModel):
    project_id: str
    name: str = Field(min_length=2, max_length=120)
    hashtags: list[str] = Field(min_length=1, description="At least one hashtag required")
    geolocation: str = Field(min_length=2, max_length=100, description="Country or region")
    language: str = Field(default="ru", max_length=10)
    notes: str | None = Field(default=None, max_length=2000)


class AudienceAvatarUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    hashtags: list[str] | None = None
    geolocation: str | None = Field(default=None, min_length=2, max_length=100)
    language: str | None = Field(default=None, max_length=10)
    notes: str | None = Field(default=None, max_length=2000)


class AudienceAvatarOut(BaseModel):
    id: str
    project_id: str
    name: str
    hashtags: list[str]
    geolocation: str
    language: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


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


# ─── Audience Avatar Endpoints ────────────────────────────────────────────────
@api_router.post(
    "/audience/avatars",
    response_model=AudienceAvatarOut,
    responses={400: {"model": ApiError}, 404: {"model": ApiError}},
)
async def create_audience_avatar(payload: AudienceAvatarCreate) -> AudienceAvatarOut:
    """Create a new audience avatar for a project."""
    try:
        pid = ObjectId(payload.project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    project = await db.projects.find_one({"_id": pid})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Normalize hashtags: strip whitespace and ensure # prefix
    normalized_hashtags = []
    for tag in payload.hashtags:
        tag = tag.strip()
        if tag:
            if not tag.startswith("#"):
                tag = f"#{tag}"
            normalized_hashtags.append(tag.lower())
    
    if not normalized_hashtags:
        raise HTTPException(status_code=400, detail="At least one valid hashtag is required")

    now = datetime.utcnow()
    doc = {
        "project_id": pid,
        "name": payload.name.strip(),
        "hashtags": normalized_hashtags,
        "geolocation": payload.geolocation.strip(),
        "language": payload.language.strip(),
        "notes": payload.notes.strip() if payload.notes else None,
        "created_at": now,
        "updated_at": now,
    }
    res = await db.audience_avatars.insert_one(doc)

    return AudienceAvatarOut(
        id=oid_str(res.inserted_id),
        project_id=payload.project_id,
        name=doc["name"],
        hashtags=doc["hashtags"],
        geolocation=doc["geolocation"],
        language=doc["language"],
        notes=doc["notes"],
        created_at=now,
        updated_at=now,
    )


@api_router.get("/audience/avatars", response_model=list[AudienceAvatarOut])
async def list_audience_avatars(project_id: str = Query(...)) -> list[AudienceAvatarOut]:
    """List all audience avatars for a project."""
    try:
        pid = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    docs = await db.audience_avatars.find({"project_id": pid}).sort("created_at", -1).to_list(100)
    return [
        AudienceAvatarOut(
            id=oid_str(d["_id"]),
            project_id=oid_str(d["project_id"]),
            name=d["name"],
            hashtags=d["hashtags"],
            geolocation=d["geolocation"],
            language=d.get("language", "ru"),
            notes=d.get("notes"),
            created_at=d["created_at"],
            updated_at=d.get("updated_at", d["created_at"]),
        )
        for d in docs
    ]


@api_router.get(
    "/audience/avatars/{avatar_id}",
    response_model=AudienceAvatarOut,
    responses={400: {"model": ApiError}, 404: {"model": ApiError}},
)
async def get_audience_avatar(avatar_id: str) -> AudienceAvatarOut:
    """Get a specific audience avatar by ID."""
    try:
        aid = ObjectId(avatar_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid avatar_id")

    d = await db.audience_avatars.find_one({"_id": aid})
    if not d:
        raise HTTPException(status_code=404, detail="Avatar not found")

    return AudienceAvatarOut(
        id=oid_str(d["_id"]),
        project_id=oid_str(d["project_id"]),
        name=d["name"],
        hashtags=d["hashtags"],
        geolocation=d["geolocation"],
        language=d.get("language", "ru"),
        notes=d.get("notes"),
        created_at=d["created_at"],
        updated_at=d.get("updated_at", d["created_at"]),
    )


@api_router.patch(
    "/audience/avatars/{avatar_id}",
    response_model=AudienceAvatarOut,
    responses={400: {"model": ApiError}, 404: {"model": ApiError}},
)
async def update_audience_avatar(avatar_id: str, payload: AudienceAvatarUpdate) -> AudienceAvatarOut:
    """Update an existing audience avatar."""
    try:
        aid = ObjectId(avatar_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid avatar_id")

    d = await db.audience_avatars.find_one({"_id": aid})
    if not d:
        raise HTTPException(status_code=404, detail="Avatar not found")

    update_data: dict[str, Any] = {"updated_at": datetime.utcnow()}
    
    if payload.name is not None:
        update_data["name"] = payload.name.strip()
    if payload.hashtags is not None:
        normalized = []
        for tag in payload.hashtags:
            tag = tag.strip()
            if tag:
                if not tag.startswith("#"):
                    tag = f"#{tag}"
                normalized.append(tag.lower())
        if not normalized:
            raise HTTPException(status_code=400, detail="At least one valid hashtag is required")
        update_data["hashtags"] = normalized
    if payload.geolocation is not None:
        update_data["geolocation"] = payload.geolocation.strip()
    if payload.language is not None:
        update_data["language"] = payload.language.strip()
    if payload.notes is not None:
        update_data["notes"] = payload.notes.strip() if payload.notes else None

    await db.audience_avatars.update_one({"_id": aid}, {"$set": update_data})
    
    # Fetch updated document
    d = await db.audience_avatars.find_one({"_id": aid})
    return AudienceAvatarOut(
        id=oid_str(d["_id"]),
        project_id=oid_str(d["project_id"]),
        name=d["name"],
        hashtags=d["hashtags"],
        geolocation=d["geolocation"],
        language=d.get("language", "ru"),
        notes=d.get("notes"),
        created_at=d["created_at"],
        updated_at=d.get("updated_at", d["created_at"]),
    )


@api_router.delete(
    "/audience/avatars/{avatar_id}",
    responses={400: {"model": ApiError}, 404: {"model": ApiError}},
)
async def delete_audience_avatar(avatar_id: str) -> dict[str, str]:
    """Delete an audience avatar."""
    try:
        aid = ObjectId(avatar_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid avatar_id")

    result = await db.audience_avatars.delete_one({"_id": aid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Avatar not found")

    return {"status": "deleted", "id": avatar_id}


# ─── Subscription & Payment Models ────────────────────────────────────────────
SUBSCRIPTION_PLANS = {
    "basic": {
        "id": "basic",
        "name": "Basic",
        "price_usd": 50,
        "features": [
            "1 project",
            "5 audience avatars",
            "10 competitor analyses",
            "Basic analytics",
        ],
    },
    "pro": {
        "id": "pro",
        "name": "Pro",
        "price_usd": 100,
        "features": [
            "5 projects",
            "Unlimited avatars",
            "50 competitor analyses",
            "Advanced analytics",
            "Blogger discovery",
            "Content planner",
        ],
    },
    "agency": {
        "id": "agency",
        "name": "Agency",
        "price_usd": 250,
        "features": [
            "Unlimited projects",
            "Unlimited avatars",
            "Unlimited analyses",
            "White-label reports",
            "API access",
            "Priority support",
            "Team collaboration",
        ],
    },
}

PAYMENT_CONFIG = {
    "crypto": {
        "wallet_address": "0xcecd3bcf98d5642722258c346c5dc1cdb83c8986",
        "supported_tokens": ["USDT", "USDC", "ETH", "BTC"],
        "networks": [
            {"id": "erc20", "name": "Ethereum (ERC-20)", "chain_id": 1},
            {"id": "bep20", "name": "BSC (BEP-20)", "chain_id": 56},
            {"id": "trc20", "name": "Tron (TRC-20)", "chain_id": None},
            {"id": "polygon", "name": "Polygon", "chain_id": 137},
        ],
    },
    "bank": {
        "account_number": "BY43POIS30140008401005002629",
        "bic": "POISBY2X",
        "currency": "USD",
        "bank_name": "Bank (BIC: POISBY2X)",
    },
    "paypal": {
        "account": "TPFTECHNOLOGY",
        "email": "TPFTECHNOLOGY",
    },
}


class SubscriptionPlanOut(BaseModel):
    id: str
    name: str
    price_usd: int
    features: list[str]


class PaymentMethodOut(BaseModel):
    method: Literal["crypto", "bank", "paypal"]
    details: dict[str, Any]


class PaymentRequestCreate(BaseModel):
    org_id: str
    plan_id: Literal["basic", "pro", "agency"]
    payment_method: Literal["crypto", "bank", "paypal"]
    crypto_network: str | None = None
    crypto_token: str | None = None


class PaymentRequestOut(BaseModel):
    id: str
    org_id: str
    plan_id: str
    plan_name: str
    amount_usd: int
    payment_method: str
    status: Literal["pending", "confirmed", "expired", "cancelled"]
    payment_details: dict[str, Any]
    created_at: datetime
    expires_at: datetime


class SubscriptionOut(BaseModel):
    id: str
    org_id: str
    plan_id: str
    plan_name: str
    status: Literal["active", "expired", "cancelled"]
    started_at: datetime
    expires_at: datetime


# ─── Subscription & Payment Endpoints ─────────────────────────────────────────
@api_router.get("/billing/plans", response_model=list[SubscriptionPlanOut])
async def list_subscription_plans() -> list[SubscriptionPlanOut]:
    """Get all available subscription plans."""
    return [SubscriptionPlanOut(**plan) for plan in SUBSCRIPTION_PLANS.values()]


@api_router.get("/billing/plans/{plan_id}", response_model=SubscriptionPlanOut)
async def get_subscription_plan(plan_id: str) -> SubscriptionPlanOut:
    """Get a specific subscription plan."""
    if plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=404, detail="Plan not found")
    return SubscriptionPlanOut(**SUBSCRIPTION_PLANS[plan_id])


@api_router.get("/billing/payment-methods")
async def list_payment_methods() -> dict[str, Any]:
    """Get available payment methods and their details."""
    return {
        "methods": ["crypto", "bank", "paypal"],
        "crypto": {
            "wallet_address": PAYMENT_CONFIG["crypto"]["wallet_address"],
            "supported_tokens": PAYMENT_CONFIG["crypto"]["supported_tokens"],
            "networks": PAYMENT_CONFIG["crypto"]["networks"],
        },
        "bank": PAYMENT_CONFIG["bank"],
        "paypal": PAYMENT_CONFIG["paypal"],
    }


@api_router.post("/billing/payment-requests", response_model=PaymentRequestOut)
async def create_payment_request(payload: PaymentRequestCreate) -> PaymentRequestOut:
    """Create a new payment request for a subscription."""
    # Validate org
    try:
        org_oid = ObjectId(payload.org_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid org_id")

    org = await db.orgs.find_one({"_id": org_oid})
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")

    # Get plan
    if payload.plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan_id")
    
    plan = SUBSCRIPTION_PLANS[payload.plan_id]
    
    # Build payment details based on method
    payment_details: dict[str, Any] = {}
    
    if payload.payment_method == "crypto":
        if not payload.crypto_network or not payload.crypto_token:
            raise HTTPException(
                status_code=400, 
                detail="crypto_network and crypto_token required for crypto payments"
            )
        payment_details = {
            "wallet_address": PAYMENT_CONFIG["crypto"]["wallet_address"],
            "network": payload.crypto_network,
            "token": payload.crypto_token,
            "amount_crypto": f"{plan['price_usd']} USD equivalent in {payload.crypto_token}",
        }
    elif payload.payment_method == "bank":
        payment_details = {
            **PAYMENT_CONFIG["bank"],
            "reference": f"TIKAUD-{org_oid}-{payload.plan_id.upper()}",
        }
    elif payload.payment_method == "paypal":
        payment_details = {
            **PAYMENT_CONFIG["paypal"],
            "reference": f"TIKAUD-{org_oid}-{payload.plan_id.upper()}",
        }

    now = datetime.utcnow()
    from datetime import timedelta
    expires_at = now + timedelta(hours=24)  # 24 hour expiry for payment

    doc = {
        "org_id": org_oid,
        "plan_id": payload.plan_id,
        "plan_name": plan["name"],
        "amount_usd": plan["price_usd"],
        "payment_method": payload.payment_method,
        "payment_details": payment_details,
        "status": "pending",
        "created_at": now,
        "expires_at": expires_at,
    }
    
    res = await db.payment_requests.insert_one(doc)
    
    return PaymentRequestOut(
        id=oid_str(res.inserted_id),
        org_id=payload.org_id,
        plan_id=payload.plan_id,
        plan_name=plan["name"],
        amount_usd=plan["price_usd"],
        payment_method=payload.payment_method,
        status="pending",
        payment_details=payment_details,
        created_at=now,
        expires_at=expires_at,
    )


@api_router.get("/billing/payment-requests", response_model=list[PaymentRequestOut])
async def list_payment_requests(org_id: str = Query(...)) -> list[PaymentRequestOut]:
    """List payment requests for an organization."""
    try:
        org_oid = ObjectId(org_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid org_id")

    docs = await db.payment_requests.find({"org_id": org_oid}).sort("created_at", -1).to_list(100)
    
    return [
        PaymentRequestOut(
            id=oid_str(d["_id"]),
            org_id=oid_str(d["org_id"]),
            plan_id=d["plan_id"],
            plan_name=d["plan_name"],
            amount_usd=d["amount_usd"],
            payment_method=d["payment_method"],
            status=d["status"],
            payment_details=d["payment_details"],
            created_at=d["created_at"],
            expires_at=d["expires_at"],
        )
        for d in docs
    ]


@api_router.get("/billing/payment-requests/{request_id}", response_model=PaymentRequestOut)
async def get_payment_request(request_id: str) -> PaymentRequestOut:
    """Get a specific payment request."""
    try:
        rid = ObjectId(request_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request_id")

    d = await db.payment_requests.find_one({"_id": rid})
    if not d:
        raise HTTPException(status_code=404, detail="Payment request not found")

    return PaymentRequestOut(
        id=oid_str(d["_id"]),
        org_id=oid_str(d["org_id"]),
        plan_id=d["plan_id"],
        plan_name=d["plan_name"],
        amount_usd=d["amount_usd"],
        payment_method=d["payment_method"],
        status=d["status"],
        payment_details=d["payment_details"],
        created_at=d["created_at"],
        expires_at=d["expires_at"],
    )


@api_router.patch("/billing/payment-requests/{request_id}/confirm")
async def confirm_payment_request(request_id: str) -> PaymentRequestOut:
    """Admin endpoint to confirm a payment and activate subscription."""
    try:
        rid = ObjectId(request_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request_id")

    d = await db.payment_requests.find_one({"_id": rid})
    if not d:
        raise HTTPException(status_code=404, detail="Payment request not found")

    if d["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot confirm payment with status: {d['status']}")

    now = datetime.utcnow()
    from datetime import timedelta
    subscription_expires = now + timedelta(days=30)

    # Update payment request status
    await db.payment_requests.update_one(
        {"_id": rid},
        {"$set": {"status": "confirmed"}}
    )

    # Create or update subscription
    existing_sub = await db.subscriptions.find_one({"org_id": d["org_id"]})
    
    if existing_sub:
        await db.subscriptions.update_one(
            {"_id": existing_sub["_id"]},
            {"$set": {
                "plan_id": d["plan_id"],
                "plan_name": d["plan_name"],
                "status": "active",
                "started_at": now,
                "expires_at": subscription_expires,
            }}
        )
    else:
        await db.subscriptions.insert_one({
            "org_id": d["org_id"],
            "plan_id": d["plan_id"],
            "plan_name": d["plan_name"],
            "status": "active",
            "started_at": now,
            "expires_at": subscription_expires,
        })

    d["status"] = "confirmed"
    return PaymentRequestOut(
        id=oid_str(d["_id"]),
        org_id=oid_str(d["org_id"]),
        plan_id=d["plan_id"],
        plan_name=d["plan_name"],
        amount_usd=d["amount_usd"],
        payment_method=d["payment_method"],
        status="confirmed",
        payment_details=d["payment_details"],
        created_at=d["created_at"],
        expires_at=d["expires_at"],
    )


@api_router.get("/billing/subscription")
async def get_subscription(org_id: str = Query(...)) -> SubscriptionOut | dict[str, None]:
    """Get current subscription for an organization."""
    try:
        org_oid = ObjectId(org_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid org_id")

    d = await db.subscriptions.find_one({"org_id": org_oid})
    if not d:
        return {"subscription": None}

    return SubscriptionOut(
        id=oid_str(d["_id"]),
        org_id=oid_str(d["org_id"]),
        plan_id=d["plan_id"],
        plan_name=d["plan_name"],
        status=d["status"],
        started_at=d["started_at"],
        expires_at=d["expires_at"],
    )


# ─── Module B: Competitor Models ──────────────────────────────────────────────
class CompetitorCreate(BaseModel):
    project_id: str
    name: str = Field(min_length=2, max_length=120)
    tiktok_url: str = Field(min_length=5, max_length=300)
    notes: str | None = None


class CompetitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    tiktok_url: str | None = Field(default=None, min_length=5, max_length=300)
    notes: str | None = None


class CompetitorOut(BaseModel):
    id: str
    project_id: str
    name: str
    tiktok_url: str
    notes: str | None
    # Placeholder metrics (will be populated when TikTok API is connected)
    followers: int | None = None
    avg_views: int | None = None
    avg_likes: int | None = None
    engagement_rate: float | None = None
    created_at: datetime
    updated_at: datetime


# ─── Module C: Creator/Blogger Models ─────────────────────────────────────────
class CreatorCreate(BaseModel):
    project_id: str
    name: str = Field(min_length=2, max_length=120)
    tiktok_url: str = Field(min_length=5, max_length=300)
    category: str = Field(default="general", max_length=50)
    notes: str | None = None


class CreatorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    tiktok_url: str | None = Field(default=None, min_length=5, max_length=300)
    category: str | None = Field(default=None, max_length=50)
    notes: str | None = None


class CreatorOut(BaseModel):
    id: str
    project_id: str
    name: str
    tiktok_url: str
    category: str
    notes: str | None
    # Placeholder metrics
    followers: int | None = None
    avg_views: int | None = None
    engagement_rate: float | None = None
    audience_match_score: float | None = None  # 0-100 score matching target audience
    created_at: datetime
    updated_at: datetime


# ─── Module B: Competitor Endpoints ───────────────────────────────────────────
@api_router.post("/competitors", response_model=CompetitorOut)
async def create_competitor(payload: CompetitorCreate) -> CompetitorOut:
    """Add a competitor to track."""
    try:
        pid = ObjectId(payload.project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    project = await db.projects.find_one({"_id": pid})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    now = datetime.utcnow()
    doc = {
        "project_id": pid,
        "name": payload.name.strip(),
        "tiktok_url": payload.tiktok_url.strip(),
        "notes": payload.notes.strip() if payload.notes else None,
        "followers": None,
        "avg_views": None,
        "avg_likes": None,
        "engagement_rate": None,
        "created_at": now,
        "updated_at": now,
    }
    res = await db.competitors.insert_one(doc)

    return CompetitorOut(
        id=oid_str(res.inserted_id),
        project_id=payload.project_id,
        **{k: v for k, v in doc.items() if k not in ("_id", "project_id")},
    )


@api_router.get("/competitors", response_model=list[CompetitorOut])
async def list_competitors(project_id: str = Query(...)) -> list[CompetitorOut]:
    """List all competitors for a project."""
    try:
        pid = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    docs = await db.competitors.find({"project_id": pid}).sort("created_at", -1).to_list(100)
    return [
        CompetitorOut(
            id=oid_str(d["_id"]),
            project_id=oid_str(d["project_id"]),
            name=d["name"],
            tiktok_url=d["tiktok_url"],
            notes=d.get("notes"),
            followers=d.get("followers"),
            avg_views=d.get("avg_views"),
            avg_likes=d.get("avg_likes"),
            engagement_rate=d.get("engagement_rate"),
            created_at=d["created_at"],
            updated_at=d.get("updated_at", d["created_at"]),
        )
        for d in docs
    ]


@api_router.get("/competitors/{competitor_id}", response_model=CompetitorOut)
async def get_competitor(competitor_id: str) -> CompetitorOut:
    """Get a specific competitor."""
    try:
        cid = ObjectId(competitor_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid competitor_id")

    d = await db.competitors.find_one({"_id": cid})
    if not d:
        raise HTTPException(status_code=404, detail="Competitor not found")

    return CompetitorOut(
        id=oid_str(d["_id"]),
        project_id=oid_str(d["project_id"]),
        name=d["name"],
        tiktok_url=d["tiktok_url"],
        notes=d.get("notes"),
        followers=d.get("followers"),
        avg_views=d.get("avg_views"),
        avg_likes=d.get("avg_likes"),
        engagement_rate=d.get("engagement_rate"),
        created_at=d["created_at"],
        updated_at=d.get("updated_at", d["created_at"]),
    )


@api_router.patch("/competitors/{competitor_id}", response_model=CompetitorOut)
async def update_competitor(competitor_id: str, payload: CompetitorUpdate) -> CompetitorOut:
    """Update a competitor."""
    try:
        cid = ObjectId(competitor_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid competitor_id")

    d = await db.competitors.find_one({"_id": cid})
    if not d:
        raise HTTPException(status_code=404, detail="Competitor not found")

    update_data: dict[str, Any] = {"updated_at": datetime.utcnow()}
    if payload.name is not None:
        update_data["name"] = payload.name.strip()
    if payload.tiktok_url is not None:
        update_data["tiktok_url"] = payload.tiktok_url.strip()
    if payload.notes is not None:
        update_data["notes"] = payload.notes.strip() if payload.notes else None

    await db.competitors.update_one({"_id": cid}, {"$set": update_data})
    d = await db.competitors.find_one({"_id": cid})

    return CompetitorOut(
        id=oid_str(d["_id"]),
        project_id=oid_str(d["project_id"]),
        name=d["name"],
        tiktok_url=d["tiktok_url"],
        notes=d.get("notes"),
        followers=d.get("followers"),
        avg_views=d.get("avg_views"),
        avg_likes=d.get("avg_likes"),
        engagement_rate=d.get("engagement_rate"),
        created_at=d["created_at"],
        updated_at=d.get("updated_at", d["created_at"]),
    )


@api_router.delete("/competitors/{competitor_id}")
async def delete_competitor(competitor_id: str) -> dict[str, str]:
    """Delete a competitor."""
    try:
        cid = ObjectId(competitor_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid competitor_id")

    result = await db.competitors.delete_one({"_id": cid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Competitor not found")

    return {"status": "deleted", "id": competitor_id}


# ─── Module C: Creator/Blogger Endpoints ──────────────────────────────────────
@api_router.post("/creators", response_model=CreatorOut)
async def create_creator(payload: CreatorCreate) -> CreatorOut:
    """Add a creator/blogger to track."""
    try:
        pid = ObjectId(payload.project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    project = await db.projects.find_one({"_id": pid})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    now = datetime.utcnow()
    doc = {
        "project_id": pid,
        "name": payload.name.strip(),
        "tiktok_url": payload.tiktok_url.strip(),
        "category": payload.category.strip(),
        "notes": payload.notes.strip() if payload.notes else None,
        "followers": None,
        "avg_views": None,
        "engagement_rate": None,
        "audience_match_score": None,
        "created_at": now,
        "updated_at": now,
    }
    res = await db.creators.insert_one(doc)

    return CreatorOut(
        id=oid_str(res.inserted_id),
        project_id=payload.project_id,
        **{k: v for k, v in doc.items() if k not in ("_id", "project_id")},
    )


@api_router.get("/creators", response_model=list[CreatorOut])
async def list_creators(
    project_id: str = Query(...),
    category: str | None = Query(default=None),
) -> list[CreatorOut]:
    """List all creators for a project, optionally filtered by category."""
    try:
        pid = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    query: dict[str, Any] = {"project_id": pid}
    if category:
        query["category"] = category

    docs = await db.creators.find(query).sort("created_at", -1).to_list(100)
    return [
        CreatorOut(
            id=oid_str(d["_id"]),
            project_id=oid_str(d["project_id"]),
            name=d["name"],
            tiktok_url=d["tiktok_url"],
            category=d.get("category", "general"),
            notes=d.get("notes"),
            followers=d.get("followers"),
            avg_views=d.get("avg_views"),
            engagement_rate=d.get("engagement_rate"),
            audience_match_score=d.get("audience_match_score"),
            created_at=d["created_at"],
            updated_at=d.get("updated_at", d["created_at"]),
        )
        for d in docs
    ]


@api_router.get("/creators/{creator_id}", response_model=CreatorOut)
async def get_creator(creator_id: str) -> CreatorOut:
    """Get a specific creator."""
    try:
        cid = ObjectId(creator_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid creator_id")

    d = await db.creators.find_one({"_id": cid})
    if not d:
        raise HTTPException(status_code=404, detail="Creator not found")

    return CreatorOut(
        id=oid_str(d["_id"]),
        project_id=oid_str(d["project_id"]),
        name=d["name"],
        tiktok_url=d["tiktok_url"],
        category=d.get("category", "general"),
        notes=d.get("notes"),
        followers=d.get("followers"),
        avg_views=d.get("avg_views"),
        engagement_rate=d.get("engagement_rate"),
        audience_match_score=d.get("audience_match_score"),
        created_at=d["created_at"],
        updated_at=d.get("updated_at", d["created_at"]),
    )


@api_router.patch("/creators/{creator_id}", response_model=CreatorOut)
async def update_creator(creator_id: str, payload: CreatorUpdate) -> CreatorOut:
    """Update a creator."""
    try:
        cid = ObjectId(creator_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid creator_id")

    d = await db.creators.find_one({"_id": cid})
    if not d:
        raise HTTPException(status_code=404, detail="Creator not found")

    update_data: dict[str, Any] = {"updated_at": datetime.utcnow()}
    if payload.name is not None:
        update_data["name"] = payload.name.strip()
    if payload.tiktok_url is not None:
        update_data["tiktok_url"] = payload.tiktok_url.strip()
    if payload.category is not None:
        update_data["category"] = payload.category.strip()
    if payload.notes is not None:
        update_data["notes"] = payload.notes.strip() if payload.notes else None

    await db.creators.update_one({"_id": cid}, {"$set": update_data})
    d = await db.creators.find_one({"_id": cid})

    return CreatorOut(
        id=oid_str(d["_id"]),
        project_id=oid_str(d["project_id"]),
        name=d["name"],
        tiktok_url=d["tiktok_url"],
        category=d.get("category", "general"),
        notes=d.get("notes"),
        followers=d.get("followers"),
        avg_views=d.get("avg_views"),
        engagement_rate=d.get("engagement_rate"),
        audience_match_score=d.get("audience_match_score"),
        created_at=d["created_at"],
        updated_at=d.get("updated_at", d["created_at"]),
    )


@api_router.delete("/creators/{creator_id}")
async def delete_creator(creator_id: str) -> dict[str, str]:
    """Delete a creator."""
    try:
        cid = ObjectId(creator_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid creator_id")

    result = await db.creators.delete_one({"_id": cid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Creator not found")

    return {"status": "deleted", "id": creator_id}


@api_router.get("/creators/categories/list")
async def list_creator_categories(project_id: str = Query(...)) -> list[str]:
    """Get unique categories for creators in a project."""
    try:
        pid = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    categories = await db.creators.distinct("category", {"project_id": pid})
    return sorted(categories) if categories else ["general"]


# ─── Module D: Content Planner Models ─────────────────────────────────────────
EMERGENT_LLM_KEY = "sk-emergent-e64Cf8103B8098f024"

class ContentIdeaRequest(BaseModel):
    project_id: str
    topic: str = Field(min_length=2, max_length=200)
    target_audience: str | None = None
    hashtags: list[str] | None = None
    content_type: Literal["video", "trend", "educational", "promotional"] = "video"
    count: int = Field(default=5, ge=1, le=10)


class ContentIdea(BaseModel):
    title: str
    description: str
    hook: str  # First 3 seconds hook
    hashtags: list[str]
    best_posting_time: str
    estimated_duration: str
    content_tips: list[str]


class ContentPlanCreate(BaseModel):
    project_id: str
    title: str = Field(min_length=2, max_length=200)
    scheduled_date: str  # ISO date string
    scheduled_time: str  # HH:MM format
    content_type: str = "video"
    description: str | None = None
    hashtags: list[str] | None = None
    status: Literal["draft", "scheduled", "published", "archived"] = "draft"
    has_ad_label: bool = False  # Mandatory ad labeling check


class ContentPlanUpdate(BaseModel):
    title: str | None = None
    scheduled_date: str | None = None
    scheduled_time: str | None = None
    content_type: str | None = None
    description: str | None = None
    hashtags: list[str] | None = None
    status: Literal["draft", "scheduled", "published", "archived"] | None = None
    has_ad_label: bool | None = None


class ContentPlanOut(BaseModel):
    id: str
    project_id: str
    title: str
    scheduled_date: str
    scheduled_time: str
    content_type: str
    description: str | None
    hashtags: list[str]
    status: str
    has_ad_label: bool
    created_at: datetime
    updated_at: datetime


# ─── Module D: Content Planner AI Endpoints ───────────────────────────────────
@api_router.post("/planner/generate-ideas")
async def generate_content_ideas(payload: ContentIdeaRequest) -> dict[str, Any]:
    """Generate AI-powered content ideas using OpenAI."""
    try:
        pid = ObjectId(payload.project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    project = await db.projects.find_one({"_id": pid})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Build prompt for AI
    audience_context = f"Target audience: {payload.target_audience}" if payload.target_audience else ""
    hashtag_context = f"Related hashtags: {', '.join(payload.hashtags)}" if payload.hashtags else ""
    
    prompt = f"""You are a TikTok content strategist. Generate {payload.count} creative content ideas for the following:

Topic: {payload.topic}
Content Type: {payload.content_type}
{audience_context}
{hashtag_context}

For each idea, provide:
1. Title (catchy, max 60 chars)
2. Description (detailed concept, 2-3 sentences)
3. Hook (first 3 seconds to grab attention)
4. Hashtags (5-7 relevant trending hashtags)
5. Best posting time (e.g., "18:00-20:00 weekdays")
6. Estimated duration (e.g., "15-30 seconds")
7. Content tips (3 actionable tips)

Respond in JSON format with array "ideas" containing objects with fields: title, description, hook, hashtags (array), best_posting_time, estimated_duration, content_tips (array).
Make ideas viral-worthy and engaging for TikTok audience. Use Russian language for content."""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {EMERGENT_LLM_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are an expert TikTok content strategist who creates viral content ideas. Always respond in valid JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8,
                    "response_format": {"type": "json_object"}
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"AI service error: {response.text}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            import json
            ideas_data = json.loads(content)
            
            return {
                "topic": payload.topic,
                "content_type": payload.content_type,
                "ideas": ideas_data.get("ideas", []),
                "generated_at": datetime.utcnow().isoformat()
            }
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI request timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@api_router.post("/planner/optimize-hashtags")
async def optimize_hashtags(hashtags: list[str] = [], topic: str = "") -> dict[str, Any]:
    """AI-powered hashtag optimization."""
    if not hashtags and not topic:
        raise HTTPException(status_code=400, detail="Provide hashtags or topic")

    prompt = f"""Analyze and optimize these TikTok hashtags for maximum reach:
Input hashtags: {', '.join(hashtags) if hashtags else 'None'}
Topic: {topic if topic else 'General'}

Provide:
1. optimized_hashtags: 10 optimized hashtags (mix of trending, niche, and branded)
2. removed_hashtags: any hashtags to remove (banned, overused, irrelevant)
3. hashtag_strategy: brief strategy explanation

Respond in JSON format with fields: optimized_hashtags (array), removed_hashtags (array), hashtag_strategy (string).
Use a mix of English and Russian hashtags for TikTok."""

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {EMERGENT_LLM_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a TikTok hashtag expert. Respond in JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.6,
                    "response_format": {"type": "json_object"}
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="AI service error")
            
            result = response.json()
            import json
            return json.loads(result["choices"][0]["message"]["content"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


# ─── Module D: Content Plan CRUD ──────────────────────────────────────────────
@api_router.post("/planner/posts", response_model=ContentPlanOut)
async def create_content_plan(payload: ContentPlanCreate) -> ContentPlanOut:
    """Create a scheduled content post."""
    try:
        pid = ObjectId(payload.project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    project = await db.projects.find_one({"_id": pid})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    now = datetime.utcnow()
    doc = {
        "project_id": pid,
        "title": payload.title.strip(),
        "scheduled_date": payload.scheduled_date,
        "scheduled_time": payload.scheduled_time,
        "content_type": payload.content_type,
        "description": payload.description.strip() if payload.description else None,
        "hashtags": payload.hashtags or [],
        "status": payload.status,
        "has_ad_label": payload.has_ad_label,
        "created_at": now,
        "updated_at": now,
    }
    
    res = await db.content_plans.insert_one(doc)
    
    return ContentPlanOut(
        id=oid_str(res.inserted_id),
        project_id=payload.project_id,
        **{k: v for k, v in doc.items() if k not in ("_id", "project_id")},
    )


@api_router.get("/planner/posts", response_model=list[ContentPlanOut])
async def list_content_plans(
    project_id: str = Query(...),
    status: str | None = Query(default=None),
) -> list[ContentPlanOut]:
    """List content plans for a project."""
    try:
        pid = ObjectId(project_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    query: dict[str, Any] = {"project_id": pid}
    if status:
        query["status"] = status

    docs = await db.content_plans.find(query).sort("scheduled_date", 1).to_list(100)
    
    return [
        ContentPlanOut(
            id=oid_str(d["_id"]),
            project_id=oid_str(d["project_id"]),
            title=d["title"],
            scheduled_date=d["scheduled_date"],
            scheduled_time=d["scheduled_time"],
            content_type=d.get("content_type", "video"),
            description=d.get("description"),
            hashtags=d.get("hashtags", []),
            status=d.get("status", "draft"),
            has_ad_label=d.get("has_ad_label", False),
            created_at=d["created_at"],
            updated_at=d.get("updated_at", d["created_at"]),
        )
        for d in docs
    ]


@api_router.patch("/planner/posts/{post_id}", response_model=ContentPlanOut)
async def update_content_plan(post_id: str, payload: ContentPlanUpdate) -> ContentPlanOut:
    """Update a content plan."""
    try:
        pid = ObjectId(post_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid post_id")

    d = await db.content_plans.find_one({"_id": pid})
    if not d:
        raise HTTPException(status_code=404, detail="Content plan not found")

    update_data: dict[str, Any] = {"updated_at": datetime.utcnow()}
    
    if payload.title is not None:
        update_data["title"] = payload.title.strip()
    if payload.scheduled_date is not None:
        update_data["scheduled_date"] = payload.scheduled_date
    if payload.scheduled_time is not None:
        update_data["scheduled_time"] = payload.scheduled_time
    if payload.content_type is not None:
        update_data["content_type"] = payload.content_type
    if payload.description is not None:
        update_data["description"] = payload.description.strip() if payload.description else None
    if payload.hashtags is not None:
        update_data["hashtags"] = payload.hashtags
    if payload.status is not None:
        update_data["status"] = payload.status
    if payload.has_ad_label is not None:
        update_data["has_ad_label"] = payload.has_ad_label

    await db.content_plans.update_one({"_id": pid}, {"$set": update_data})
    d = await db.content_plans.find_one({"_id": pid})

    return ContentPlanOut(
        id=oid_str(d["_id"]),
        project_id=oid_str(d["project_id"]),
        title=d["title"],
        scheduled_date=d["scheduled_date"],
        scheduled_time=d["scheduled_time"],
        content_type=d.get("content_type", "video"),
        description=d.get("description"),
        hashtags=d.get("hashtags", []),
        status=d.get("status", "draft"),
        has_ad_label=d.get("has_ad_label", False),
        created_at=d["created_at"],
        updated_at=d.get("updated_at", d["created_at"]),
    )


@api_router.delete("/planner/posts/{post_id}")
async def delete_content_plan(post_id: str) -> dict[str, str]:
    """Delete a content plan."""
    try:
        pid = ObjectId(post_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid post_id")

    result = await db.content_plans.delete_one({"_id": pid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Content plan not found")

    return {"status": "deleted", "id": post_id}


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
