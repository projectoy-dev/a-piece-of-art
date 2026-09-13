from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.utils.media import media_url

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
templates.env.globals["media_url"] = media_url
