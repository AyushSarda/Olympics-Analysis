import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import f

player_data = pd.read_csv('athlete_events.csv')
noc_data = pd.read_csv('noc_regions.csv')

#Merge datasets on 'NOC' to get region names
merged_data = pd.merge(player_data, noc_data, on='NOC', how='left')
merged_data = merged_data[merged_data['Season'] == 'Summer']
merged_data.drop_duplicates(inplace=True)
merged_data['region'] = merged_data['region'].fillna("Unknown").astype(str)

st.title("Olympics Data Analysis 1896-2016")
st.sidebar.header("Choose Your Preferences")


# Filter merged_data to only include Olympic years (multiples of 4)
olympic_years = sorted(merged_data['Year'].unique())
olympic_years = [year for year in olympic_years if year % 4 == 0]

time_selection = st.sidebar.radio("Select Analysis Type", ("Year Range", "Specific Year"))

merged_data,selected_year_range = f.year_selection(merged_data, olympic_years, time_selection)



selected_countries = st.sidebar.multiselect("Select Countries", 
                                            sorted(merged_data['region'].unique()))

# Sport Selection
all_sports = ["All"] + sorted(merged_data['Sport'].unique())
selected_sport = st.sidebar.selectbox("Select Sport", all_sports)

# Gender Selection
selected_gender = st.sidebar.selectbox("Select Gender", ["Both", "M", "F"])


st.sidebar.header("Select Analysis to View")

analysis_options = [
    "Overall Analysis",
    "region-Wise Medal Comparison",
    "Year-Wise region Performance",
    "Top Athletes",
    "Compare Medal Counts for Selected Countries",
    "Heatmap of Medals by region and Year",
    
]
selected_analysis = st.sidebar.multiselect("Choose Analysis Options", analysis_options)

if "Overall Analysis" in selected_analysis:
    top_n = st.sidebar.slider("Select Top N Countries for Overall Analysis", 1, 15, 7)
    f.overall_analysis(merged_data,top_n,selected_countries,selected_sport,selected_gender)

if "region-Wise Medal Comparison" in selected_analysis:
    f.region_wise(merged_data, selected_countries,selected_sport,selected_gender)

if "Compare Medal Counts for Selected Countries" in selected_analysis:
    f.compare_medals(merged_data, selected_countries, selected_sport, selected_gender)

if "Top Athletes" in selected_analysis:
    f.top_athletes(merged_data,selected_countries,selected_sport,selected_gender)    

if "Heatmap of Medals by region and Year" in selected_analysis:
    st.subheader("Medal Count Heatmap for Selected Year(s)")

    # Generate and display the heatmap for selected year(s) and countries
    if selected_countries:
        heatmap_fig = f.display_medal_heatmap(merged_data, selected_year_range, selected_countries,selected_sport,selected_gender)
        if heatmap_fig:
            st.pyplot(heatmap_fig)
    else:
        st.warning("Please select at least one country to display the heatmap.")     

if "Year-Wise region Performance" in selected_analysis:
    st.subheader("Year-Wise Region Performance")
    
    # Generate the performance plot based on selected countries, sport, and gender
    performance_fig = f.year_wise_region_performance(merged_data, selected_countries, selected_sport, selected_gender)
    
    # Display the plot or a warning if no data is available
    if performance_fig:
        st.plotly_chart(performance_fig)
    else:
        st.warning("No data available for the selected filters.")
