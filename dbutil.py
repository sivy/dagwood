import os
import sqlite3
from collections import namedtuple

DBNAME = 'database.db'

CREATE_DB_SQL = """
    CREATE TABLE nodes (
      id    INTEGER PRIMARY KEY AUTOINCREMENT,
      label STRING,
      title STRING NOT NULL,
      classes STRING NULL,
      effect STRING NULL,
      weight FLOAT NULL
    );

    CREATE TABLE edges (
      xfrom INTEGER REFERENCES nodes,
      xto INTEGER REFERENCES nodes,
      PRIMARY KEY(xfrom, xto)
    );

    --INSERT INTO nodes (title, label, weight) VALUES (
    --    'MY PROJECT', 'my_project', '0'
    --);
    --INSERT INTO nodes (title, label, classes, weight) VALUES (
    --    'Skills', 'skills', 'education', '0.9'
    --);
    --INSERT INTO nodes (title, label, classes, weight) VALUES (
    --    'Tools', 'tools', 'wealth', '0.9'
    --);
    --INSERT INTO nodes (title, label, classes, weight) VALUES (
    --    'Materials', 'materials', 'wealth', '0.9'
    --);

    --INSERT INTO edges (xfrom, xto) VALUES (2, 1);
    --INSERT INTO edges (xfrom, xto) VALUES (3, 1);
    --INSERT INTO edges (xfrom, xto) VALUES (4, 1);
"""


CREATE_NODE_SQL = """
INSERT INTO nodes (label, title, classes, effect, weight) VALUES (?, ?, ?, ?, ?);
"""

UPDATE_NODE_SQL = """
UPDATE nodes SET title = ?, label = ?, classes = ?, effect = ?, weight = ? WHERE id = ?;
"""

DELETE_NODE_SQL = """
DELETE FROM nodes WHERE id = ?;
"""

GET_ALL_NODES_SQL = """
SELECT * FROM nodes;
"""

CREATE_EDGE_SQL = """
INSERT INTO edges (xfrom, xto) VALUES (?, ?);
"""

GET_ALL_EDGES_SQL = """
SELECT * from edges WHERE xfrom IS NOT NULL and xto IS NOT NULL;
"""

# GET_GRAPH_SQL = """
# WITH RECURSIVE
#     ancestor(id) AS (
#         SELECT * FROM nodes WHERE id=?
#         UNION
#         SELECT edges.xfrom
#           FROM ancestor, edges, nodes
#           WHERE ancenstor.id=edges.xto
#           AND nodes.id=edges.xfrom
#     ) SELECT * from nodes JOIN ancestor USING(id);
# """

Node = namedtuple("Node", "id, label, title, classes, effect, weight")
Edge = namedtuple("Edge", "xfrom, xto")

CLASSES=[
    "wealth",
    "relationships",
    "education",
    "time",
    "government",
    "health",
]

FILL_COLORS = {
    "wealth": "#D5E8D4",
    "relationships": "#DAE8FC",
    "education": "#E1D5E7",
    "time": "#FFF2CC",
    "government": "#F5F5F5",
    "health": "#F8CECC",
}

STROKE_COLORS = {
    "wealth": "#82B366",
    "relationships": "#6C8EBF",
    "education": "#9673A6",
    "time": "#D6B656",
    "government": "#666666",
    "health": "#B85450",
}

# TODO don't call this every start-up (see below where called in if...__MAIN__)
# probably a way with flask to have an initial database.db instead
def bootstrap_db():

    needs_create = not os.path.exists(DBNAME)

    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    if needs_create:
        c.executescript(CREATE_DB_SQL)

    conn.commit()
    conn.close()


# TODO I bet it is fine to leave sqlite connection persistent instead of opening/closing for each call
def create_node(title, label=None, classes=None, effect='', weight=1.0):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    if label is None:
        label = title.lower().replace(" ", "_")

    node = Node(
        id=None,
        label=label,
        title=title,
        classes=classes,
        effect=effect,
        weight=weight,
        )

    c.execute(CREATE_NODE_SQL, node[1:])

    conn.commit()
    conn.close()
    return c.lastrowid

def update_node(node_data):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    print("node data to update: " + str(node_data))

    c.execute(UPDATE_NODE_SQL, node_data)

    conn.commit()
    conn.close()


def create_edge(xfrom, xto):
    print("creating edge: %r, %r" % (xfrom, xto))
    if not xfrom or not xto:
        return

    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    edge = Edge(xfrom, xto)

    c.execute(CREATE_EDGE_SQL, edge)

    conn.commit()
    conn.close()


def get_nodes_by_id():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    c.execute(GET_ALL_NODES_SQL)
    ret = c.fetchall()

    conn.commit()
    conn.close()

    node_graph = {n.id:n for n in [Node(*r) for r in ret]}
    print(node_graph)
    return node_graph

def get_nodes_data():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    c.execute(GET_ALL_NODES_SQL)
    ret = c.fetchall()

    conn.commit()
    conn.close()

    node_graph = {n.id:n._asdict() for n in [Node(*r) for r in ret]}
    print(node_graph)
    return node_graph


def get_all_edges():
    conn = sqlite3.connect(DBNAME)

    c = conn.cursor()

    c.execute(GET_ALL_EDGES_SQL)

    ret = c.fetchall()

    conn.commit()
    conn.close()

    return [Edge(*r) for r in ret]

def get_graph():
    nodes = get_nodes_by_id()
    edges = get_all_edges()

    graph = []
    for xfrom, xto in edges:
        graph.append([
            nodes[xfrom],
            nodes[xto],
        ])

    return graph


def get_graph_json():
    nodes = get_nodes_by_id()
    edges = get_all_edges()

    graph = []
    for xfrom, xto in edges:
        graph.append([
            nodes[xfrom]._asdict(),
            nodes[xto]._asdict(),
        ])

    return graph
