"""Filesystem path configuration for the application.

This module defines the Pydantic model used to resolve standard directories
under the project root (static assets, bundled JS/CSS, images, fonts).
"""

__all__ = ("PathsInfo",)

from pathlib import Path

from pydantic import BaseModel, Field


class PathsInfo(BaseModel):
    """Resolved paths for application assets relative to the repository root.

    The default ``root`` is inferred from this file's location so static paths
    stay correct regardless of the current working directory.

    Attributes:
        root: Top-level project directory (parent chain from this module).

    """

    root: Path = Field(Path(__file__).resolve().parents[5], description="The root path of the application")

    @property
    def static(self) -> Path:
        """Return the static files root directory.

        Returns:
            Path: ``root / "static"``.

        """
        return self.root / "static"

    @property
    def src(self) -> Path:
        """Return the services directory.

        Returns:
            Path: ``root / "services"``.

        """
        return self.root / "src" / "expenses_counter"

    @property
    def assets(self) -> Path:
        """Return the directory for Vite-bundled JS and CSS assets.

        Returns:
            Path: ``static / "assets"``.

        """
        return self.static / "assets"

    @property
    def index_html(self) -> Path:
        """Return the index.html file.

        Returns:
            Path: ``static / "index.html"``.

        """
        return self.static / "index.html"

    @property
    def js(self) -> Path:
        """Return the directory for bundled JavaScript assets.

        Returns:
            Path: ``static / "js"``.

        """
        return self.static / "js"

    @property
    def css(self) -> Path:
        """Return the directory for stylesheet assets.

        Returns:
            Path: ``static / "css"``.

        """
        return self.static / "css"

    @property
    def images(self) -> Path:
        """Return the directory for image assets.

        Returns:
            Path: ``static / "images"``.

        """
        return self.static / "images"

    @property
    def fonts(self) -> Path:
        """Return the directory for font assets.

        Returns:
            Path: ``static / "fonts"``.

        """
        return self.static / "fonts"

    @property
    def alembic_ini(self) -> Path:
        """Return the alembic.ini file.

        Returns:
            Path: ``root / "services" / "alembic" / "alembic.ini"``.

        """
        return self.src / "services" / "alembic" / "alembic.ini"
