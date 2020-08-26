#!/usr/bin/env python
# -*- coding: utf-8 -*-

# quick and dirty DAG

import os
import dbutil
import io
import networkx as nx
# import matplotlib
# matplotlib.use("Agg")
# import matplotlib.pyplot as plt


from flask import Flask, request, render_template, jsonify, make_response

# Support for gomix's 'front-end' and 'back-end' UI.
app = Flask(__name__, static_folder='public', template_folder='views')

# Set the app secret key from the secret environment variables.
app.secret = os.environ.get('SECRET')

def build_graph():
    nodes = dbutil.get_nodes_data()

    for n in nodes.values():
        classes = n["classes"]
        n.update({
            "id": n["label"],
            "label": n["title"],
            "color": dbutil.STROKE_COLORS[classes] if classes else "#666666",
            "fillcolor": dbutil.FILL_COLORS[classes] if classes else "#ffffff",
        })

    graph = dbutil.get_graph()

    G = nx.DiGraph()
    G.add_nodes_from([(n["title"], n) for _, n in nodes.items()])

    for xfrom, xto in graph:
        G.add_edge(
            xfrom.title, xto.title,
            label=xfrom.effect or "",
            color=dbutil.STROKE_COLORS[xfrom.classes] if xfrom.classes else "#666666",
            weight=xfrom.weight)

    return G


@app.route('/')
def homepage():
    """Displays the homepage."""

    nodes = dbutil.get_nodes_by_id()
    classes = dbutil.CLASSES

    return render_template(
        'index.html', nodes=nodes, classes=classes)


@app.route('/graph.svg')
def graph_png():
    G = build_graph()

    A = nx.nx_agraph.to_agraph(G)
    A.graph_attr['label'] = "Generated by Dagwood"

    A.graph_attr['rankdir'] = 'LR'
    A.node_attr.update(
        style="filled",
        shape='box',
        fontname='Helvetica',
        fontsize='12',
    )
    A.edge_attr.update(
        fontname='Helvetica',
        fontsize='9',
        arrowhead="vee",
        arrowsize=0.8,
    )
    print(A)

    svg_output = A.draw(format="svg", prog="dot")  # draw png
    response = make_response(svg_output)

    # pos = nx.drawing.nx_agraph.graphviz_layout(G, prog="neato")

    # nx.draw_networkx_nodes(
    #     G, pos, **{
    #         "node_size": 300, "node_color": "white",
    #         "edgecolors": "blue", "node_shape": "s",
    #     })

    # nx.draw_networkx_edges(
    #     G, pos, width=1, arrowstyle="->", arrowsize=20)

    # # labels
    # nx.draw_networkx_labels(G, pos, font_size=12, font_family="sans-serif")

    # png_output = io.BytesIO()
    # plt.savefig(png_output)
    # response = make_response(png_output.getvalue())

    response.headers['Content-Type'] = 'image/svg+xml'
    return response

@app.route('/nodes', methods=['GET', 'POST'])
def nodes():
    """Simple API endpoint for dreams.
    In memory, ephemeral, like real dreams.
    """

    # Add a dream to the in-memory database, if given.
    if request.method == 'POST':
        data = None
        if request.is_json:
            data = request.get_json()
            print('JSON!')
            print(data)
        else:
            # Note: request args is bad form for POSTs
            # However, we're preserving this approach so that the HTML client
            # can still work
            data = request.args
            print('NOT JSON!')
            print(data)

        if 'node' in data:
            title = data['node']
            target = data['target']
            class_ = data['class']

            node_id = dbutil.create_node(title, classes=class_)
            if target:
                dbutil.create_edge(node_id, target)

    # Return the list of remembered dreams.
    return jsonify(dbutil.get_graph_json())

if __name__ == '__main__':
    dbutil.bootstrap_db()
    app.run(debug=True)