from app.engines.rag import corpus


def test_load_sample_corpus_returns_documents_with_required_fields():
    documents = corpus.load_sample_corpus()
    assert len(documents) > 0
    for doc in documents:
        assert doc["id"]
        assert doc["law_name"]
        assert doc["article"]
        assert doc["text"]


def test_citation_label_combines_law_name_and_article():
    label = corpus.citation_label({"law_name": "근로기준법", "article": "제50조"})
    assert label == "근로기준법 제50조"
