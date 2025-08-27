import os

import networkx as nx
import plotly.graph_objects as go
import plotly.io as pio
import yaml

CONTENT_DIR = "content/researchers"


def load_researcher_files(content_dir):
    data = []
    for fname in os.listdir(content_dir):
        if fname.endswith(".md") or fname.endswith(".yaml"):
            with open(os.path.join(content_dir, fname), "r") as f:
                raw = f.read().split("---")
                if len(raw) >= 3:
                    frontmatter = raw[1]
                    parsed = yaml.safe_load(frontmatter)
                    data.append(parsed)
    return data


researchers = load_researcher_files(CONTENT_DIR)

# Build coauthor graph
G = nx.Graph()

for r in researchers:
    for work in r.get("recent_works", []):
        authors = work.get("authors", [])
        for i, a1 in enumerate(authors):
            for a2 in authors[i + 1 :]:
                if G.has_edge(a1, a2):
                    G[a1][a2]["weight"] += 1
                else:
                    G.add_edge(a1, a2, weight=1)


def network_graph(G):
    pos = nx.spring_layout(G, k=0.3, iterations=50)

    # Edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    # Nodes
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_size.append(5 + 2 * G.degree(node))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        hoverinfo="text",
        marker=dict(showscale=False, color="skyblue", size=node_size, line_width=2),
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )
    return fig


fig = network_graph(G)

# Save as a self-contained HTML
pio.write_html(fig, "coauthors.html", full_html=True, include_plotlyjs=True)
