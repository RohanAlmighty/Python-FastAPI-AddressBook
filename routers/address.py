from math import radians, cos, sin, asin, sqrt
import geocoder
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
from fastapi import Depends, APIRouter, Request, Form
import sys

sys.path.append("..")

router = APIRouter(
    prefix="/address", tags=["address"], responses={404: {"description": "not found"}}
)

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/read-all-address")
async def read_all_addresses(db: Session = Depends(get_db)):
    addresses = db.query(models.Address).all()
    return addresses


@router.get("/read-address")
async def read_address(user_id: int, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.user_id == user_id).all()
    if len(address) == 0:
        return "Invalid user id"
    else:
        return address


@router.post("/add-address")
async def create_address(
    address_street: str,
    address_city: str,
    address_lat: float,
    address_lon: float,
    db: Session = Depends(get_db),
):
    address_model = models.Address()
    address_model.street = address_street
    address_model.city = address_city
    address_model.lat = address_lat
    address_model.lon = address_lon

    db.add(address_model)
    db.commit()

    return "Address added"


@router.put("/update-address")
async def update_address(
    user_id: int,
    address_street: str,
    address_city: str,
    address_lat: float,
    address_lon: float,
    db: Session = Depends(get_db),
):
    address_model = (
        db.query(models.Address).filter(models.Address.user_id == user_id).first()
    )
    address_model.street = address_street
    address_model.city = address_city
    address_model.lat = address_lat
    address_model.lon = address_lon

    db.add(address_model)
    db.commit()

    return "Address saved"


@router.delete("/delete-address")
async def delete_address(
    user_id: int,
    db: Session = Depends(get_db),
):
    db.query(models.Address).filter(models.Address.user_id == user_id).delete()

    db.commit()

    return f"Address of user {user_id} deleted"


@router.get("/addresses-within-radius")
async def get_addresses_within_radius(radius_in_km: int, db: Session = Depends(get_db)):

    g = geocoder.ip("me")
    user_location_lat = g.lat
    user_location_lon = g.lng

    addresses = db.query(models.Address).all()

    addresses_in_radius = []

    for address in addresses:

        dist = haversine(
            user_location_lon,
            user_location_lat,
            address.lon,
            address.lat,
        )

        if dist <= radius_in_km:
            addresses_in_radius.append(address)
    if len(addresses_in_radius) > 0:
        return addresses_in_radius
    else:
        return "No address found in radius"


def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km
