from datetime import date

from tadu.param import Param
from tadu.param_options import param_options


def test_a_day_reads_as_a_date_unless_parsed_otherwise() -> None:
    assert param_options(Param("since", "day", "h")) == {
        "help": "h",
        "type": date.fromisoformat,
        "metavar": "YYYY-MM-DD",
    }
    own = Param("at", "day", "h", metavar="DAY", parse=str.strip)
    assert param_options(own) == {"help": "h", "type": str.strip, "metavar": "DAY"}


def test_a_positional_list_does_not_append() -> None:
    assert param_options(Param("paths", "list", "h", positional=True)) == {"help": "h"}
    assert param_options(Param("label", "list", "h"))["action"] == "append"
