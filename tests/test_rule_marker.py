from tadu.rule_marker import RuleMarker


def test_marker_records_kind_span_and_version() -> None:
    marker = RuleMarker("open", 4, 26, 1)
    assert (marker.kind, marker.start, marker.end, marker.version) == ("open", 4, 26, 1)
