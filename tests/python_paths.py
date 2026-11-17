"""Which expressions of a Python module hold filesystem paths, inferred from the syntax."""

import ast

PATH_METHODS = {"resolve", "absolute", "expanduser", "with_name", "with_suffix", "joinpath"}


def is_path_annotation(annotation: ast.expr | None) -> bool:
    """`Path`, `Path | None` and the like."""
    return annotation is not None and any(
        isinstance(node, ast.Name) and node.id == "Path" for node in ast.walk(annotation)
    )


def path_like(expr: ast.expr, names: set[str]) -> bool:
    """A path built by `Path(...)`, a path method, `.parent`, `/`, or a name known to hold one."""
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
        return path_like(expr.left, names) or path_like(expr.right, names)
    func = expr.func if isinstance(expr, ast.Call) else None
    return (
        (isinstance(func, ast.Name) and func.id == "Path")
        or (isinstance(func, ast.Attribute) and func.attr in PATH_METHODS)
        or (isinstance(expr, ast.Attribute) and expr.attr == "parent")
        or (isinstance(expr, ast.Name) and expr.id in names)
    )


def holds_paths(expr: ast.expr, names: set[str], containers: set[str]) -> bool:
    """True when any part of the expression is a path or a container of paths."""
    return any(
        (isinstance(node, ast.expr) and path_like(node, names))
        or (isinstance(node, ast.Name) and node.id in containers)
        for node in ast.walk(expr)
    )


def bound_names(target: ast.expr) -> list[str]:
    """The plain names an assignment or loop target binds."""
    return [node.id for node in ast.walk(target) if isinstance(node, ast.Name)]


def learn(node: ast.AST, names: set[str], containers: set[str]) -> None:
    """Add what one assignment or loop says about paths to `names` and `containers`."""
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target, value = node.targets[0], node.value
        if isinstance(target, ast.Name) and path_like(value, names):
            names.add(target.id)
        elif holds_paths(value, names, containers):
            containers.update(bound_names(target))
    elif isinstance(node, ast.For | ast.comprehension) and holds_paths(
        node.iter, names, containers
    ):
        names.update(bound_names(node.target))


def path_names(nodes: list[ast.AST]) -> set[str]:
    """Names that hold a path somewhere in the module: annotated, assigned or iterated.

    `nodes` is every node of the module. One set per module is enough for tadu's
    one-function modules.
    """
    names = {
        node.arg if isinstance(node, ast.arg) else ast.unparse(node.target)
        for node in nodes
        if isinstance(node, ast.arg | ast.AnnAssign) and is_path_annotation(node.annotation)
    }
    containers: set[str] = set()
    binders = [node for node in nodes if isinstance(node, ast.Assign | ast.For | ast.comprehension)]
    for _ in range(3):
        for node in binders:
            learn(node, names, containers)
    return names
