"""Tool arguments as command-line options."""

from __future__ import annotations

LISTS = {"assignees", "labels"}
POSITIONAL = {"key", "repository"}


def mcp_options(arguments: dict[str, object]) -> list[str]:
    """`--flag=value` for each argument, so no value is read as a flag.

    A true boolean is a bare flag and a false one is left out; assignees and labels
    join with commas; notes repeat `--note`.
    """
    options: list[str] = []
    for key, value in arguments.items():
        flag = "--" + ("note" if key == "notes" else key.replace("_", "-"))
        if key in POSITIONAL or value is False:
            continue
        if value is True:
            options.append(flag)
        elif isinstance(value, list) and key in LISTS:
            options.append(f"{flag}={', '.join(str(item) for item in value)}")
        elif isinstance(value, list):
            options += [f"{flag}={item}" for item in value]
        else:
            options.append(f"{flag}={value}")
    return options
