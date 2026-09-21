"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document



@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str                 # which file it came from
    index: int                  # which chunk within that file, starting at 0
    produced_by: str            # the function that made it — cite this in your README


    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in week 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks

'''
def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

    Right now it just calls the fallback. That is the plain, generic behaviour
    the brief is talking about.

    When you write your own strategy, set `produced_by` to
    "chunker.py::split_documents" so your README's Sample Chunks section names
    the right function. `app.py chunks` prints that string for you.

    Things worth thinking about before you write any code:
      - Are your documents short posts or long guides?
      - Is the useful information in one sentence, or spread over a paragraph?
      - Would splitting on paragraph breaks keep more thoughts intact than
        splitting on a character count?
    """
    return fallback_split(documents)
'''



# ****Deb****    
import re 

"""
Stage 2 of the pipeline: splitting documents into chunks.
 
MILESTONE 3: replaced the body of `split_documents` with a structure-aware,
config-driven chunker. `fallback_split` is preserved unchanged for the
comparison the milestone asks for.
 
Behaviour is controlled from config.py:
  - config.CHUNKER_MODE     : "original" | "experiment"  (which chunker runs)
  - config.CORPUS_STRATEGIES: which strategy each corpus uses (experiment mode)
  - config.CORPUS_SETTINGS  : per-corpus chunk_size / overlap overrides
  - config.CHUNK_SIZE       : global default size (original mode + fallback)
  - config.CHUNK_OVERLAP    : global default overlap
  - config.DEFAULT_STRATEGY : fallback strategy when corpus not in the map
 
Strategies (experiment mode):
  - prose_with_headings : short posts; merges a leading heading line with
                          the body paragraph so it isn't orphaned as its
                          own tiny chunk.
  - threaded            : topic line + `--- reply N (X votes) ---` blocks.
                          Each reply becomes its own chunk with the topic
                          prepended so retrieval finds it either way.
  - sectioned           : long guides with labelled sections. Chunks stay
                          within a section and carry the section heading
                          as prefix.
 
Common invariants across strategies:
  - chunks begin and end on sentence boundaries when possible
  - overlap is carried as whole trailing sentences and RESET at every
    paragraph or section boundary — nothing bleeds across unrelated content
  - chunk_size is a HARD cap; a lone over-long sentence falls back to a
    character cut (rare, last resort)
"""


# =====================================================================
# Experiment-mode helpers — regexes and small utilities
# =====================================================================
 
_PARAGRAPH_RE = re.compile(r"\n\s*\n")                   # one or more blank lines
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")               # after . ! ? + whitespace
_REPLY_MARKER_RE = re.compile(                            # "--- reply 1 (27 votes) ---"
    r"^---\s*reply\s+\d+.*?---\s*$",
    re.MULTILINE | re.IGNORECASE,
)
_HEADING_MAX_LEN = 60
 
# Hard ceiling regardless of what config says, because all-MiniLM-L6-v2
# truncates past 256 tokens (~1000-1300 chars). 900 chars ≈ 225 tokens,
# safely under. If someone sets a corpus to 2000 by accident we cap it
# instead of silently truncating embeddings.
_HARD_MAX_CHUNK_SIZE = 900
 
 
def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in _PARAGRAPH_RE.split(text) if p.strip()]
 
 
def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_RE.split(text.strip()) if s.strip()]
 
 
def _looks_like_heading(paragraph: str) -> bool:
    """Short, one-line, no terminal sentence punctuation."""
    if "\n" in paragraph:
        return False
    if len(paragraph) > _HEADING_MAX_LEN:
        return False
    return not paragraph.rstrip().endswith((".", "!", "?"))
 
 
def _overlap_tail(sentences: list[str], overlap: int) -> list[str]:
    """Trailing whole sentences totalling up to `overlap` characters."""
    tail: list[str] = []
    length = 0
    for s in reversed(sentences):
        add = len(s) + (1 if tail else 0)
        if length + add > overlap:
            break
        tail.insert(0, s)
        length += add
    return tail
 
 
