STOREFRONT_WORKSPACE = {
    "organizations": [{"id": "acme", "name": "Acme"}],
    "projects": [
        {
            "key": "storefront",
            "name": "storefront",
            "repositories": ["shop"],
            "roles": [{"role": "client", "org": "acme"}],
        }
    ],
    "repositories": [{"key": "shop", "access": "admin"}],
}
