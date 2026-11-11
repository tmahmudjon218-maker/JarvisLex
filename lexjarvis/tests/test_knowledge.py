from lexjarvis.knowledge import KnowledgeBase, split_into_chunks, tokenize

SAMPLE = """# Davlat belgilari

Davlatning hududi, aholisi va suveren hokimiyati uning asosiy belgilaridir.

# Huquq normalari

Huquq normasi — davlat tomonidan o'rnatilgan yoki ruxsat etilgan, majburiy xulq-atvor qoidasi.

Qonunlar huquq normalarini mustahkamlovchi asosiy manbadir.
"""


def test_tokenize_normalises_apostrophes_and_stems():
    assert tokenize("O‘zbekiston") == tokenize("O'zbekiston")
    assert tokenize("qonunlar") == tokenize("qonunlarning")


def test_chunks_do_not_cross_headings():
    chunks = split_into_chunks("a.md", SAMPLE)
    assert [c.heading for c in chunks] == ["Davlat belgilari", "Huquq normalari"]
    assert chunks[1].ref == "a.md#1"
    assert "suveren" not in chunks[1].text


def test_search_ranks_relevant_chunk_first():
    kb = KnowledgeBase(split_into_chunks("a.md", SAMPLE))
    hits = kb.search("huquq normasi nima?")
    assert hits and hits[0][0].heading == "Huquq normalari"


def test_search_returns_nothing_for_unrelated_query():
    kb = KnowledgeBase(split_into_chunks("a.md", SAMPLE))
    assert kb.search("kvant fizikasi") == []


def test_from_directory_loads_md_and_txt(tmp_path):
    (tmp_path / "x.md").write_text(SAMPLE, encoding="utf-8")
    (tmp_path / "y.txt").write_text("Qonun matni.", encoding="utf-8")
    (tmp_path / "skip.pdf").write_bytes(b"%PDF")
    kb = KnowledgeBase.from_directory(tmp_path)
    assert {c.source for c in kb.chunks} == {"x.md", "y.txt"}
