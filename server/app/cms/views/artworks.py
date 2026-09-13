from typing import Annotated, Any

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import SessionDep
from app.cms.deps import AdminUser
from app.cms.forms import ArtworkForm, FormError, error_messages, parse_image
from app.cms.templating import templates
from app.models import Artwork, User
from app.services.artist_service import ArtistService
from app.services.artwork_service import ArtworkService

router = APIRouter(prefix="/artworks")

PAGE_SIZE = 20


@router.get("", name="cms_artwork_list")
async def artwork_list(
    request: Request,
    user: AdminUser,
    session: SessionDep,
    page: Annotated[int, Query(ge=1)] = 1,
) -> Response:
    result = await ArtworkService(session).list_artworks(
        page=page, size=PAGE_SIZE, published_only=False
    )
    context = {"user": user, "active": "artworks", "result": result}
    # HTMX 요청(페이지 이동)이면 목록 조각만 반환
    template = "artworks/_rows.html" if request.headers.get("HX-Request") else "artworks/list.html"
    return templates.TemplateResponse(request, template, context)


@router.get("/new", name="cms_artwork_new")
async def artwork_new(request: Request, user: AdminUser, session: SessionDep) -> Response:
    return await _render_form(request, session, user, artwork=None, form_data={})


@router.post("/new")
async def artwork_create(request: Request, user: AdminUser, session: SessionDep) -> Response:
    form = await request.form()
    try:
        data = ArtworkForm.model_validate(dict(form))
        image = parse_image(form.get("image"))
    except (ValidationError, FormError) as exc:
        return await _render_form(
            request, session, user, artwork=None, form_data=dict(form), errors=error_messages(exc)
        )
    await ArtworkService(session).create_artwork(data.to_create(), image)
    return RedirectResponse(request.url_for("cms_artwork_list"), status_code=303)


@router.get("/{artwork_id}/edit", name="cms_artwork_edit")
async def artwork_edit(
    request: Request, artwork_id: int, user: AdminUser, session: SessionDep
) -> Response:
    artwork = await ArtworkService(session).get_artwork(artwork_id, published_only=False)
    form_data = ArtworkForm.model_validate(artwork, from_attributes=True).model_dump()
    return await _render_form(request, session, user, artwork=artwork, form_data=form_data)


@router.post("/{artwork_id}/edit")
async def artwork_update(
    request: Request, artwork_id: int, user: AdminUser, session: SessionDep
) -> Response:
    service = ArtworkService(session)
    form = await request.form()
    try:
        data = ArtworkForm.model_validate(dict(form))
        image = parse_image(form.get("image"))
    except (ValidationError, FormError) as exc:
        artwork = await service.get_artwork(artwork_id, published_only=False)
        return await _render_form(
            request,
            session,
            user,
            artwork=artwork,
            form_data=dict(form),
            errors=error_messages(exc),
        )
    await service.update_artwork(artwork_id, data.to_update(), image)
    return RedirectResponse(request.url_for("cms_artwork_list"), status_code=303)


@router.post("/{artwork_id}/delete", name="cms_artwork_delete")
async def artwork_delete(
    request: Request, artwork_id: int, user: AdminUser, session: SessionDep
) -> Response:
    await ArtworkService(session).delete_artwork(artwork_id)
    if request.headers.get("HX-Request"):
        return Response(status_code=200)  # HTMX가 해당 행을 빈 내용으로 교체
    return RedirectResponse(request.url_for("cms_artwork_list"), status_code=303)


async def _render_form(
    request: Request,
    session: AsyncSession,
    user: User,
    *,
    artwork: Artwork | None,
    form_data: dict[str, Any],
    errors: list[str] | None = None,
) -> Response:
    context = {
        "user": user,
        "active": "artworks",
        "artwork": artwork,
        "form": form_data,
        "errors": errors or [],
        "artists": await ArtistService(session).list_artists(),
    }
    return templates.TemplateResponse(
        request, "artworks/form.html", context, status_code=400 if errors else 200
    )