def _pack_paragraph(paragraph: str, chunk_size: int, overlap: int) -> list[str]:
    """Pack one paragraph's sentences into <=chunk_size pieces, sentence-aligned."""
    sentences = _split_sentences(paragraph)
    pieces: list[str] = []
    current: list[str] = []
    current_len = 0
 
    for sent in sentences:
        # Single sentence bigger than the cap: flush, then hard-split it.
        if len(sent) > chunk_size:
            if current:
                pieces.append(" ".join(current))
                current, current_len = [], 0
            start = 0
            step = max(1, chunk_size - overlap)
            while start < len(sent):
                piece = sent[start : start + chunk_size].strip()
                if piece:
                    pieces.append(piece)
                start += step
            continue
 
        add = len(sent) + (1 if current else 0)
        if current and current_len + add > chunk_size:
            pieces.append(" ".join(current))
            current = _overlap_tail(current, overlap)
            current_len = sum(len(s) for s in current) + max(0, len(current) - 1)
            add = len(sent) + (1 if current else 0)
 
        current.append(sent)
        current_len += add
 
    if current:
        pieces.append(" ".join(current))
    return pieces
 
 
def _emit(chunks: list[Chunk], text: str, source: str, index: int) -> int:
    """Append a chunk if it has content; return the next index."""
    text = text.strip()
    if not text:
        return index
    chunks.append(
        Chunk(
            text=text,
            source=source,
            index=index,
            produced_by="chunker.py::split_documents",
        )
    )
    return index + 1

# _heading_level replaces the role _looks_like_heading was playing inside
# the sectioned strategy specifically. Keep _looks_like_heading — the
# prose_with_headings strategy still uses it.
 
def _heading_level(paragraph: str) -> int:
    """
    Classify a paragraph as a heading and return its level.
 
    Returns 0 (not a heading), 1 ('# Title'), 2 ('## Section'), etc.
    For corpora without markdown structure, falls back to the prose
    heuristic (short, one-line, no terminal sentence punctuation) and
    treats such paragraphs as level 2 so they still act as section
    boundaries.
    """
    if "\n" in paragraph:
        return 0
    # Explicit markdown heading: '# Title', '## Section', up to '######'
    m = re.match(r"^(#{1,6})\s+\S", paragraph)
    if m:
        return len(m.group(1))
    # Prose fallback (no markdown) — treat as a section-level heading.
    if len(paragraph) <= _HEADING_MAX_LEN and not paragraph.rstrip().endswith((".", "!", "?")):
        return 2
    return 0
  
 
# =====================================================================
# Strategies (experiment mode)
# =====================================================================
 
def _strategy_prose_with_headings(doc: Document, chunk_size: int, overlap: int,
                                  chunks: list[Chunk]) -> None:
    """
    For short posts (campus_life). A leading short line without terminal
    punctuation is treated as a heading and merged with the paragraph that
    follows, so you don't get an orphaned one-line chunk and a headless body.
    """
    paragraphs = _split_paragraphs(doc.text)
 
    merged: list[str] = []
    i = 0
    while i < len(paragraphs):
        p = paragraphs[i]
        if _looks_like_heading(p) and i + 1 < len(paragraphs):
            merged.append(f"{p}\n\n{paragraphs[i + 1]}")
            i += 2
        else:
            merged.append(p)
            i += 1
 
    index = 0
    for paragraph in merged:
        if len(paragraph) <= chunk_size:
            pieces = [paragraph]
        else:
            pieces = _pack_paragraph(paragraph, chunk_size, overlap)
        for piece in pieces:
            index = _emit(chunks, piece, doc.source, index)
 
 
