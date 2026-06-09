import pandas as pd
from dash import Dash, html, dcc, Input, Output
from dash.dash import no_update
import locale
locale.setlocale(locale.LC_TIME, 'Spanish_Colombia.1252')
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# ARCHIVO
# =====================================================

RUTA = r"C:\Users\NOOSDOMINGUE\Documents\Unidades contenidas\Unidades_Dias.xlsx"

# =====================================================
# COLORES
# =====================================================

GREEN_DARK = "#046A38"
GREEN_LIGHT = "#8ED12F"
GREEN_BG = "#F4F6F4"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#163300"


# =====================================================
# LEER ARCHIVO
# =====================================================

try:

    df = pd.read_excel(
        RUTA,
        engine="openpyxl"
    )

except:

    try:

        df = pd.read_excel(
            RUTA,
            engine="xlrd"
        )

    except:

        df = pd.read_csv(
            RUTA,
            encoding="latin1"
        )
# =====================================================
# LIMPIAR COLUMNAS
# =====================================================

df.columns = df.columns.str.strip()

# =====================================================
# RECONSTRUIR DATASET
# =====================================================

dataframes = []

# A-B-C luego E-F-G luego I-J-K ...

for i in range(0, len(df.columns), 4):

    try:

        fecha = df.iloc[:, i]

        regional = df.iloc[:, i + 1]

        unidades = df.iloc[:, i + 2]

        temp = pd.DataFrame({

            "FECHA": fecha,
            "REGIONAL": regional,
            "UNIDADES": unidades

        })

        temp = temp.dropna(
            subset=[
                "FECHA",
                "REGIONAL",
                "UNIDADES"
            ]
        )

        dataframes.append(temp)

    except:
        pass

# =====================================================
# UNIR TODO
# =====================================================

df = pd.concat(
    dataframes,
    ignore_index=True
)

# =====================================================
# LIMPIAR FECHA
# =====================================================

df["FECHA"] = pd.to_datetime(
    df["FECHA"],
    dayfirst=True,
    errors="coerce"
)

df = df.dropna(
    subset=["FECHA"]
)

# =====================================================
# LIMPIAR UNIDADES
# =====================================================

df["UNIDADES"] = pd.to_numeric(
    df["UNIDADES"],
    errors="coerce"
)

df = df.dropna(
    subset=["UNIDADES"]
)

# =====================================================
# LIMPIAR REGION
# =====================================================

df["REGIONAL"] = (
    df["REGIONAL"]
    .astype(str)
    .str.strip()
)

# =====================================================
# VARIABLES
# =====================================================

col_fecha = "FECHA"
col_region = "REGIONAL"
col_unidades = "UNIDADES"
# =====================================================
# LIMPIAR FECHA
# =====================================================

df["FECHA"] = pd.to_datetime(
    df["FECHA"],
    dayfirst=True,
    errors="coerce"
)

df = df.dropna(
    subset=["FECHA"]
)

# =====================================================
# AÑO
# =====================================================

anio = int(
    df[col_fecha].dt.year.mode()[0]
)

# =====================================================
# SEMANAS PERSONALIZADAS
# =====================================================

inicio_anio = pd.Timestamp(
    year=anio,
    month=1,
    day=1
)

primer_domingo = pd.Timestamp(
    year=anio,
    month=1,
    day=4
)

primer_lunes = pd.Timestamp(
    year=anio,
    month=1,
    day=5
)

# =====================================================
# FUNCION SEMANA
# =====================================================

def calcular_semana(fecha):

    if fecha <= primer_domingo:
        return 1

    dias = (
        fecha - primer_lunes
    ).days

    return (dias // 7) + 2

## =====================================================
# ASIGNAR SEMANAS ISO
# =====================================================

df["SEMANA"] = (
    df[col_fecha]
    .dt.isocalendar()
    .week
)

# =====================================================
# RANGO SEMANAS
# =====================================================

rangos = []

for semana in sorted(df["SEMANA"].unique()):

    temp = df[
        df["SEMANA"] == semana
    ]

    inicio_sem = temp[col_fecha].min()

    fin_sem = temp[col_fecha].max()

    rangos.append({

        "SEMANA": semana,
        "INICIO_SEMANA": inicio_sem,
        "FIN_SEMANA": fin_sem

    })

df_rangos = pd.DataFrame(rangos)

# =====================================================
# MERGE RANGOS
# =====================================================

df = df.merge(
    df_rangos,
    on="SEMANA",
    how="left"
)

# =====================================================
# MES REAL
# =====================================================

df["NUM_MES"] = df[col_fecha].dt.month

mapa_meses = {

    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"

}

df["MES"] = df["NUM_MES"].map(mapa_meses)


# =====================================================
# DIA EN ESPAÑOL
# =====================================================

dias_es = {

    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"

}

df["DIA"] = (
    df[col_fecha]
    .dt.dayofweek
    .map(dias_es)
)

# =====================================================
# APP
# =====================================================

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY]
)

server = app.server

# =====================================================
# FILTROS
# =====================================================

