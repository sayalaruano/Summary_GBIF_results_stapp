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
#@st.experimental_memo
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

df_GBIF = load_data("Data/50_species_GBIFrecords_fieldnotes.csv")

# Create streamlit app

st.header('Summary about the results of 50 species search into GBIF')

st.subheader('by [Sebastián Ayala-Ruano](https://sayalaruano.github.io/)')

st.sidebar.header('About')

st.sidebar.write('This is the exploratory data analysis of a project about phenology of species from tropical montane forests in the northwestern Pichincha in Ecuador.')

st.sidebar.header('Data')

st.sidebar.write('The dataset was retrieved from [GBIF](https://www.gbif.org/), an initiative to collect biological information and share it openly.')

st.sidebar.header('Code availability')

st.sidebar.write('The code for this project is available under the [MIT License](https://mit-license.org/) in this [GitHub repo](https://github.com/sayalaruano/Summary_GBIF_results_stapp). If you use or modify the source code of this project, please provide the proper attributions for this work.')

st.sidebar.header('Contact')

st.sidebar.write('If you have any comments or suggestions about this work, please DM by [twitter](https://twitter.com/sayalaruano) or [create an issue](https://github.com/sayalaruano/Summary_GBIF_results_stapp/issues/new) in the GitHub repository of this project.')

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

    @st.cache
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
n_lt = df_GBIF["decimalLatitude"].notnull().sum()
n_lg = df_GBIF["decimalLongitude"].notnull().sum()
n_mth = df_GBIF["month"].notnull().sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total", prettify(n_total))
col2.metric("With fieldNotes data", prettify(n_fn))
col3.metric("With occurrenceRemarks data", prettify(n_or))

col4, col5, col6 = st.columns(3)
col4.metric("With dynamicProperties data", prettify(n_dp))
col5.metric("With links to images", prettify(n_im))
col6.metric("With reproductiveCondition data", prettify(n_rc))

col7, col8, col9 = st.columns(3)
col7.metric("With Latitude data", prettify(n_lt))
col8.metric("With Longitude data", prettify(n_lg))
col9.metric("With month's date data", prettify(n_mth))

# Number of records by species
# Create a df with the data
names = pd.DataFrame(df_GBIF["acceptedScientificName_corr"].unique(), 
                    columns = ["acceptedScientificName_corr"])

names = names.sort_values(by=["acceptedScientificName_corr"], ignore_index=True)

df_counts = pd.DataFrame(columns=["acceptedScientificName_corr", "count"])

for i in names["acceptedScientificName_corr"]:
  count_temp = len(df_GBIF[df_GBIF["acceptedScientificName_corr"] == i])
  df_counts.loc[len(df_counts)] = [i, count_temp]

# Create plot of records by species
st.subheader("Number of records by species")

plot = px.bar(df_counts, y='count', x='acceptedScientificName_corr',
            text_auto='.2s', labels={
                    "count": "Number of records",
                    "acceptedScientificName_corr": "Scientific names"
                })
plot.update_traces(textfont_size=12, textangle=0, textposition="outside", showlegend=False)
st.plotly_chart(plot)

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

# Records information by species
st.subheader("Records information by species")
# Create sidebar
country = st.selectbox('Species:', df_GBIF["acceptedScientificName_corr"].unique())

# Filter data of the selected species
df_species = df_GBIF[df_GBIF["acceptedScientificName_corr"] == country]

# Calculate parameters by species
n_total_sp = len(df_species)
n_fn_sp = df_species["fieldNotes"].notnull().sum()
n_or_sp = df_species["occurrenceRemarks"].notnull().sum()
n_dp_sp = df_species["dynamicProperties"].notnull().sum()
n_im_sp = df_species["image_url"].notnull().sum()
n_rc_sp = df_species["reproductiveCondition"].notnull().sum()
n_lt_sp = df_species["decimalLatitude"].notnull().sum()
n_lg_sp = df_species["decimalLongitude"].notnull().sum()
n_mth_sp = df_species["month"].notnull().sum()

col10, col11, col12 = st.columns(3)
col10.metric("Total", prettify(n_total_sp))
col11.metric("With fieldNotes data", prettify(n_fn_sp))
col12.metric("With occurrenceRemarks data", prettify(n_or_sp))

col13, col14, col15 = st.columns(3)
col13.metric("With dynamicProperties data", prettify(n_dp_sp))
col14.metric("With links to images", prettify(n_im_sp))
col15.metric("With reproductiveCondition data", prettify(n_rc_sp))

col16, col17, col18 = st.columns(3)
col16.metric("With Latitude data", prettify(n_lt_sp))
col17.metric("With Longitude data", prettify(n_lg_sp))
col18.metric("With month's date data", prettify(n_mth_sp))

# Clear all cached entries for functions
load_data.clear()