import os
import pathlib

import litestar
from litestar import MediaType
from litestar import Response
from litestar.response import File
from litestar.router import Router
from litestar.static_files import create_static_files_router

BASE_PATH = str(pathlib.Path(__file__).parent.parent.resolve() / "assets")


def assets_router(base_path: str = BASE_PATH):
    @litestar.get(
        ["/", "/projects/{path:path}"],
        include_in_schema=False,
    )
    async def index() -> Response:
        return File(
            path=os.path.join(base_path, "index.html"),
            filename="index.html",
            media_type=MediaType.HTML,
            content_disposition_type="inline",
        )

    return Router(
        path="",
        route_handlers=[
            index,
            create_static_files_router("/", directories=[base_path]),
        ],
    )
