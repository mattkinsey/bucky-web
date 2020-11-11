from datetime import datetime, timedelta
import io
import os
import json
import sys
import streamlit as st
import numpy as np
import pandas as pd
from urllib.request import urlopen
from readable_col_names import readable_col_names

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from tabbed_timeseries_chart import *
from tabbed_choropleth_chart import *

max_width_str = f"max-width: 98%;"
st.markdown(
    f"""
<style>
    .reportview-container .main .block-container{{
        {max_width_str}
        padding: 1rem 2rem 1rem 1rem;
    }}
    footer{{
        display: none;
    }}
    .modebar{{
        display: none;
    }}
</style>
""",
    unsafe_allow_html=True,
)


###  Get data functions
####################################################################################
@st.cache
def _get_quantiles(dir, adm_level, quantile):
    df = pd.read_csv(f"output/{dir}/adm{adm_level}_quantiles.csv")
    df = df[df["quantile"] == quantile]
    df["CODE"] = "USA"
    return df


def get_output_folders():
    folders = [name for name in os.listdir("output/") if not ".DS_Store" in name]
    # print(f"Available output folders: {folders}")
    return folders


###  Styling params
####################################################################################
map_width = 600
map_height = 600

chart_width = 1200
chart_height = 350

table_height = 600
table_width = 400
background_color = "#efeded"
line_width = 2
line_color = "slategray"
scatterdot_color = line_color
scatterdot_size = 3

html = """
  <style>
    /* 1st button */
    .stDeckGlJsonChart{
    }
    .streamlit-table.stTable{
    width: 20% !important;
    height: 40% !important;
    overflow: scroll !important;
    }
    div[data-baseweb="select"] {
        color: blue;
    }
  </style>
"""

TOOLS = "pan,reset,hover,save,box_zoom"

st.markdown(html, unsafe_allow_html=True)

### Get data
####################################################################################

col_names = list(readable_col_names.values())
output_dirs = get_output_folders()
output_select = st.sidebar.selectbox("Available output directories", output_dirs)
admin_level = st.sidebar.selectbox("Admin level", ["1", "0"])
# These columns will be included when the dashboard first opens
cols_included = st.sidebar.multiselect(
    "Columns to include in line chart", col_names, default=col_names[0:4]
)
show_choro = st.sidebar.checkbox("Show map", value=False, key=None)
show_line_chart = st.sidebar.checkbox("Show line chart", value=True, key=None)
show_error_bar = st.sidebar.checkbox("Show error bars", value=True, key=None)
upper_error_bar = st.sidebar.selectbox("Upper error bar", [0.75, 0.95])
lower_error_bar = st.sidebar.selectbox("Lower error bar", [0.05, 0.25])

df_lower = _get_quantiles(output_select, admin_level, lower_error_bar).rename(columns=readable_col_names)
df_upper = _get_quantiles(output_select, admin_level, upper_error_bar).rename(columns=readable_col_names)
df = _get_quantiles(output_select, admin_level, 0.5).rename(columns=readable_col_names)

### Generate plots & Put together layout
####################################################################################
FIPS_df = pd.read_csv("data_tables/FIPS_states.csv", dtype={"FIPS": int})

if int(admin_level) == 2:
    show_choro = False

map_height = 460

if show_choro:
    if not show_line_chart:
        map_height = 850
    if int(admin_level) == 0:
        bkh_choro = tabbed_choropleth_chart(df, cols_included, map_height)
    if int(admin_level) == 1:
        df["adm1"] = [int(x) for x in df["adm1"]]
        new_df = df.merge(FIPS_df, left_on="adm1", right_on="FIPS")
        bkh_choro = tabbed_US_choropleth_chart(new_df, cols_included, map_height)
    st.bokeh_chart(bkh_choro, use_container_width=False)

if not show_choro:
    chart_height = 900

tabs = tabbed_timeseries_chart(
    df,
    df_lower,
    df_upper,
    cols_included,
    chart_width,
    chart_height,
    line_color,
    scatterdot_size,
    TOOLS,
    show_error_bar,
)
if show_line_chart:
    layout = column(tabs, name="layout")
    st.bokeh_chart(layout, use_container_width=True)
