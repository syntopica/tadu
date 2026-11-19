"""The git data of the fake GitHub: heads, commits, trees, branches, pull requests, issues."""

import hashlib
import itertools
from dataclasses import dataclass, field


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data, usedforsecurity=False).hexdigest()


@dataclass
class FakeGit:
    """One commit per repository to begin with (`seed`), and what people POST on top of it.

    `pushers` maps a repository to the logins that may push. `created` records every
    POST of the git data API, pulls and issues as (kind, repository, login, body), so a
    test can say what was made and, above all, what was not.
    """

    default_branch: str = "main"
    pushers: dict[str, set[str]] = field(default_factory=dict)
    trees: dict[str, dict[str, str]] = field(default_factory=dict)
    commits: dict[str, str] = field(default_factory=dict)
    refs: dict[str, dict[str, str]] = field(default_factory=dict)
    blobs: dict[str, bytes] = field(default_factory=dict)
    protected: set[str] = field(default_factory=set)
    created: list[tuple[str, str, str, dict[str, object]]] = field(default_factory=list)
    serial: "itertools.count[int]" = field(default_factory=lambda: itertools.count(1))

    def seed(self, repository: str, files: dict[str, bytes]) -> None:
        """The repository's default branch holds exactly these files, in one commit."""
        tree = {path: git_blob_sha(data) for path, data in files.items()}
        self.blobs |= {git_blob_sha(data): data for data in files.values()}
        self.trees[f"tree-{repository}"] = tree
        self.commits[f"commit-{repository}"] = f"tree-{repository}"
        self.refs[repository] = {f"heads/{self.default_branch}": f"commit-{repository}"}

    def get(self, repository: str, path: str, query: str) -> tuple[int, object]:
        """Answer a GET under /repos/<repository>/git/ (`path` is what follows `git/`)."""
        if path.startswith("ref/") and path.removeprefix("ref/") in self.refs.get(repository, {}):
            sha = self.refs[repository][path.removeprefix("ref/")]
            return 200, {"object": {"sha": sha}}
        if path.removeprefix("commits/") in self.commits:
            return 200, {"tree": {"sha": self.commits[path.removeprefix("commits/")]}}
        tree = self.trees.get(path.removeprefix("trees/"))
        if tree is not None and query == "recursive=1":
            entries = [{"path": p, "type": "blob", "sha": s} for p, s in sorted(tree.items())]
            return 200, {"tree": entries, "truncated": False}
        return 404, {"message": "Not Found"}

    def post(
        self, repository: str, login: str, tail: str, body: dict[str, object]
    ) -> tuple[int, object]:
        """Answer a POST under /repos/<repository>/; anyone may open an issue, only pushers the rest."""
        self.created.append((tail, repository, login, body))
        number = next(self.serial)
        if tail != "issues" and login not in self.pushers.get(repository, set()):
            return 403, {"message": "Resource not accessible by integration"}
        made = {
            "issues": {"html_url": f"https://github.test/{repository}/issues/{number}"},
            "pulls": {"html_url": f"https://github.test/{repository}/pull/{number}"},
        }
        if tail in made:
            return 201, made[tail]
        return self.post_git(repository, tail, body, number)

    def change(
        self, repository: str, login: str, call: str, body: dict[str, object]
    ) -> tuple[int, object]:
        """Answer a PUT (merge a pull request) or PATCH (move a branch) under /repos/<repository>/.

        `call` is the method and what follows the repository, such as `PATCH git/refs/heads/main`.

        Only pushers may; a repository in `protected` refuses both, as a protected branch does.
        """
        self.created.append((call, repository, login, body))
        method, tail = call.split(" ", 1)
        if login not in self.pushers.get(repository, set()):
            return 403, {"message": "Resource not accessible by integration"}
        ref = tail.removeprefix("git/refs/")
        if repository in self.protected:
            return 405, {"message": "Protected branch"}
        if method == "PATCH" and ref in self.refs.get(repository, {}):
            self.refs[repository][ref] = str(body["sha"])
        elif not (method == "PUT" and tail.startswith("pulls/")):
            return 404, {"message": "Not Found"}
        return 200, {}

    def post_git(
        self, repository: str, tail: str, body: dict[str, object], number: int
    ) -> tuple[int, object]:
        """The git data API: a tree, a commit on it, a branch at the commit."""
        if tail == "git/trees":
            return 201, {"sha": self.new_tree(body)}
        if tail == "git/commits":
            self.commits[f"commit-{number}"] = str(body["tree"])
            return 201, {"sha": f"commit-{number}"}
        if tail == "git/refs":
            self.refs[repository][str(body["ref"]).removeprefix("refs/")] = str(body["sha"])
            return 201, {"ref": body["ref"]}
        return 404, {"message": "Not Found"}

    def new_tree(self, body: dict[str, object]) -> str:
        """A tree like the base one with the entries' files added, changed or (sha null) deleted."""
        tree = dict(self.trees[str(body["base_tree"])])
        for entry in body["tree"]:  # type: ignore[attr-defined]
            if "content" in entry:
                data = entry["content"].encode()
                self.blobs[git_blob_sha(data)] = data
                tree[entry["path"]] = git_blob_sha(data)
            else:
                del tree[entry["path"]]
        sha = f"tree-{next(self.serial)}"
        self.trees[sha] = tree
        return sha