lista_meses = sorted(
    df["MES"]
    .dropna()
    .unique()
)

lista_regiones = sorted(
    df[col_region]
    .dropna()
    .unique()
)

# =====================================================
# CARD
# =====================================================

def crear_card(
    titulo,
    valor,
    subtitulo=""
):

    return dbc.Card(

        dbc.CardBody([

            html.Div(
                titulo,
                style={
                    "fontSize": "13px",
                    "fontWeight": "600",
                    "color": "#666"
                }
            ),

            html.Div(
                valor,
                style={
                    "fontSize": "24px",
                    "fontWeight": "700",
                    "color": GREEN_DARK,
                    "marginTop": "8px"
                }
            ),

            html.Div(
                subtitulo,
                style={
                    "fontSize": "12px",
                    "color": "#777",
                    "marginTop": "6px"
                }
            )

        ]),

        style={
            "borderRadius": "18px",
            "border": f"1px solid {GREEN_LIGHT}",
            "backgroundColor": CARD_BG,
            "padding": "10px"
        }

    )

# =====================================================
# LAYOUT
# =====================================================

app.layout = dbc.Container([

   dbc.Row([

    dbc.Col([

        html.H1(
            "Dashboard - unidades Operación Logística",
            style={
                "color": GREEN_DARK,
                "fontWeight": "700",
                "marginBottom": "25px"
            }
        )

    ], width=10),

    dbc.Col([

        html.Img(

            src="/assets/logo.png",

            style={

                "width": "220px",

                # =========================
                # MOVER IZQUIERDA / DERECHA
                # =========================
                "marginLeft": "0px",

                # =========================
                # MOVER ARRIBA / ABAJO
                # =========================
                "marginTop": "0px",

                # =========================
                # OPCIONAL
                # =========================
                "float": "right"

            }

        )

    ], width=2)

]),

    dbc.Card([

        dbc.CardBody([

            dbc.Row([

                dbc.Col([

                    html.Label("Mes"),

                    dcc.Dropdown(
                        id="filtro-mes",
                        options=[
                            {
                                "label": x,
                                "value": x
                            }
                            for x in lista_meses
                        ],
                        multi=True
                    )

                ]),

                dbc.Col([

                    html.Label("Semana"),

                    dcc.Dropdown(
                        id="filtro-semana",
                        multi=True
                    )

                ]),

                dbc.Col([

                    html.Label("Regional"),

                    dcc.Dropdown(
                        id="filtro-region",
                        options=[
                            {
                                "label": x,
                                "value": x
                            }
                            for x in lista_regiones
                        ],
                        multi=True
                    )

                ])

            ])

        ])

    ],

    style={
        "marginBottom": "25px",
        "borderRadius": "20px"
    }),

    dbc.Row(
        id="contenedor-kpis",
        className="mb-4"
    ),

    dbc.Row([

        dbc.Col([

            dbc.Card([

                dbc.CardBody([

                    dcc.Graph(
                        id="grafico-linea"
                    )

                ])

            ])

        ], width=8),

        dbc.Col([

            dbc.Card([

                dbc.CardBody([

                    dcc.Graph(
                        id="grafico-region"
                    )

                ])

            ])

        ], width=4)

    ]),

   
],

fluid=True,

style={
    "backgroundColor": GREEN_BG,
    "padding": "20px",
    "minHeight": "100vh"
})

# =====================================================
# SEMANAS DINAMICAS
# =====================================================

@app.callback(
    Output("filtro-semana", "options"),
    Input("filtro-mes", "value")
)

def actualizar_semanas(meses_sel):

    dff = df.copy()

    if meses_sel:

        dff = dff[
            dff["MES"].isin(meses_sel)
        ]

    semanas = sorted(
        dff["SEMANA"]
        .unique()
    )

    opciones = []

    for semana in semanas:

        fila = df_rangos[
            df_rangos["SEMANA"] == semana
        ]

        ini = fila["INICIO_SEMANA"].iloc[0]
        fin = fila["FIN_SEMANA"].iloc[0]

        opciones.append({

            "label": (
                f"Semana {semana} | "
                f"{ini.strftime('%d %b')} "
                f"a "
                f"{fin.strftime('%d %b')}"
            ),

            "value": semana

        })

    return opciones

# =====================================================
# CALLBACK
# =====================================================

@app.callback(

    Output("grafico-linea", "figure"),
    Output("grafico-region", "figure"),
    Output("contenedor-kpis", "children"),

    Input("filtro-mes", "value"),
    Input("filtro-semana", "value"),
    Input("filtro-region", "value")

)

