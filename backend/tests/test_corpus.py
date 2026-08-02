from app.engines.rag import corpus


def test_load_sample_corpus_returns_documents_with_required_fields():
    documents = corpus.load_sample_corpus()
    assert len(documents) > 0
    for doc in documents:
        assert doc["id"]
        assert doc["law_name"]
        assert doc["article"]
        assert doc["text"]
        assert doc["keywords"]  # 검색 정확도를 위한 임베딩 전용 키워드


def test_embedding_text_is_short_and_keyword_dense():
    documents = corpus.load_sample_corpus()
    for doc in documents:
        embedding_text = corpus._embedding_text(doc)
        # 임베딩용 텍스트는 본문 전체가 아니라 키워드+제목 정도로 짧아야
        # 검색 신호가 흐려지지 않는다(실측으로 확인된 회귀 방지)
        assert len(embedding_text) < len(doc["text"])


def test_citation_label_combines_law_name_and_article():
    label = corpus.citation_label({"law_name": "근로기준법", "article": "제50조"})
    assert label == "근로기준법 제50조"
