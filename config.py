"""
Settings for The Unofficial Guide.

Everything you're likely to change lives here, at the top, on purpose.
You'll edit THRESHOLD in Milestone 4 and the chunking numbers in Milestone 3.

Anything you set in your .env file wins over the defaults here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")


# ─── The corpus you're working with ──────────────────────────────────────────
# Change this to switch corpora, or pass --corpus on the command line.
# Options are the folder names inside corpora/. See corpora/README.md.

CORPUS = os.getenv("AI201_CORPUS", "campus_life")


# ─── Chunking (Milestone 3) ──────────────────────────────────────────────────
# These are deliberately plain, generic numbers. Milestone 3 is where you
# replace them with numbers that fit the documents you actually read.

CHUNK_SIZE = 800        # characters per chunk
CHUNK_OVERLAP = 120     # characters shared between neighbouring chunks

# *******Deb***

# =====================================================================
# Chunker configuration
# =====================================================================

# ---- Chunker switch --------------------------------------------------
# "original"   -> chunker.py::fallback_split
#                 (starter's fixed-size character windows, ignores corpus)
# "experiment" -> chunker.py::split_documents
#                 (structure-aware, per-corpus strategy and sizing)
# Milestone 3 asks you to compare the two. Flip this to A/B without
# editing any code, then re-run `python app.py --corpus X index` and
# `python app.py --corpus X chunks -n 10`.
# CHUNKER_MODE = "original"     # "original" | "experiment"
#CHUNKER_MODE = "experiment"   # "original" | "experiment"


# ---- Global chunk-size defaults --------------------------------------
# Used by:
#   - "original" mode (fallback_split reads these directly), and
#   - "experiment" mode as the FALLBACK when a corpus has no per-corpus
#     override in CORPUS_SETTINGS below.
#

# ---- Experiment-mode routing (ignored in "original" mode) ------------
# Which chunking strategy to use for each corpus. The name on the right
# must match a strategy registered in chunker.py's _STRATEGIES dict.
CORPUS_STRATEGIES = {
    "campus_life":    "prose_with_headings",
    "advice_threads": "threaded",
    "city_guides":    "sectioned",       # <- only this one runs the sectioned strategy soas city info gets added to the chunk
    "practice":       "prose_with_headings",
}

# Fallback strategy for a corpus name not listed in CORPUS_STRATEGIES
# (e.g. a corpus you bring your own under corpora/your_name/).
DEFAULT_STRATEGY = "prose_with_headings"


# ---- Experiment-mode per-corpus size overrides -----------------------
# Any key omitted for a corpus falls back to the global CHUNK_SIZE /
# CHUNK_OVERLAP above. Leave this dict empty ({}) to use the globals
# for every corpus.
#
# Reasoning per corpus:
#   campus_life    - README says ~317 chars/doc. A 900 cap is wasteful;
#                    500 is enough for the occasional longer doc and
#                    keeps short-doc chunks tight.
#   advice_threads - Very uneven reply length; keep 900 so a long reply
#                    plus its topic prefix stays in one chunk when it
#                    can. 10% overlap is enough because replies are
#                    semantically independent (different authors).
#   city_guides    - ~2,068 chars/doc, sectioned. Full 900 cap under the
#                    model limit, and ~15% overlap because long sections
#                    routinely split into 3+ chunks that need context
#                    bleeding across the cuts.
#   practice       - Omitted -> falls back to globals. Instructor corpus,
#                    no tuning needed.
CORPUS_SETTINGS = {
    "campus_life":    {"chunk_size": 500, "overlap":  50},
    "advice_threads": {"chunk_size": 500, "overlap":  90},
    "city_guides":    {"chunk_size": 900, "overlap":  90},    #overlap10% as we are breakin on paragraph 
}


# *******Deb***

# ─── Chunking (Milestone 3) ──────────────────────────────────────────────────
# These are deliberately plain, generic numbers. Milestone 3 is where you
# replace them with numbers that fit the documents you actually read.

CHUNK_SIZE = 1200        # characters per chunk
CHUNK_OVERLAP = 120     # characters shared between neighbouring chunks



# ─── Retrieval (Milestone 4) ─────────────────────────────────────────────────

TOP_K = 3               # how many chunks to pull back per question

# The relevance gate. If the best chunk is further away than this, the system
# refuses to answer instead of handing the model thin material.
#
# LOWER IS BETTER: 0.3 is a close match, 0.9 is unrelated.
#
# 0.6 is a reasonable starting point, not a right answer. Milestone 4 has you
# measure your own two groups of distances and put the cutoff in the gap.
# Most corpora land somewhere between 0.45 and 0.75.
THRESHOLD = 0.5


# ─── Models ──────────────────────────────────────────────────────────────────
# Embeddings run on your own machine and cost no API quota.
# Only generation calls out to a service.

# This is the model Chroma bundles, and leaving it alone is the fast path: it
# downloads about 80 MB from Chroma's own CDN and needs nothing else installed.
#
# Setting it to any other name — week 2's "try a second embedding model"
# stretch option — switches to loading that model from Hugging Face instead,
# which needs `pip install 'sentence-transformers>=3.4,<3.5'` first. store.py
# says so with a real error message rather than a stack trace if you forget.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MODEL = os.getenv("AI201_MODEL", "gemini-3.5-flash-lite")


# ─── Rate limiting and quota guards ──────────────────────────────────────────
# You should not need to touch these. They exist so that a runaway loop costs
# you a warning instead of your whole day's allowance.

REQUESTS_PER_MINUTE = 30       # outgoing calls the limiter will allow per minute
SESSION_REQUEST_BUDGET = 300   # stop and warn rather than draining the daily quota
MAX_RETRIES = 4                # on 429 / resource-exhausted, with backoff

CACHE_ENABLED = os.getenv("AI201_CACHE", "1") != "0"
CACHE_DIR = ROOT / ".cache"


# ─── Paths ───────────────────────────────────────────────────────────────────

CORPORA_DIR = ROOT / "corpora"
CHROMA_DIR = ROOT / "chroma_db"
RESULTS_DIR = ROOT / "results"


def corpus_path(name: str | None = None) -> Path:
    """Folder holding the documents for a corpus."""
    return CORPORA_DIR / (name or CORPUS) / "documents"


def collection_name(name: str | None = None, variant: str = "default") -> str:
    """
    Name of the vector-store collection for a corpus.

    `variant` lets you index the same corpus two different ways and query both
    without deleting anything — you'll want that in week 2 when you compare
    chunking strategies.

    Chroma is fussy about collection names: 3 to 63 characters, starting and
    ending with a letter or digit, and nothing but letters, digits, underscores
    and hyphens in between. If you bring your own corpus and name the folder
    something Chroma won't accept, this cleans it up rather than failing.
    """
    import re

    raw = f"{name or CORPUS}__{variant}"
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "-", raw)
    cleaned = cleaned.strip("_-")          # must start and end alphanumeric
    if not cleaned or not cleaned[0].isalnum():
        cleaned = f"c{cleaned}"
    if not cleaned[-1].isalnum():
        cleaned = f"{cleaned}0"
    return cleaned[:63].rstrip("_-") or "collection"
