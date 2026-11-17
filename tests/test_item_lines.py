from tadu.add_request import AddRequest
from tadu.item_lines import item_lines


def test_category_prefix_fields_then_notes() -> None:
    request = AddRequest(" Pick one ", "Shipping", (("Kind", " decision "),), ("REST or SOAP.",))
    assert item_lines(request) == [
        "- [ ] **Shipping:** Pick one",
        "",
        "  Kind: decision",
        "",
        "  REST or SOAP.",
    ]


def test_existing_prefix_and_no_category_stay() -> None:
    assert item_lines(AddRequest("**Ops:** Renew", "Shipping", (), ())) == ["- [ ] **Ops:** Renew"]
    assert item_lines(AddRequest("Renew", None, (), ())) == ["- [ ] Renew"]