def _strategy_threaded(doc: Document, chunk_size: int, overlap: int,
                       chunks: list[Chunk]) -> None:
    """
    For threaded discussions (advice_threads). Anchors on the
    "--- reply N (X votes) ---" markers rather than blank lines, so it's
    robust to extra whitespace or byline noise in the topic block.
    Each reply becomes its own chunk with the topic line prepended so
    retrieval finds it via the topic phrase AND the reply's own words.
    """
    text = doc.text.strip()
    marker_positions = [m.start() for m in _REPLY_MARKER_RE.finditer(text)]
 
    if not marker_positions:
        # No reply markers -> fall back to blank-line paragraphs.
        paragraphs = _split_paragraphs(text)
        if not paragraphs:
            return
        topic = paragraphs[0]
        replies = paragraphs[1:]
    else:
        topic = text[: marker_positions[0]].strip()
        replies = []
        for i, start in enumerate(marker_positions):
            end = marker_positions[i + 1] if i + 1 < len(marker_positions) else len(text)
            replies.append(text[start:end].strip())
 
    if not replies:

        #_emit(chunks, topic, doc.source, 0)
        return
 
    prefix = f"{topic}\n\n" if topic else ""
    reply_budget = max(1, chunk_size - len(prefix))
 
    index = 0
    for reply in replies:
        if len(reply) + len(prefix) <= chunk_size:
            pieces = [prefix + reply]
        else:
            reply_pieces = _pack_paragraph(reply, reply_budget, overlap)
            pieces = [prefix + rp for rp in reply_pieces]
        for piece in pieces:
            index = _emit(chunks, piece, doc.source, index)
 
 

def _strategy_sectioned(doc: Document, chunk_size: int, overlap: int,
                        chunks: list[Chunk]) -> None:
    """
    For long guides with labelled sections (city_guides).
 
    Splits into (title, intro, sections):
      - Level-1 heading ('# Marchwood')            -> doc title
      - Non-heading paragraphs before the first ## -> intro
      - Level-2 heading + following non-heading    -> section
 
    Emits:
      - The intro as its own chunk (title + intro, no section body).
      - Each section as one or more chunks (title + intro + section
        heading + section body), so every section chunk is self-contained
        for retrieval — doc identity, doc context, section topic, and
        section content are all embedded in one vector.
 
    Chunks NEVER cross a section boundary.
    """
    paragraphs = _split_paragraphs(doc.text)
 
    doc_title: str = ""
    intro_paragraphs: list[str] = []
    sections: list[tuple[str, list[str]]] = []   # (section_heading, body_paragraphs)
    current_section: str = ""
    current_body: list[str] = []
    seen_section = False
 
    for p in paragraphs:
        level = _heading_level(p)
        if level == 1:
            doc_title = p
        elif level >= 2:
            # Flush the previous section (if any) before starting this one.
            if seen_section:
                sections.append((current_section, current_body))
            current_section = p
            current_body = []
            seen_section = True
        else:
            # Non-heading paragraph. Goes to intro until we hit a section.
            if seen_section:
                current_body.append(p)
            else:
                intro_paragraphs.append(p)
    if seen_section:
        sections.append((current_section, current_body))
 
    # Build the intro block once — used both as its own chunk and as
    # a prefix on every section chunk. Empty when the doc has no title
    # and no intro (in which case section chunks just carry section
    # heading + body, matching the previous behaviour).
    intro_block_parts = [x for x in ([doc_title] + intro_paragraphs) if x]
    intro_block = "\n\n".join(intro_block_parts).strip()
 
    index = 0
 
    # 1) Emit the intro as its own chunk if there is one.
    if intro_block:
        index = _emit(chunks, intro_block, doc.source, index)
 
    # 2) Emit each section, prepending intro_block + section heading.
    for section_heading, body_paragraphs in sections:
        prefix_parts = [x for x in (intro_block, section_heading) if x]
        prefix = ("\n\n".join(prefix_parts) + "\n\n") if prefix_parts else ""
        body_budget = max(1, chunk_size - len(prefix))
 
        for paragraph in body_paragraphs:
            if len(paragraph) + len(prefix) <= chunk_size:
                pieces = [prefix + paragraph]
            else:
                packed = _pack_paragraph(paragraph, body_budget, overlap)
                pieces = [prefix + pk for pk in packed]
            for piece in pieces:
                index = _emit(chunks, piece, doc.source, index)
 
        # Section heading with no body: emit the prefix (title + intro
        # + heading) so the heading itself is still retrievable.
        if section_heading and not body_paragraphs:
            index = _emit(chunks, prefix.rstrip(), doc.source, index)
 
 
 
