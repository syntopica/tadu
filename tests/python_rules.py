"""Project-wide rules for tadu's Python sources, checked on the syntax tree.

Each rule names a shape that once let tadu act on the wrong thing. A line may carry
the rule's marker with a reason (on the line, or the line above the statement) when
the shape is safe there; the reason is what a reviewer reads.
"""

import ast
import re

from python_paths import path_like, path_names

WRITERS = {"write_file_atomically.py", "create_file_exclusively.py"}
MUTATORS = {"write_text", "write_bytes", "unlink", "rmdir", "mkdir", "touch", "chmod"}
MUTATORS |= {"hardlink_to", "symlink_to", "rename"}
OS_MUTATORS = {"replace", "rename", "remove", "unlink", "rmdir", "makedirs", "mkdir", "fdopen"}
OS_MUTATORS |= {"write", "truncate", "link", "symlink"}
MARKERS = {"P001": "path-name", "P002": "keys", "P003": "writes"}


def write_mode(call: ast.Call, position: int) -> bool:
    """An `open` whose mode (positional or keyword) writes, appends, creates or updates."""
    modes = [keyword.value for keyword in call.keywords if keyword.arg == "mode"]
    modes += call.args[position : position + 1]
    return any(
        isinstance(mode, ast.Constant) and set(str(mode.value)) & set("wax+") for mode in modes
    )


def module_writes(owner: str | None, call: ast.Call) -> bool:
    """`os`, `shutil` and `tempfile` functions that change the filesystem."""
    attr = call.func.attr  # type: ignore[attr-defined]
    if owner == "os" and attr == "open":
        return any(flag in ast.unparse(call) for flag in ("O_WRONLY", "O_RDWR", "O_CREAT"))
    return owner in ("shutil", "tempfile") or (owner == "os" and attr in OS_MUTATORS)


def method_writes(func: ast.Attribute, call: ast.Call, names: set[str]) -> bool:
    """Path methods that change the filesystem; `replace` only on a path (str has one too)."""
    if func.attr == "open":
        return write_mode(call, 0)
    return func.attr in MUTATORS or (
        func.attr == "replace" and len(call.args) == 1 and path_like(func.value, names)
    )


def writes(call: ast.Call, names: set[str]) -> bool:
    """Whether the call changes the filesystem."""
    func = call.func
    if isinstance(func, ast.Name):
        return func.id == "open" and write_mode(call, 1)
    if not isinstance(func, ast.Attribute):
        return False
    owner = func.value.id if isinstance(func.value, ast.Name) else None
    if owner in ("os", "shutil", "tempfile"):
        return module_writes(owner, call)
    return method_writes(func, call, names)


def unique_by_source(node: ast.DictComp) -> bool:
    """`{key: ... for key, ... in x.items()}` keeps the keys of a dict, which are unique."""
    generator = node.generators[0]
    iterated = generator.iter
    method = iterated.func if isinstance(iterated, ast.Call) else None
    keeps = isinstance(method, ast.Attribute) and method.attr in ("items", "keys")
    first = (
        generator.target.elts[0] if isinstance(generator.target, ast.Tuple) else generator.target
    )
    return keeps and ast.unparse(node.key) == ast.unparse(first) and len(node.generators) == 1


def loose_keys(nodes: list[ast.AST]) -> list[ast.AST]:
    """Dicts built from data: comprehensions, `dict.fromkeys`, and `x[key] = ...` in loops."""
    found: list[ast.AST] = [
        node
        for node in nodes
        if (isinstance(node, ast.DictComp) and not unique_by_source(node))
        or (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "fromkeys"
        )
    ]
    for loop in (node for node in nodes if isinstance(node, ast.For | ast.While)):
        for node in ast.walk(loop):
            if isinstance(node, ast.Assign):
                found += [
                    target
                    for target in node.targets
                    if isinstance(target, ast.Subscript)
                    and not isinstance(target.slice, ast.Constant | ast.UnaryOp)
                ]
    return found


def marked(lines: list[str], node: ast.AST, code: str) -> bool:
    """The marker with a reason on one of the node's lines or in the comments right above."""
    first, last = node.lineno - 1, (node.end_lineno or node.lineno)  # type: ignore[attr-defined]
    while first > 0 and lines[first - 1].strip().startswith("#"):
        first -= 1
    pattern = re.compile(rf"# {MARKERS[code]}: \S")
    return any(pattern.search(line) for line in lines[first:last])


def unchecked_writes(nodes: list[ast.AST]) -> list[ast.AST]:
    """Functions that replace a file without first checking it still holds what was read."""
    found: list[ast.AST] = []
    for function in (node for node in nodes if isinstance(node, ast.FunctionDef)):
        called = [
            node.func.id
            for node in ast.walk(function)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        if "write_file_atomically" in called and "backlog_unchanged" not in called:
            found.append(function)
    return found


def rule_findings(source: str, module: str) -> list[tuple[str, int, str]]:
    """(code, line, text) for every unmarked breach of the rules in one module."""
    nodes, lines = list(ast.walk(ast.parse(source))), source.splitlines()
    names = path_names(nodes)
    found: list[tuple[str, ast.AST]] = [
        ("P001", node)
        for node in nodes
        if isinstance(node, ast.Attribute)
        and node.attr in ("name", "stem")
        and path_like(node.value, names)
    ]
    found += [("P002", node) for node in loose_keys(nodes)]
    if module not in WRITERS:
        found += [
            ("P003", node) for node in nodes if isinstance(node, ast.Call) and writes(node, names)
        ]
        found += [("P004", node) for node in unchecked_writes(nodes)]
    return sorted(
        (code, node.lineno, ast.unparse(node).splitlines()[0])  # type: ignore[attr-defined]
        for code, node in found
        if code == "P004" or not marked(lines, node, code)
    )
