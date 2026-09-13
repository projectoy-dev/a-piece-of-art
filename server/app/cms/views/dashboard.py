from fastapi import APIRouter, Request, Response

from app.api.deps import SessionDep
from app.cms.deps import AdminUser
from app.cms.templating import templates
from app.services.artist_service import ArtistService
from app.services.artwork_service import ArtworkService

router = APIRouter()


@router.get("/", name="cms_dashboard")
async def dashboard(request: Request, user: AdminUser, session: SessionDep) -> Response:
    context = {
        "user": user,
        "active": "dashboard",
        "artwork_count": await ArtworkService(session).count_artworks(),
        "artist_count": await ArtistService(session).count_artists(),
    }
    return templates.TemplateResponse(request, "dashboard.html", context)
