"""
Names: Ryan Hewes and Caleb Martin
CS230: Section SN6
Data: volcanoes.csv
URL: https://share.streamlit.io/ryanthewes/final_project/main/final_revised.py

Description: The map shows a map of all of the volcano eruptions and can be sorted by how recently they have
             erupted. This is a good way to see what volcanoes may erupt in the near future. The charts show
             metrics about volcanoes and the user can change how to data is displayed. Finally, the raw data option
             shows the volcanoes.csv file to the user.

"""

import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st
from flexidate import parse

st.set_page_config(layout="wide")

def load_data():
    data = pd.read_csv("volcanoes.csv").dropna()
    return data


# Function that lets the user change charts
def chart_user_input(index):
    st.header("Chart Options")
    option_1, option_2, option_3, option_4 = st.beta_columns(4)
    chart_color = option_1.selectbox("Select Color for Charts", ["Red", "Green", "Yellow", "Orange", "Blue", "Purple"], key=index)
    transparency = option_2.slider("Select Graph Transparency", 0.0, 1.0, .5, key=index)
    chart_grid = option_3.checkbox("Do you want your chart to have a grid?", key=index)
    label_sizes = option_4.checkbox("Would you like to change the font size of the labels?", key=index)
    if label_sizes == True:
        chosen_size = option_4.selectbox("Select a size", ["10", "12", "14"], key=index)
    else:
        chosen_size = "10"

    return transparency, chart_grid, chart_color, label_sizes, chosen_size

# Chart options specifically for pie chart
def pie_options(index):

    st.header("Pie Chart Options")
    option_1, option_2 = st.beta_columns(2)
    explode_amount = option_1.selectbox("Select Distance Between Pieces", [0, 0.1, 0.2, 0.3], key=index)
    explode_amount_used = []
    if explode_amount == 0:
        explode_amount_used = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    elif explode_amount == 0.1:
        explode_amount_used = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    elif explode_amount == 0.2:
        explode_amount_used = [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]
    elif explode_amount == 0.3:
        explode_amount_used = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]

    shadow_select = option_2.checkbox("Do you want your chart to have a shadow?", key=index)


    return explode_amount_used, shadow_select

# Loading the charts that we made
def load_charts():
    st.header("Check out These Charts!")
    index = 0
    data = load_data()

    # Pie Chart of Volcanoes by Region
    explode_amount_used, shadow_select = pie_options(index)
    tectonic_setting_count = data["Tectonic Setting"].value_counts()
    tectonic_labels = ["Subduction zone / Continental crust (>25 km)", "Intraplate / Continental crust (>25 km)",
                       "Subduction zone / Oceanic crust (< 15 km)", "Rift zone / Oceanic crust (< 15 km)",
                       "Rift zone / Continental crust (>25 km)", "Subduction zone / Crustal thickness unknown",
                       "Subduction zone / Intermediate crust (15-25 km)", "Rift zone / Intermediate crust (15-25 km)",
                       "Intraplate / Oceanic crust (< 15 km)", "Intraplate / Intermediate crust (15-25 km)",
                       "Unknown"]
    plt.pie(tectonic_setting_count, explode=explode_amount_used, shadow=shadow_select)
    plt.legend(tectonic_labels, prop={'size': 3}, loc=2)

    plt.title("Pie Chart by Tectonic Setting")
    st.pyplot(plt)
    plt.clf()
    index += 1

    # Horizontal bar chart of volcano count by region
    transparency, chart_grid, chart_color, label_sizes, chosen_size = chart_user_input(index)

    regions = data["Region"].unique()
    region_count = data["Region"].value_counts()
    plt.barh(regions, region_count, align='edge', alpha=transparency, color=chart_color)
    if chart_grid == True:
        plt.grid()
    plt.xlabel("Count", size=chosen_size)
    plt.ylabel("Region", size=chosen_size)
    plt.title("Number of Volcanoes by Region", size=chosen_size)
    st.pyplot(plt)
    plt.clf()
    index += 1

    # Histogram of most recent eruptions
    # Adding the options for the graph again
    transparency, chart_grid, chart_color, label_sizes, chosen_size = chart_user_input(index)

    years=[]
    for z, x in enumerate(data["Last Known Eruption"]):
        if "BCE" in x:
            x = -int(x.split(" ")[0])
        elif "CE" in x:
            x = int(x.split(" ")[0])
        elif x == "Unknown":
            continue
        years.append(x)
    plt.hist(years, bins=20,color=chart_color, alpha=transparency)
    if chart_grid == True:
        plt.grid()

    plt.ylabel("Number of Volcanos", size=chosen_size)
    plt.xlabel("Year of Last Eruption", size=chosen_size)
    plt.title(f"Distribution of Last Eruptions", size=chosen_size)
    st.pyplot(plt)
    plt.clf()
    index += 1

#Reads in data for map and removes BC from the eruption dates and makes them negative

data = pd.read_csv("volcanoes.csv")
x = parse("1892 BCE")
c = data.set_index("Last Known Eruption")
c = c.drop(labels="Unknown", axis=0)
dropped = c

c = c.reset_index()
c = c["Last Known Eruption"]
c = c.apply(lambda z: parse(z))
data = pd.read_csv("volcanoes.csv").dropna()

dropped = dropped.reset_index()
dropped["Last Known Eruption"] = c


df = pd.pivot_table(data, index=["Country"], aggfunc="size")


def load_maps():

    data = load_data()
    options=[]
    for x in data:
        options.append(x)
    sea_level = st.multiselect("Select data to diplay on mouse hover and on dataframe below map",options)
    volcanoes_list = ""
    for feature in sea_level:
        volcanoes_list = volcanoes_list +" "+feature+": {"+feature+"} |"
    under = data[data["Elevation (m)"]<0]
    under["elev"] = -under["Elevation (m)"]
    over = data[data["Elevation (m)"]>0]
    over["elev"] = over["Elevation (m)"]
    view=pdk.ViewState(latitude=over["Latitude"].mean(),
                       longitude=over["Longitude"].mean(),
                       pitch=30,
                       zoom=0)

    above_sea=pdk.Layer("ColumnLayer",
                  data=over,get_position=["Longitude", "Latitude"],
                  get_elevation="elev",
                  elevation_scale=100,
                  radius=10000,
                  pickable=True,
                  auto_highlight=True,
                  get_fill_color=[0, 225, 0, 225])

    below_sea=pdk.Layer("ColumnLayer",
                 data=under,
                 get_position=["Longitude", "Latitude"],
                 get_elevation="elev",
                 elevation_scale=100,
                 radius=10000,
                 pickable=True,
                 auto_highlight=True,
                 get_fill_color=[0,30,225,225])

    tooltip = {"html": volcanoes_list,"style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"}}

    map=pdk.Deck(map_provider='carto',
                 layers=[above_sea, below_sea],
                 initial_view_state=view,
                 api_keys=None,
                 tooltip=tooltip)

    st.pydeck_chart(map)
    for x in data:
        if x not in sea_level:
            data=data.drop(columns=[x])
    st.dataframe(data)



def main():
    load_data()
    st.title("The History of Volcanic Eruptions")
    st.sidebar.title("Menu Navigation:")
    menu = st.sidebar.selectbox("What Would you like to See?", ["Maps", "Charts"])
    if menu == "Maps":
        load_maps()
    if menu == "Charts":
        load_charts()



main()
