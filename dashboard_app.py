"""
Rwanda School Construction Survey — Interactive Dashboard
=========================================================

HOW TO RUN:
  1. Place this file in the same folder as:
       - district_facility_counts.csv
       - whosonfirst-data-admin-rw-county-polygon.shp  (and its companion files)
  2. Install dependencies:
       pip install dash plotly geopandas pandas openpyxl
  3. Run:
       python3 dashboard_app.py
  4. Open your browser at:
       http://127.0.0.1:8050
"""

import pandas as pd
import geopandas as gpd
import json
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# =============================================================
# CONFIGURATION — update paths if needed
# =============================================================
CSV_FILE = "district_facility_counts.csv"
SHP_FILE = SHP_FILE = SHP_FILE = "whosonfirst-data-admin-rw-latest/whosonfirst-data-admin-rw-county-polygon.shp"

# ========================================s=====================
# LOAD DATA
# =============================================================
df = pd.read_csv(CSV_FILE)

# Facility labels (without the "Current — " / "Planned — " prefix)
FACILITY_LABELS = [
    'Classrooms', 'Latrines', 'Kitchens', 'Sci. Labs', 'Libraries',
    'Admin Blocks', 'Staff Houses', 'WASH', 'Halls', 'Fences'
]
CURRENT_COLS = [f'Current — {l}' for l in FACILITY_LABELS]
PLANNED_COLS = [f'Planned — {l}' for l in FACILITY_LABELS]

# =============================================================
# LOAD SHAPEFILE & BUILD GEOJSON
# =============================================================
gdf = gpd.read_file(SHP_FILE)
gdf['district'] = gdf['name']   # WOF names already match CSV exactly
gdf = gdf.to_crs(epsg=4326)

# Merge facility data into geodataframe
gdf = gdf.merge(df, left_on='district', right_on='District', how='left')

# Build GeoJSON for Plotly
geojson = json.loads(gdf[['district', 'geometry']].to_json())
# Give each feature an id so Plotly can join it to the data
for i, feature in enumerate(geojson['features']):
    feature['id'] = feature['properties']['district']

# =============================================================
# COLOR SCALE
# =============================================================
COLORSCALE = [
    [0.0,  '#f0f4f8'],
    [0.01, '#c6dbef'],
    [0.25, '#9ecae1'],
    [0.5,  '#6baed6'],
    [0.75, '#2171b5'],
    [1.0,  '#084594'],
]

# =============================================================
# BUILD DASH APP
# =============================================================
app = Dash(__name__)
app.title = "Rwanda School Construction Survey"

# ── Styles ────────────────────────────────────────────────────
NAVY  = '#1C2B4A'
BLUE  = '#185fa5'
LIGHT = '#f0f4f8'
WHITE = '#ffffff'

