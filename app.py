import streamlit as st
import osmnx as ox
import networkx as nx
import folium
from streamlit_folium import st_folium
import pandas as pd
from folium.plugins import MarkerCluster

st.set_page_config(page_title="Cartographie des flux pendulaires", layout="wide")

st.title("Visualisation des flux domicile-travail")

st.markdown("""
Ce travail entre dans le scope du projet I-Maroc. Cette application vous permet de visualiser les flux domicile-travail sur un graphe routier OpenStreetMap.
Choisissez une ville ou une zone géographique, et la carte vous montrera les principaux trajets et intersections. Cette application est en cours de développement.
""")

# Choix du thème
with st.sidebar:
    theme = st.radio("Choisir le thème :", ["Clair", "Sombre"])
    st.markdown("---")
    city_name = st.text_input("Nom de la ville (ex: Paris, France)", value="Paris, France")
    distance = st.slider("Rayon autour du centre (en mètres)", min_value=500, max_value=5000, value=1000, step=500)
    st.markdown("---")
    show_nodes = st.checkbox("Afficher les noeuds importants", value=True)

if theme == "Sombre":
    tiles = "CartoDB dark_matter"
else:
    tiles = "OpenStreetMap"

@st.cache_resource
def load_graph(city, dist):
    center = ox.geocode(city)
    G = ox.graph_from_point(center, dist=dist, network_type='drive')
    G = G.to_undirected()
    return G, center

G, center = load_graph(city_name, distance)

st.success(f"Graphe chargé avec {len(G.nodes)} noeuds et {len(G.edges)} arêtes.")

# Exemple de calcul de flux (simplifié)

def compute_flows(G):
    degree = dict(G.degree())
    sorted_nodes = sorted(degree.items(), key=lambda x: x[1], reverse=True)
    top_nodes = [n for n, d in sorted_nodes[:10]]
    flows = []
    for i in range(len(top_nodes)):
        for j in range(i + 1, len(top_nodes)):
            try:
                path = nx.shortest_path(G, source=top_nodes[i], target=top_nodes[j], weight='length')
                flows.append((top_nodes[i], top_nodes[j], path))
            except Exception:
                continue
    return flows

flows = compute_flows(G)

# Affichage carte
m = folium.Map(location=center, zoom_start=14, tiles=tiles)

if show_nodes:
    for node in list(dict(G.degree()).keys())[:50]:
        x, y = G.nodes[node]['x'], G.nodes[node]['y']
        folium.CircleMarker([y, x], radius=2, color='blue', fill=True).add_to(m)

for src, tgt, path in flows:
    points = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in path]
    folium.PolyLine(points, color='red', weight=2).add_to(m)

st_data = st_folium(m, width=1000, height=600)

st.markdown("---")
st.markdown("**Note** : Les flux sont calculés à partir des 10 noeuds les plus connectés sur le graphe. Vous pouvez étendre cette logique pour y insérer vos propres données de mobilité réelle.")
