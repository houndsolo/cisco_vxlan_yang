vyos_leafs = [
    {
        "hostname": "vtep-fichina",
        "host_node": "fichina",
        "node_id": 10,
        "spine_connections": [
            {"spine_id": 1, "interface": "1/0/14"},
            {"spine_id": 2, "interface": "1/0/8"}
        ],
        "leaf_connections": [
            {"leaf_id": 1, "interface": "1/0/6"},
        ],
    },
    {
        "hostname": "vtep-fortuna",
        "host_node": "fortuna",
        "node_id": 11,
        "spine_connections": [
            {"spine_id": 1, "interface": "1/0/5"},
            {"spine_id": 2, "interface": "1/0/13"}
        ],
        "leaf_connections": [
        ],
    },
    {
        "hostname": "vtep-macbeth",
        "host_node": "macbeth",
        "node_id": 12,
        "spine_connections": [
            {"spine_id": 1, "interface": "1/0/15"},
            {"spine_id": 2, "interface": "1/0/6"}
        ],
        "leaf_connections": [
            {"leaf_id": 1, "interface": "1/0/8"},
        ],
    },
    {
        "hostname": "vtep-titania",
        "host_node": "titania",
        "node_id": 13,
        "spine_connections": [
            {"spine_id": 1, "interface": "1/0/13"},
            {"spine_id": 2, "interface": "1/0/5"}
        ],
        "leaf_connections": [
            {"leaf_id": 1, "interface": "1/0/5"},
        ],
    },
    {
        "hostname": "vtep-zoness",
        "host_node": "zoness",
        "node_id": 14,
        "spine_connections": [
            {"spine_id": 1, "interface": "1/0/6"},
            {"spine_id": 2, "interface": "1/0/15"}
        ],
        "leaf_connections": [
        ],
    },
    {
        "hostname": "vtep-venom",
        "host_node": "venom",
        "node_id": 17,
        "spine_connections": [
            {"spine_id": 1, "interface": "1/0/16"},
            {"spine_id": 2, "interface": "1/0/7"}
        ],
        "leaf_connections": [
            {"leaf_id": 1, "interface": "1/0/7"},
        ],
    },
    {
        "hostname": "vtep-eldarad",
        "host_node": "eldarad",
        "node_id": 21,
        "spine_connections": [
            {"spine_id": 1, "interface": "1/0/7"},
            {"spine_id": 2, "interface": "1/0/16"}
        ],
        "leaf_connections": [
            {"leaf_id": 2, "interface": "1/0/6"},
        ],
    },
]

