# Imports
import pandas as pd
import streamlit as st
from millify import prettify
import plotly.graph_objects as go
import plotly.express as px

# Imports for aggrid
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid import GridUpdateMode, DataReturnMode

# Load data
@st.experimental_singleton
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

df_GBIF = load_data("Data/Allspecies_GBIFrecords_fieldnotes_complete.csv")

# Create streamlit app
st.header('Summary about the GBIF results of all the 438 species')

st.subheader('by [Sebastián Ayala-Ruano](https://sayalaruano.github.io/)')

st.subheader('Original dataset')

# Create an interactive df with aggrid
gb = GridOptionsBuilder.from_dataframe(df_GBIF)
# enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
gb.configure_default_column(
    enablePivot=True, enableValue=True, enableRowGroup=True
)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
gb.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
gridOptions = gb.build()

response = AgGrid(
    df_GBIF,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    height=500,
    width= 900,
    fit_columns_on_grid_load=False,
    configure_side_bar=True,
)

# Download button
cs, c1 = st.columns([2, 2])

with cs:

    @st.experimental_singleton
    def convert_df(df_GBIF):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df_GBIF.to_csv().encode("utf-8")

    csv = convert_df(df_GBIF)  

    st.caption("")

    st.download_button(
        label="Download original data as CSV",
        data=csv,
        file_name="results_GBIF.csv",
        mime="text/csv",
    )

# General counts
st.subheader("General information about the records of the dataset")

n_total = len(df_GBIF)
n_fn = df_GBIF["fieldNotes"].notnull().sum()
n_or = df_GBIF["occurrenceRemarks"].notnull().sum()
n_dp = df_GBIF["dynamicProperties"].notnull().sum()
n_im = df_GBIF["image_url"].notnull().sum()
n_rc = df_GBIF["reproductiveCondition"].notnull().sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total", prettify(n_total))
col2.metric("With fieldNotes data", prettify(n_fn))
col3.metric("With occurrenceRemarks data", prettify(n_or))

col4, col5, col6 = st.columns(3)
col4.metric("With dynamicProperties data", prettify(n_dp))
col5.metric("With links to images", prettify(n_im))
col6.metric("With reproductiveCondition data", prettify(n_rc))

# Number of records by species
# Create a df with the data
names = pd.DataFrame(df_GBIF["acceptedScientificName_corr"].unique(), 
                    columns = ["acceptedScientificName_corr"])

names = names.sort_values(by=["acceptedScientificName_corr"], ignore_index=True)

df_counts = pd.DataFrame(columns=["acceptedScientificName_corr", "count"])

for i in names["acceptedScientificName_corr"]:
  count_temp = len(df_GBIF[df_GBIF["acceptedScientificName_corr"] == i])
  df_counts.loc[len(df_counts)] = [i, count_temp]

# Create dot plot of records by species
st.subheader("Number of records by species")

dotplot = px.scatter(df_counts, x="acceptedScientificName_corr", y="count", 
                 labels={"count": "Number of records",
                    "acceptedScientificName_corr": "Scientific names"
                    })
dotplot.update_xaxes(showticklabels=False) 
#plot.update_traces(textfont_size=12, textangle=0, textposition="outside", showlegend=False)
st.plotly_chart(dotplot)

# Number of records by country
# Create a df with the data
countries = pd.DataFrame(df_GBIF["Country_name"].unique(), 
                    columns = ["Country_name"])

countries = countries.sort_values(by=["Country_name"], ignore_index=True)

df_counts_c = pd.DataFrame(columns=["Country_name", "count"])

for i in countries["Country_name"]:
  count_temp = len(df_GBIF[df_GBIF["Country_name"] == i])
  df_counts_c.loc[len(df_counts_c)] = [i, count_temp]

# Create plot of records by species
st.subheader("Number of records by countries")

plot2 = go.Figure(data=[go.Pie(labels=df_counts_c["Country_name"], 
    values=df_counts_c["count"], hole=.4, textposition = "inside")])

st.plotly_chart(plot2)

# Binned latitude
# Create a df with the data
lat = df_GBIF[df_GBIF['decimalLatitude'].notnull()]["decimalLatitude"]

# Create plot of records by species
st.subheader("Histogram of binned latitude")

plot3 = px.histogram(lat, x="decimalLatitude", labels={'decimalLatitude':'Latitude'}, 
                    nbins=15, opacity=0.8)

st.plotly_chart(plot3)

# Map
# Create a df with the data
# Create plot of records by species
st.subheader("Map of distribution records")

plot4 = px.scatter_geo(df_GBIF, lat="decimalLatitude", lon="decimalLongitude", 
                    hover_name="Country_name")

st.plotly_chart(plot4)

# Clear all cached entries for functions
load_data.clear()
convert_df.clear()