# =====================================================================
# Strategy registry — names here must match the strings on the right in
# config.CORPUS_STRATEGIES.
# =====================================================================
 
_STRATEGIES = {
    "prose_with_headings": _strategy_prose_with_headings,
    "threaded":            _strategy_threaded,
    "sectioned":           _strategy_sectioned,
}
 
 
# =====================================================================
# Settings resolution — most-specific wins
# =====================================================================
 
def _resolve_settings(corpus_key: str) -> tuple[int, int, str]:
    """Resolve (chunk_size, overlap, strategy_name) for a corpus."""
    per_corpus = getattr(config, "CORPUS_SETTINGS", {}).get(corpus_key, {})
 
    chunk_size = per_corpus.get("chunk_size", config.CHUNK_SIZE)
    overlap = per_corpus.get("overlap", config.CHUNK_OVERLAP)
 
    if chunk_size > _HARD_MAX_CHUNK_SIZE:
        print(
            f"[chunker] WARNING: chunk_size {chunk_size} for corpus "
            f"{corpus_key!r} exceeds the {_HARD_MAX_CHUNK_SIZE}-char ceiling "
            f"(all-MiniLM-L6-v2 truncates past 256 tokens). Capping to "
            f"{_HARD_MAX_CHUNK_SIZE}."
        )
        chunk_size = _HARD_MAX_CHUNK_SIZE
 
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be smaller than chunk_size "
            f"({chunk_size}) for corpus {corpus_key!r}"
        )
 
    strategy_name = getattr(config, "CORPUS_STRATEGIES", {}).get(
        corpus_key, getattr(config, "DEFAULT_STRATEGY", "prose_with_headings")
    )
    if strategy_name not in _STRATEGIES:
        raise ValueError(
            f"config points corpus {corpus_key!r} at strategy "
            f"{strategy_name!r}, which is not a known strategy. "
            f"Known: {sorted(_STRATEGIES)}"
        )
 
    return chunk_size, overlap, strategy_name
 
 
# =====================================================================
# Public entry point — dispatches based on config.CHUNKER_MODE
# =====================================================================
 
def _split_documents_experiment(documents: list[Document],
                                corpus: str | None = None) -> list[Chunk]:
    """Structure-aware, config-driven chunking (Milestone 3 improvement)."""
    corpus_key = (corpus or config.CORPUS or "").strip().lower()
    chunk_size, overlap, strategy_name = _resolve_settings(corpus_key)
    strategy = _STRATEGIES[strategy_name]
 
    chunks: list[Chunk] = []
    for doc in documents:
        strategy(doc, chunk_size, overlap, chunks)
    return chunks
 
 
def split_documents(documents: list[Document],
                    corpus: str | None = None) -> list[Chunk]:
    """
    Dispatch to the chunker named by config.CHUNKER_MODE.
 
      "original"   -> fallback_split (starter's fixed-size windows)
      "experiment" -> structure-aware strategy chosen per corpus
 
    Unknown values fall back to "experiment" with a warning, so a typo in
    config doesn't silently drop you back to the fixed-size chunker.
    """
    mode = getattr(config, "CHUNKER_MODE", "experiment").strip().lower()
 
    if mode == "original":
        chunks = fallback_split(documents)
        # Re-tag so the Sample Chunks output names the mode we ran in.
        for c in chunks:
            c.produced_by = (
                "chunker.py::split_documents (original mode -> fallback_split)"
            )
        return chunks
 
    if mode != "experiment":
        print(
            f"[chunker] WARNING: config.CHUNKER_MODE={mode!r} is not "
            f"'original' or 'experiment'. Using 'experiment'."
        )
 
    return _split_documents_experiment(documents, corpus=corpus)
# *****Deb****

def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
