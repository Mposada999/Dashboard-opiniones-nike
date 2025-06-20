import pandas as pd
from dash import Dash, dcc, html, Output, Input
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk import download
from collections import Counter
from pyngrok import ngrok
import warnings
warnings.filterwarnings("ignore")

# --- DESCARGAR STOPWORDS ---
download("stopwords")
stop_words = set(stopwords.words("spanish"))

# --- CARGAR Y LIMPIAR DATOS ---
df = pd.read_csv("OPINIONES_NIKE_CORREGIDO.csv", sep=";", encoding="latin1")
df.columns = ["Opinión", "Comentario", "Sentimiento"]

df["Comentario"] = df["Comentario"].astype(str).str.lower().str.replace('"', '').str.strip()
df["Sentimiento"] = df["Sentimiento"].astype(str).str.capitalize().str.strip()

# --- DASH APP ---
app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Análisis de Opiniones - Nike", style={'textAlign': 'center'}),

    dcc.Dropdown(
        id="filtro-sentimiento",
        options=[{"label": s, "value": s} for s in df["Sentimiento"].unique()] + [{"label": "Todos", "value": "Todos"}],
        value="Todos",
        style={'width': '50%', 'margin': '0 auto'}
    ),

    dcc.Graph(id="grafico-torta"),
    dcc.Graph(id="grafico-barras"),
    dcc.Graph(id="grafico-nube")
])

# --- CALLBACK: TORTA ---
@app.callback(
    Output("grafico-torta", "figure"),
    Input("filtro-sentimiento", "value")
)
def actualizar_grafico_torta(sentimiento):
    datos = df if sentimiento == "Todos" else df[df["Sentimiento"] == sentimiento]
    conteo = datos["Sentimiento"].value_counts().reset_index()
    conteo.columns = ["Sentimiento", "Cantidad"]
    fig = px.pie(conteo, values="Cantidad", names="Sentimiento", title="Distribución de Sentimientos (%)", hole=0.3)
    return fig

# --- CALLBACK: BARRAS ---
@app.callback(
    Output("grafico-barras", "figure"),
    Input("filtro-sentimiento", "value")
)
def actualizar_barras(sentimiento):
    datos = df if sentimiento == "Todos" else df[df["Sentimiento"] == sentimiento]
    palabras = " ".join(datos["Comentario"]).split()
    palabras_filtradas = [w for w in palabras if w not in stop_words]
    top_palabras = Counter(palabras_filtradas).most_common(10)
    palabras, conteos = zip(*top_palabras)
    fig = px.bar(x=conteos, y=palabras, orientation='h',
                 labels={'x': 'Frecuencia', 'y': 'Palabra'},
                 title='Top 10 Palabras Más Comunes')
    return fig

# --- CALLBACK: NUBE DE PALABRAS ---
@app.callback(
    Output("grafico-nube", "figure"),
    Input("filtro-sentimiento", "value")
)
def actualizar_nube(sentimiento):
    datos = df if sentimiento == "Todos" else df[df["Sentimiento"] == sentimiento]
    palabras = " ".join(datos["Comentario"]).split()
    palabras_filtradas = [w for w in palabras if w not in stop_words]
    frecuencias = Counter(palabras_filtradas)
    nube = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(frecuencias)
    fig = go.Figure()
    fig.add_layout_image(
        dict(
            source=nube.to_image(),
            x=0, y=1, sizex=1, sizey=1,
            xref="paper", yref="paper",
            xanchor="left", yanchor="top",
            layer="below"
        )
    )
    fig.update_layout(title="Nube de Palabras", xaxis_visible=False, yaxis_visible=False)
    return fig
    
server = app.server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
