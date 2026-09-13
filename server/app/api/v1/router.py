from fastapi import APIRouter

from app.api.v1.endpoints import artists, artworks, auth, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(artists.router)
api_router.include_router(artworks.router)