def update_dashboard(
    meses_sel,
    semanas_sel,
    regiones_sel
):

    dff = df.copy()

   

 

    # -----------------------------
    # FILTRO SEMANA
    # -----------------------------

    if semanas_sel:

        dff = dff[
            dff["SEMANA"].isin(semanas_sel)
        ]

    # -----------------------------
    # FILTRO MES
    # SOLO SI NO HAY SEMANA
    # -----------------------------

    elif meses_sel:

        dff = dff[
            dff["MES"].isin(meses_sel)
        ]

    # -----------------------------
    # FILTRO REGION
    # -----------------------------

    if regiones_sel:

        dff = dff[
            dff[col_region].isin(regiones_sel)
        ]
    # =================================================
    # KPIS
    # =================================================

    total = int(
        dff[col_unidades].sum()
    )

    region_top = (
        dff.groupby(col_region)[col_unidades]
        .sum()
        .idxmax()
    )

    # =================================================
    # DIAS VALIDOS
    # =================================================

    dias = (

        dff.groupby(col_fecha)[col_unidades]
        .sum()
        .reset_index()

    )

    dias = dias[
        dias[col_unidades] > 0
    ]

    dia_max = dias.loc[
        dias[col_unidades].idxmax()
    ]

    dia_min = dias.loc[
        dias[col_unidades].idxmin()
    ]

    # =================================================
    # CARDS
    # =================================================

    kpis = [

        dbc.Col(
            crear_card(
                "Total Unidades",
                f"{total:,.0f}"
            )
        ),

        dbc.Col(
            crear_card(
                "Mejor Región",
                str(region_top)
            )
        )

    ]

    # =================================================
    # MOSTRAR KPI SEMANAS
    # =================================================

    mostrar_semanas = (
        semanas_sel is None or
        len(semanas_sel) == 0
    )

    if mostrar_semanas:

        semana_stats = (

            dff.groupby("SEMANA")[col_unidades]
            .sum()

        )

        semana_max = int(
            semana_stats.idxmax()
        )

        semana_min = int(
            semana_stats.idxmin()
        )

        fila_max = df_rangos[
            df_rangos["SEMANA"] == semana_max
        ]

        fila_min = df_rangos[
            df_rangos["SEMANA"] == semana_min
        ]

        ini_max = fila_max["INICIO_SEMANA"].iloc[0]
        fin_max = fila_max["FIN_SEMANA"].iloc[0]

        ini_min = fila_min["INICIO_SEMANA"].iloc[0]
        fin_min = fila_min["FIN_SEMANA"].iloc[0]

        kpis.extend([

            dbc.Col(
                crear_card(
                    "Semana Más Alta",
                    f"Semana {semana_max}",
                    (
                        f"{ini_max.strftime('%d %b')} "
                        f"a "
                        f"{fin_max.strftime('%d %b')}"
                    )
                )
            ),

            dbc.Col(
                crear_card(
                    "Semana Más Baja",
                    f"Semana {semana_min}",
                    (
                        f"{ini_min.strftime('%d %b')} "
                        f"a "
                        f"{fin_min.strftime('%d %b')}"
                    )
                )
            )

        ])

    # =================================================
    # KPI DIAS
    # =================================================

    # =================================================
    # TOTAL SEMANA FILTRADA
    # =================================================

    if semanas_sel and len(semanas_sel) > 0:

        total_semana = int(
            dff[col_unidades].sum()
        )

        kpis.append(

            dbc.Col(
                crear_card(
                    "Total Semana",
                    f"{total_semana:,.0f}"
                )
            )

        )

    # =================================================
    # LINEA
    # =================================================

    linea = (

        dff.groupby(
            [col_fecha, col_region, "DIA"]
        )[col_unidades]

        .sum()
        .reset_index()

    )

    fig_linea = px.line(

        linea,

        x=col_fecha,
        y=col_unidades,
        color=col_region,
        markers=True,

        custom_data=["DIA"]

    )

    fig_linea.update_layout(

    title="Tendencia Diaria",

    paper_bgcolor="white",
    plot_bgcolor="white",

    height=500,

    hovermode="x unified",

    hoverlabel=dict(

        font_size=22,
        font_family="Arial"

    )

)

    fig_linea.update_traces(

        hovertemplate=

        "<b>Regional:</b> %{fullData.name}<br>" +

        "<b>Día:</b> %{customdata[0]}<br>" +

        "<b>Fecha:</b> %{x|%d/%m/%Y}<br>" +

        "<b>Unidades:</b> %{y:,.0f} unds<extra></extra>"

    )

    fig_linea.update_xaxes(

    tickformat="%d %b",

    rangebreaks=[

        dict(bounds=["sun", "mon"])

    ]

)
    # =================================================
    # REGION
    # =================================================

    region_chart = (

        dff.groupby(col_region)[col_unidades]

        .sum()
        .reset_index()

        .sort_values(
            by=col_unidades,
            ascending=False
        )

    )

    fig_region = px.bar(

        region_chart,

        x=col_unidades,
        y=col_region,

        orientation="h",

        color=col_unidades,

        color_continuous_scale=[
            GREEN_LIGHT,
            GREEN_DARK
        ]

    )

    fig_region.update_layout(

    title="Ranking Regional",

    paper_bgcolor="white",
    plot_bgcolor="white",

    height=500,

    coloraxis_showscale=False,

    hoverlabel=dict(

        font_size=22

    )

)

    return (

        fig_linea,
        fig_region,
        kpis

    )

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=8050
    )