app.layout = html.Div(style={'fontFamily': 'Segoe UI, Arial, sans-serif',
                              'background': LIGHT, 'minHeight': '100vh'}, children=[

    # ── Header ───────────────────────────────────────────────
    html.Div(style={
        'background': NAVY, 'color': WHITE,
        'padding': '18px 32px',
        'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.2)'
    }, children=[
        html.Div([
            html.H1("Rwanda District School Facilities",
                    style={'margin': 0, 'fontSize': '18px', 'fontWeight': '700'}),
            html.P("Non-MINEDUC funded construction  |  2025–2026",
                   style={'margin': '2px 0 0', 'fontSize': '12px', 'color': '#a0b0c8'}),
        ]),
        html.Span("194 schools  |  30 districts",
                  style={'background': BLUE, 'color': WHITE,
                         'fontSize': '11px', 'padding': '4px 12px',
                         'borderRadius': '20px'}),
    ]),

    # ── KPI cards ─────────────────────────────────────────────
    html.Div(id='kpi-row', style={
        'display': 'flex', 'gap': '16px', 'padding': '20px 32px 0'
    }),

    # ── Main content ──────────────────────────────────────────
    html.Div(style={'display': 'flex', 'gap': '20px', 'padding': '20px 32px 32px'}, children=[

        # ── Left sidebar ──────────────────────────────────────
        html.Div(style={'width': '240px', 'flexShrink': '0',
                        'display': 'flex', 'flexDirection': 'column', 'gap': '16px'}, children=[

            # Mode toggle
            html.Div(style={
                'background': WHITE, 'borderRadius': '10px',
                'padding': '18px', 'boxShadow': '0 1px 6px rgba(0,0,0,0.08)'
            }, children=[
                html.H3("View", style={
                    'fontSize': '12px', 'fontWeight': '700', 'color': NAVY,
                    'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                    'marginBottom': '14px', 'marginTop': 0
                }),
                dcc.RadioItems(
                    id='mode-toggle',
                    options=[
                        {'label': ' Current Construction', 'value': 'current'},
                        {'label': ' Planned (Jul 2026+)',  'value': 'planned'},
                    ],
                    value='current',
                    labelStyle={'display': 'block', 'marginBottom': '12px',
                                'fontSize': '13px', 'cursor': 'pointer',
                                'color': NAVY, 'fontWeight': '600'},
                    inputStyle={'marginRight': '8px', 'accentColor': BLUE},
                ),
            ]),

            # National total pill
            html.Div(id='stat-pill', style={
                'background': NAVY, 'color': WHITE,
                'borderRadius': '10px', 'padding': '16px',
                'textAlign': 'center',
                'boxShadow': '0 1px 6px rgba(0,0,0,0.12)'
            }),

            # Color legend
            html.Div(style={
                'background': WHITE, 'borderRadius': '10px',
                'padding': '18px', 'boxShadow': '0 1px 6px rgba(0,0,0,0.08)'
            }, children=[
                html.H3("Facility units", style={
                    'fontSize': '12px', 'fontWeight': '700', 'color': NAVY,
                    'textTransform': 'uppercase', 'letterSpacing': '0.5px',
                    'marginBottom': '12px', 'marginTop': 0
                }),
                *[html.Div(style={'display': 'flex', 'alignItems': 'center',
                                  'marginBottom': '7px', 'fontSize': '12px', 'color': '#444'}, children=[
                    html.Span(style={
                        'width': '18px', 'height': '12px', 'borderRadius': '3px',
                        'marginRight': '10px', 'flexShrink': '0',
                        'background': color,
                        'border': '1px solid #ddd' if color == '#f0f4f8' else 'none'
                    }),
                    html.Span(label)
                ]) for color, label in [
                    ('#f0f4f8', 'None'),
                    ('#c6dbef', 'Low'),
                    ('#9ecae1', 'Medium-low'),
                    ('#6baed6', 'Medium'),
                    ('#2171b5', 'Medium-high'),
                    ('#084594', 'High'),
                ]],
            ]),

        ]),

        # ── Map + detail panel ────────────────────────────────
        html.Div(style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'gap': '16px'}, children=[

            # Map card
            html.Div(style={
                'background': WHITE, 'borderRadius': '12px',
                'boxShadow': '0 1px 6px rgba(0,0,0,0.08)',
                'overflow': 'hidden'
            }, children=[
                dcc.Graph(id='choropleth-map',
                          config={'displayModeBar': False, 'scrollZoom': True},
                          style={'height': '540px'}),
                html.P("Hover over a district to see its facility breakdown",
                       style={'textAlign': 'center', 'fontSize': '11px',
                              'color': '#aaa', 'padding': '4px 0 8px'}),
            ]),

            # District detail panel (appears when you hover)
            html.Div(id='district-detail', style={
                'background': WHITE, 'borderRadius': '12px',
                'boxShadow': '0 1px 6px rgba(0,0,0,0.08)',
                'padding': '20px 24px',
                'display': 'none'   # hidden until hover
            }),

        ]),

    ]),

])


# =============================================================
# CALLBACKS
# =============================================================

