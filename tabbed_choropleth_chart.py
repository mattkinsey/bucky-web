import json
import geopandas as gpd

from bokeh.plotting import figure
from bokeh.models.glyphs import Patches
from bokeh.models import Panel, Tabs, GeoJSONDataSource, LinearColorMapper, ColorBar


def style_plots(fig, chart_height=480, ratio=650 / 380):
    chart_width = round(chart_height * ratio)
    fig.background_fill_color = None
    fig.border_fill_color = None
    fig.toolbar.logo = None
    fig.outline_line_color = None
    fig.title.text_font_size = "9pt"
    fig.title.text_font_style = "bold"
    fig.yaxis.major_label_text_color = "slategray"
    fig.xaxis.major_label_text_color = "slategray"
    fig.yaxis.major_tick_line_color = "slategray"
    fig.xaxis.major_tick_line_color = "slategray"
    fig.yaxis.axis_line_color = "slategray"
    fig.xaxis.axis_line_color = "slategray"
    fig.xaxis.major_label_text_font_size = "8pt"
    fig.yaxis.major_label_text_font_size = "8pt"
    fig.width = chart_width
    fig.height = chart_height
    return fig


def get_geodatasource(gdf):
    """Get getjsondatasource from geopandas object"""
    json_data = json.dumps(json.loads(gdf.to_json()))
    return GeoJSONDataSource(geojson=json_data)


def bokeh_plot_map(gdf, column=None, height=480):
    """Plot bokeh map from GeoJSONDataSource"""
    geosource = get_geodatasource(gdf)
    palette = [
        "#e2e5e8",
        "#d4d8dd",
        "#c5ccd2",
        "#b7bfc7",
        "#a9b2bc",
        "#9aa6b1",
        "#8c99a6",
    ]

    vals = gdf[column]

    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette=palette, low=vals.min(), high=vals.max())
    color_bar = ColorBar(
        color_mapper=color_mapper,
        label_standoff=15,
        width=15,
        height=height - 50,
        orientation="vertical",
        location=(0, 0),
    )
    p = figure(
        title="",
        toolbar_location="left",
    )
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.yaxis.visible = False
    p.xaxis.visible = False

    # Add patch renderer to figure
    p.patches(
        "xs",
        "ys",
        source=geosource,
        fill_alpha=1,
        line_width=1,
        line_color="white",
        fill_color={"field": column, "transform": color_mapper},
    )

    # Specify figure layout.
    p.add_layout(color_bar, "left")
    return p


def bokeh_US_state_choropleth(df, colname, chart_height):
    shapefile = "data_tables/geo_data/ne_110m_admin_1_states_provinces_lakes/ne_110m_admin_1_states_provinces_lakes.shp"

    # Read shapefile using Geopandas
    gdf = gpd.read_file(shapefile)[["name", "geometry", "postal"]]
    merged = gdf.merge(df, left_on="name", right_on="State", how="left")
    p = bokeh_plot_map(merged, colname, chart_height)
    return p


def tabbed_US_choropleth_chart(df, tab_column_names, chart_height):
    tabs_list = []
    ratio = 650 / 380
    for col in tab_column_names:
        p = figure()
        adm_colname = df.columns[0]
        p = bokeh_US_state_choropleth(df, col, chart_height)
        p = style_plots(p, chart_height, ratio)
        tab = Panel(child=p, title=col)
        tabs_list.append(tab)

    tabs = Tabs(tabs=tabs_list)
    return tabs


def bokeh_choropleth(df, colname, chart_height):
    shapefile = "data_tables/geo_data/countries_110m/ne_110m_admin_0_countries.shp"
    # Read shapefile using Geopandas
    gdf = gpd.read_file(shapefile)[["ADMIN", "ADM0_A3", "geometry"]]
    # Rename columns.
    gdf.columns = ["country", "country_code", "geometry"]
    gdf = gdf.drop(gdf.index[159])
    merged = gdf.merge(df, left_on="country_code", right_on="CODE", how="left")
    merged = merged.fillna(0)
    p = bokeh_plot_map(merged, colname, chart_height)
    return p


def tabbed_choropleth_chart(df, tab_column_names, chart_height):
    tabs_list = []
    ratio = 750 / 320
    for col in tab_column_names:
        p = figure(plot_height=chart_height)
        adm_colname = df.columns[0]
        p = bokeh_choropleth(df, col, chart_height)
        p = style_plots(p, chart_height, ratio)
        tab = Panel(child=p, title=col)
        tabs_list.append(tab)

    tabs = Tabs(tabs=tabs_list)
    return tabs
