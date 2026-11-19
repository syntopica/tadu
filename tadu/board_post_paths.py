"""The routes a team board accepts POST on, besides tool calls."""

from __future__ import annotations

from tadu.board_data_path import BOARD_CHECK_PATH
from tadu.sign_in_settings import SIGN_OUT_PATH

POST_PATHS = frozenset({SIGN_OUT_PATH, BOARD_CHECK_PATH})