@app.callback(
    Output('choropleth-map',  'figure'),
    Output('kpi-row',         'children'),
    Output('stat-pill',       'children'),
    Input('mode-toggle',      'value'),
)
def update_map(mode):
    """Redraws the choropleth and KPI cards when mode changes."""

    is_current  = (mode == 'current')
    total_col   = 'Total Current Units' if is_current else 'Total Planned Units'
    fac_cols    = CURRENT_COLS if is_current else PLANNED_COLS
    mode_label  = 'Current' if is_current else 'Planned (Jul 2026+)'

    z_vals      = gdf[total_col].fillna(0).tolist()
    districts   = gdf['district'].tolist()
    nat_total   = int(sum(z_vals))

    # ── Hover template ──────────────────────────────────────
    # Build custom hover text for each district
    hover_texts = []
    for _, row in gdf.iterrows():
        lines = [f"<b style='font-size:14px'>{row['district']}</b>",
                 f"<span style='color:#888'>{mode_label} construction</span>",
                 "<br>"]
        for col, label in zip(fac_cols, FACILITY_LABELS):
            val = row.get(col, 0)
            if pd.notna(val) and int(val) > 0:
                # Dot-leader style: label ... count
                dots = '.' * max(1, 22 - len(label))
                lines.append(f"{label} {dots} <b>{int(val)}</b>")
        lines.append("<br>")
        lines.append(f"<b>Total  →  {int(row[total_col] or 0)}</b>")
        hover_texts.append("<br>".join(lines))

    # ── Choropleth figure ────────────────────────────────────
    fig = go.Figure(go.Choropleth(
        geojson=geojson,
        locations=districts,
        z=z_vals,
        colorscale=COLORSCALE,
        zmin=0,
        zmax=max(z_vals) if max(z_vals) > 0 else 1,
        marker_line_color='white',
        marker_line_width=1.2,
        showscale=False,
        hovertext=hover_texts,
        hovertemplate='%{hovertext}<extra></extra>',
    ))

    fig.update_geos(
        fitbounds='locations',
        visible=False,           # hide ocean, other countries, graticule
        showland=False,
        showocean=False,
        showlakes=False,
        showrivers=False,
        showcountries=False,
        showcoastlines=False,
        showframe=False,
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        geo=dict(bgcolor=WHITE),
        hoverlabel=dict(
            bgcolor=WHITE,
            bordercolor='#ddd',
            font=dict(family='Segoe UI, Arial', size=12, color=NAVY),
        ),
    )

    # ── KPI cards ────────────────────────────────────────────
    kpi_data = [
        (str(sum((gdf['Total Current Units'] > 0).astype(int)
                  if is_current else
                  (gdf['Total Planned Units'] > 0).astype(int))),
         f'Districts with {mode_label.lower()} construction'),
        (f"{int(gdf[fac_cols[0]].sum(skipna=True)):,}",
         'Classrooms ' + ('built/building' if is_current else 'planned')),
        (f"{int(gdf[fac_cols[1]].sum(skipna=True)):,}",
         'Latrines ' + ('built/building' if is_current else 'planned')),
        (f"{nat_total:,}",
         f'Total facility units — {mode_label.lower()}'),
    ]

    kpi_cards = [
        html.Div(style={
            'background': WHITE, 'borderRadius': '10px',
            'padding': '16px 20px', 'flex': '1',
            'boxShadow': '0 1px 6px rgba(0,0,0,0.08)',
            'borderLeft': f'4px solid {BLUE}'
        }, children=[
            html.Span(num, style={
                'fontSize': '28px', 'fontWeight': '700',
                'color': NAVY, 'display': 'block'
            }),
            html.Span(lbl, style={
                'fontSize': '11px', 'color': '#888',
                'marginTop': '2px', 'display': 'block'
            }),
        ]) for num, lbl in kpi_data
    ]

    # ── Stat pill ─────────────────────────────────────────────
    stat_pill = [
        html.Span(f"{nat_total:,}", style={
            'fontSize': '30px', 'fontWeight': '700', 'display': 'block'
        }),
        html.Span(f"facility units nationally", style={
            'fontSize': '11px', 'color': '#a0b0c8',
            'marginTop': '2px', 'display': 'block'
        }),
        html.Span(f"({mode_label})", style={
            'fontSize': '10px', 'color': '#6080a0', 'display': 'block'
        }),
    ]

    return fig, kpi_cards, stat_pill


# =============================================================
# RUN
# =============================================================
if __name__ == '__main__':
    print("""
    ✓ Dashboard starting...
    Open your browser at:  http://127.0.0.1:8050
    Press Ctrl+C to stop.
    """)
    app.run(debug=False, port=8050)
