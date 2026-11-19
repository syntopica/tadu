from tadu.param import Param
from tadu.param_help import param_help


def test_a_format_leads_the_help() -> None:
    assert param_help(Param("type", "text", "type slug", format=2)) == "format 2: type slug"
    assert param_help(Param("title", "text", "one line")) == "one line"
