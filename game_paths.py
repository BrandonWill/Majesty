r"""
game_paths.py - Locate the Majesty HD game data files
=========================================================
This repo (Majesty_Mod) contains only our own tooling and mod source.
The actual game data (Data/, DataMX/, Music/, Quests/, QuestsMX/, SDK/)
lives in a SEPARATE location -- either the `Majesty_Files` repo
(https://github.com/BrandonWill/Majesty_Files) or a modder's own Steam
install -- since every modder already owns the game and doesn't need us
to distribute ~600MB of it alongside our tooling.

Configure the path via a `.env` file in this repo's root (see
.env.example):

    MAJESTY_GAME_PATH=C:\path\to\Majesty_Files

If unset, resolution falls back to (in order):
  1. MAJESTY_GAME_PATH from the environment / .env file
  2. ../Majesty_Files          (sibling folder -- our own dev layout:
                                 Majesty/Majesty_Mod + Majesty/Majesty_Files)
  3. The default Steam install path for Majesty HD
  4. A clear error telling you to set MAJESTY_GAME_PATH

Usage in scripts:
    from game_paths import resolve_game_path, game_dir

    # For a single file (works whether the path is a local override,
    # an explicit absolute path, or needs resolving against the game root):
    cam_path = resolve_game_path("Data/maindata.cam")

    # For a directory (existence-checked lazily by the caller, e.g. via
    # .exists() or .glob() -- matches existing test-skip patterns):
    quest_dir = game_dir("Quests")
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed -- MAJESTY_GAME_PATH can still be set as
    # a real environment variable, just no .env file support.
    pass

_THIS_DIR = Path(__file__).resolve().parent

_STEAM_DEFAULT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Majesty HD")


def _candidate_roots():
    env_path = os.environ.get("MAJESTY_GAME_PATH")
    if env_path:
        yield Path(env_path)
    yield _THIS_DIR.parent / "Majesty_Files"  # sibling folder convention
    yield _STEAM_DEFAULT


def _find_game_root():
    for candidate in _candidate_roots():
        if candidate.exists() and (candidate / "Data").exists():
            return candidate
    return None


GAME_ROOT = _find_game_root()


class GamePathError(FileNotFoundError):
    """Raised when a game data file/folder can't be located anywhere."""


def resolve_game_path(relative_or_absolute) -> Path:
    """Resolve a game-data path (e.g. "Data/maindata.cam") to a real Path.

    Resolution order:
      1. As given, if it's absolute or already exists relative to the
         current working directory (backward compatible with anyone who
         still has Data/ etc. physically present, or an explicit override).
      2. Relative to GAME_ROOT (the resolved Majesty_Files checkout or
         Steam install), if GAME_ROOT was found.

    Raises GamePathError with an actionable message if neither works.
    """
    p = Path(relative_or_absolute)
    if p.is_absolute() or p.exists():
        return p
    if GAME_ROOT is not None:
        candidate = GAME_ROOT / p
        if candidate.exists():
            return candidate
    raise GamePathError(
        f"Could not find game data path '{relative_or_absolute}'. "
        f"Set MAJESTY_GAME_PATH in a .env file (see .env.example), or place "
        f"a Majesty_Files checkout as a sibling of this repo."
    )


def game_dir(name: str) -> Path:
    """Return the path to a top-level game data directory (e.g. "Quests",
    "Data", "SDK"), for callers that check .exists()/.glob() themselves
    rather than needing a hard failure immediately.

    Falls back to a repo-relative path (matching the pre-split layout) if
    GAME_ROOT wasn't resolved, so existing `if not path.exists(): skip`
    patterns keep working with a sensible (if unresolved) path to check.
    """
    if GAME_ROOT is not None:
        return GAME_ROOT / name
    return _THIS_DIR / name
