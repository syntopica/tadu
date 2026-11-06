from board_js import js_card

WORKSPACE = {
    "organizations": [
        {"id": "pp", "name": "Pixel Potion"},
        {"id": "br", "name": "BusiRocket"},
        {"id": "at", "name": "Automate Texas"},
    ],
    "projects": [
        {
            "key": "gtm",
            "name": "VerticaGTM",
            "repositories": ["gtm", "gtm-web"],
            "roles": [{"role": "company", "org": "pp"}, {"role": "client", "org": "at"}],
        },
        {
            "key": "joy",
            "name": "10xJoy",
            "repositories": ["joy"],
            "roles": [{"role": "company", "org": "pp"}],
        },
        {
            "key": "tele",
            "name": "Teleporte",
            "repositories": ["tele"],
            "roles": [{"role": "company", "org": "br"}],
        },
        {"key": "lone", "name": "Lone", "repositories": ["lone-repo"], "roles": []},
    ],
    "repositories": [
        {"key": key} for key in ("gtm", "gtm-web", "joy", "tele", "lone-repo", "misc")
    ],
}
PLACES = [
    ("gtm", "gtm", "backlog"),
    ("gtm", "gtm", "blocked"),
    ("gtm", "gtm", "done"),
    ("gtm", "gtm-web", "in_progress"),
    ("gtm", "gtm-web", "cancelled"),
    ("joy", "joy", "backlog"),
    ("tele", "tele", "blocked"),
    (None, "misc", "backlog"),
    ("lone", "lone-repo", "ready"),
]
CARDS = [
    js_card(column, key=f"k{at}", project=project, repository=repository)
    for at, (project, repository, column) in enumerate(PLACES)
]
