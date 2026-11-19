"""Find the user's config file."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from platformdirs import user_config_dir

from tadu.config_settings import CONFIG_FILE_NAME, CONFIG_VARIABLE

if TYPE_CHECKING:
    from collections.abc import Mapping


def user_config_file(explicit: str | None, environ: Mapping[str, str]) -> Path | None:
    """`--config FILE`, else $TADU_CONFIG, else config.toml in the user config directory.

    The first two must exist; the default place is read only when it holds the file.
    platformdirs knows each system's directory: $XDG_CONFIG_HOME/tadu or ~/.config/tadu
    on Linux, ~/Library/Application Support/tadu on macOS, %LOCALAPPDATA%/tadu on Windows.
    """
    named = explicit or environ.get(CONFIG_VARIABLE, "")
    if named:
        return Path(named).expanduser()
    default = Path(user_config_dir("tadu", appauthor=False)) / CONFIG_FILE_NAME
    return default if default.is_file() else None
