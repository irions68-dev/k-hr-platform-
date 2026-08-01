from app.engines.rag.citation_verifier import UNVERIFIED_NOTICE, verify_citations


def test_exact_match_is_verified():
    result = verify_citations(
        cited_references=["파견근로자보호 등에 관한 법률 제6조"],
        retrieved_citations=["파견근로자보호 등에 관한 법률 제6조", "근로기준법 제50조"],
    )
    assert result["verified_references"] == ["파견근로자보호 등에 관한 법률 제6조"]
    assert result["rejected_references"] == []
    assert result["final_references"] == ["파견근로자보호 등에 관한 법률 제6조"]


def test_cited_reference_with_extra_detail_still_matches_by_substring():
    result = verify_citations(
        cited_references=["파견근로자보호 등에 관한 법률 제6조 (파견기간)"],
        retrieved_citations=["파견근로자보호 등에 관한 법률 제6조"],
    )
    assert result["verified_references"] == ["파견근로자보호 등에 관한 법률 제6조 (파견기간)"]


def test_hallucinated_reference_is_rejected_and_replaced():
    result = verify_citations(
        cited_references=["존재하지않는법 제99조"],
        retrieved_citations=["근로기준법 제50조"],
    )
    assert result["verified_references"] == []
    assert result["rejected_references"] == ["존재하지않는법 제99조"]
    assert result["final_references"] == [UNVERIFIED_NOTICE]


def test_mixed_verified_and_rejected_references():
    result = verify_citations(
        cited_references=["근로기준법 제50조", "존재하지않는법 제99조"],
        retrieved_citations=["근로기준법 제50조"],
    )
    assert result["verified_references"] == ["근로기준법 제50조"]
    assert result["rejected_references"] == ["존재하지않는법 제99조"]
    # 검증된 인용이 하나라도 있으면 그것만 최종 인용으로 사용한다
    assert result["final_references"] == ["근로기준법 제50조"]


def test_no_citations_at_all_falls_back_to_notice():
    result = verify_citations(cited_references=[], retrieved_citations=["근로기준법 제50조"])
    assert result["final_references"] == [UNVERIFIED_NOTICE]
