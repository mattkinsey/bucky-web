import json
import pandas as pd

from bokeh.plotting import figure
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Panel, Tabs, Band


def style_plots(fig, chart_width):
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
    fig.yaxis.minor_tick_line_color = "slategray"
    fig.xaxis.minor_tick_line_color = "slategray"
    fig.yaxis.axis_line_color = "slategray"
    fig.xaxis.axis_line_color = "slategray"
    fig.xaxis.major_label_text_font_size = "8pt"
    fig.yaxis.major_label_text_font_size = "8pt"
    fig.width = chart_width
    return fig


def tabbed_timeseries_chart(
    df,
    df_05,
    df_95,
    tab_column_names,
    chart_width,
    chart_height,
    line_color,
    scatterdot_size,
    TOOLS,
    show_error,
):
    tabs_list = []

    for col in tab_column_names:
        TOOLTIPS = [("region", "@rgn_text")]
        p = figure(
            plot_width=chart_width,
            plot_height=chart_height,
            x_axis_type="datetime",
            tools=TOOLS,
            toolbar_location="left",
            tooltips=TOOLTIPS,
        )
        adm_colname = df.columns[0]
        for adm_region in df.iloc[:, 0].unique():
            df_sub_region = df[df[adm_colname] == adm_region]
            df_sub_region_05 = df_05[df_05[adm_colname] == adm_region]
            df_sub_region_95 = df_95[df_95[adm_colname] == adm_region]
            dt = [pd.to_datetime(x) for x in df_sub_region["date"]]
            source = ColumnDataSource(
                data=dict(
                    x=dt,
                    y=df_sub_region[col],
                    rgn_text=df_sub_region[adm_colname],
                    lower=df_sub_region_05[col],
                    upper=df_sub_region_95[col],
                )
            )
            p.scatter(
                "x",
                "y",
                source=source,
                size=scatterdot_size,
                fill_alpha=1,
                line_alpha=1,
                fill_color=line_color,
                line_color=line_color,
            )
            p.line(
                "x",
                "y",
                source=ColumnDataSource(
                    data=dict(
                        x=dt, y=df_sub_region[col], rgn_text=df_sub_region[adm_colname]
                    )
                ),
                line_alpha=1,
                line_color=line_color,
            )
            if show_error:
                band = Band(
                    base="x",
                    lower="lower",
                    upper="upper",
                    source=source,
                    level="underlay",
                    fill_alpha=0.7,
                    fill_color="#f0f2f6",
                    line_width=0.5,
                    line_color=line_color,
                )
                p.add_layout(band)
        p = style_plots(p, chart_width)
        tab = Panel(child=p, title=col)
        tabs_list.append(tab)

    tabs = Tabs(tabs=tabs_list)
    return tabs
