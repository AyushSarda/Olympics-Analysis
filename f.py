import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

def year_selection(merged_data, olympic_years, time_selection):
    if time_selection == "Year Range":
        selected_year_range = st.sidebar.select_slider(
            "Select Year Range",
            options=olympic_years,
            value=(olympic_years[0], olympic_years[-1])
        )
        filtered_data = merged_data[(merged_data['Year'] >= selected_year_range[0]) & 
                                    (merged_data['Year'] <= selected_year_range[1])]
    else:
        # Specific Year Selection with multiples of 4 only
        selected_year = st.sidebar.selectbox("Select Year", olympic_years)
        filtered_data = merged_data[merged_data['Year'] == selected_year]
        selected_year_range = [selected_year]
    
    return filtered_data,selected_year_range

def overall_analysis(merged_data,top_n,countries,sports,gender):
    merged_data = merged_data.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

    if countries or sports != "All" or gender != "Both":
        st.warning("For Overall Analysis, avoid using filters like specific countries, sports, or gender. "
                   "Please use these filters in the appropriate detailed analysis sections.")
        return  # Exit the function if incompatible filters are selected
    else:
        overall_medal_counts = merged_data[merged_data['Medal'].notnull()].groupby('region')['Medal'].count().reset_index()
        overall_medal_counts.columns = ['Country', 'Total Medals']

    # Get the top N countries
        top_countries = overall_medal_counts.nlargest(top_n, 'Total Medals')

    # Calculate the 'Others' category
        others_count = overall_medal_counts[~overall_medal_counts['Country'].isin(top_countries['Country'])]['Total Medals'].sum()
        others_data = pd.DataFrame({'Country': ['Others'], 'Total Medals': [others_count]})

    # Combine top N countries with Others
        final_counts = pd.concat([top_countries, others_data], ignore_index=True)

    # Plotting the pie chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(final_counts['Total Medals'], labels=final_counts['Country'], autopct='%1.1f%%', startangle=140)
        ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.

        plt.title(f"Overall Medal Distribution by Top {top_n} Countries and Others ")
        st.pyplot(fig)
    # Grouping the filtered data to count medals by region


def region_wise(merged_data, countries,sports,gender):
    st.subheader("Region-Wise Medal Comparison")
    
    if merged_data.empty:
        st.warning("No data available for the selected filters in Region-Wise Medal Comparison.")
        return

    medal_data = merged_data[merged_data['Medal'].notnull()]

    if countries:
        medal_data = medal_data[medal_data['region'].isin(countries)]

    
    if sports != "All":
        medal_data = medal_data[medal_data['Sport'] == sports]

    # Check if there are any medals for the selected gender
    if gender != "Both":
        medal_data = medal_data[medal_data['Sex'] == gender]

    if medal_data.empty:
        st.warning("No medals found for the selected filters (countries, sport, gender) in the chosen years.")
        return
    else:
        st.write("Fitered Data")
        st.dataframe(medal_data[['Name', 'Team', 'Year', 'Sport', 'Event', 'Medal','Sex']])    

    medal_data = medal_data.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])    

    # Group by region, year, and medal type
    region_medal_data = medal_data.groupby(['region', 'Year', 'Medal']).size().unstack().fillna(0)

    # Ensure that 'Gold', 'Silver', and 'Bronze' columns are present
    region_medal_data = region_medal_data.reindex(columns=['Gold', 'Silver', 'Bronze'], fill_value=0)

    # Calculate total medals for each region and year
    region_medal_data['Total'] = region_medal_data.sum(axis=1)

    # Calculate the overall totals for each medal type and add it as a summary row
    total_row = region_medal_data.sum().to_frame().T
    total_row.index = ['Overall Total']
    region_medal_data = pd.concat([region_medal_data, total_row])
    

    # Display the medal counts in Streamlit with the summary row
    st.write("Medal Counts by Region and Year (Including Overall Totals):")
    st.write(region_medal_data)

    # Plotting the graph with separate bars for each medal type
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plotting Gold, Silver, Bronze as separate bars
    region_medal_data[['Gold', 'Silver', 'Bronze']].iloc[:-1].plot(kind='bar', stacked=False, ax=ax, color=['#FFD700', '#C0C0C0', '#CD7F32'])
    
    # Creating a secondary y-axis for the total medals
    ax_total = ax.twinx()
    region_medal_data['Total'].iloc[:-1].plot(kind='line', marker='o', color='black', ax=ax_total, label="Total")

    # Customizing the plot
    ax.set_title("Region-Wise Medal Count by Type and Total Over the Years")
    ax.set_xlabel("Region and Year")
    ax.set_ylabel("Medal Count")
    ax_total.set_ylabel("Total Medal Count")  # Secondary y-axis for total line

    # Handling the legend manually to show both bar and line plot legends
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax_total.get_legend_handles_labels()
    ax_total.legend(lines + lines2, labels + labels2, loc='upper left')

    # Display the plot in Streamlit
    st.pyplot(fig)

def compare_medals(merged_data, selected_countries, selected_sport, selected_gender):
    # Set the subheader with formatted year range
    st.subheader("Medal Comparison in Selected Year selected year(s)")
    # Drop duplicates to ensure unique medals are counted
    merged_data = merged_data.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

    # Filter by selected countries
    if not selected_countries:
        st.warning("No countries selected for comparison.")
        return

    # Filter by selected sport
    if selected_sport != "All":
        merged_data = merged_data[merged_data['Sport'] == selected_sport]

    # Filter by selected gender
    if selected_gender != "Both":
        merged_data = merged_data[merged_data['Sex'] == selected_gender]

    # Ensure selected countries are in the filtered data
    medal_data = merged_data[merged_data['region'].isin(selected_countries)]

    # Check if there are any medals for the selected countries
    if medal_data.empty:
        st.warning("No medals found for the selected countries in selected year range.")
        return
    else:
      st.dataframe(medal_data[['Name', 'Team', 'Year', 'Sport', 'Event', 'Medal']])

    # Group by country and medal type
    medal_counts = medal_data[medal_data['Medal'].notnull()].groupby(['region', 'Medal']).size().unstack(fill_value=0)
    if medal_counts.empty:
        st.warning(f"No medals found for the selected countries in selected year(s)")
        return
    else:
      st.dataframe(medal_data[['Name', 'Team', 'Year', 'Sport', 'Event', 'Medal']])

    # Convert indices to string type for proper labeling
    medal_counts.index = medal_counts.index.astype(str)

    # Add a 'Total' column for overall medal counts
    medal_counts['Total'] = medal_counts.sum(axis=1)

    # Plotting the bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    medal_counts[['Gold', 'Silver', 'Bronze']].plot(kind='bar', stacked=True, ax=ax, color=['#FFD700', '#C0C0C0', '#CD7F32'])

    # Customizing the plot
    ax.set_title(f"Medals Found for Selected Countries in selected year(s)")
    ax.set_xlabel("Countries")
    ax.set_ylabel("Medal Count")
    ax.legend(title='Medal Type', loc='upper left')

    # Display the plot in Streamlit
    st.pyplot(fig)


def display_medal_heatmap(merged_data, selected_year_range, selected_countries,selected_sport,selected_gender):
   
    
    if selected_sport != "All":
        merged_data = merged_data[merged_data['Sport'] == selected_sport]

    if selected_gender != "Both":
        merged_data = merged_data[merged_data['Sex'] == selected_gender]

    # Ensure selected countries are in the filtered data
    merged_data = merged_data[merged_data['region'].isin(selected_countries)]

    

    # Remove duplicates and count medals by region and type
    merged_data = merged_data.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    region_medal_counts = merged_data.groupby(['region', 'Medal']).size().unstack(fill_value=0)
    if region_medal_counts.empty:
        st.warning("No medals found for the selected countries in the specified time period.")
        return None
    # Plot heatmap using seaborn
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(region_medal_counts, cmap="YlOrRd", annot=True, fmt="d", ax=ax)

    # Set title based on selection

    ax.set_title(f"Medals Found for Selected Countries in {selected_year_range[0]}")
    ax.set_xlabel("Medal Type")
    ax.set_ylabel("Country/Region")

    return fig

def year_wise_region_performance(filtered_data, selected_countries, selected_sport,selected_gender):


    # Filter by selected countries if provided
    filtered_data = filtered_data.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    if selected_countries and "All" not in selected_countries:
        filtered_data = filtered_data[filtered_data['region'].isin(selected_countries)]
    
    # Additional filtering based on selected sport and gender
    if selected_sport != "All":
        filtered_data = filtered_data[filtered_data['Sport'] == selected_sport]
    if selected_gender != "Both":
        filtered_data = filtered_data[filtered_data['Sex'] == selected_gender]
    
    # Check if there’s any data after filtering
    if filtered_data.empty:
        return None  # Return None if no data is available for selected criteria
    
    # Group data by year and region, count medals, and fill missing values with 0
    year_region_medal = filtered_data.groupby(['Year', 'region'])['Medal'].count().unstack().fillna(0)

    # Convert data into long format for Plotly
    year_region_medal_long = year_region_medal.reset_index().melt(id_vars='Year', var_name='Region', value_name='Medal Count')
    
    # Plotting using Plotly Express
    fig = px.line(year_region_medal_long, x="Year", y="Medal Count", color="Region",
                  title="Year-Wise Medal Performance by Region",
                  labels={"Year": "Year", "Medal Count": "Medal Count", "Region": "Country/Region"})
    
    fig.update_traces(mode="lines+markers")

    # Customize layout for better interactivity and visibility
    fig.update_layout(
        legend_title_text="Country/Region",
        hovermode="x unified",
        legend=dict(
            title="Click to show/hide",
            font=dict(size=12),
            itemclick="toggle",  # Allows single-country analysis by toggling visibility
            itemdoubleclick="toggleothers"  # Double-click hides other countries except the selected one
        )
    )

    return fig

def top_athletes(merged_data, selected_countries, selected_sport, selected_gender):
    st.subheader("Top Athletes from selected year")

    # Filter by selected countries
    if selected_countries:
        merged_data = merged_data[merged_data['region'].isin(selected_countries)]

    # Filter by selected sport
    if selected_sport != "All":
        merged_data = merged_data[merged_data['Sport'] == selected_sport]

    # Filter by selected gender
    if selected_gender != "Both":
       merged_data = merged_data[merged_data['Sex'] == selected_gender]

    # Filter out rows without medals
    medal_data = merged_data[merged_data['Medal'].notnull()]

    if medal_data.empty:
        st.warning("No athletes with medals found for the selected filters.")
        return

    # Group by athlete to count their medals
    athlete_medal_counts = medal_data.groupby(['Name', 'region', 'Sport'])['Medal'].count().reset_index()
    athlete_medal_counts = athlete_medal_counts.sort_values(by='Medal', ascending=False)

    # Convert columns to strings to ensure Arrow compatibility
    athlete_medal_counts['Name'] = athlete_medal_counts['Name'].astype(str)
    athlete_medal_counts['region'] = athlete_medal_counts['region'].astype(str)
    athlete_medal_counts['Sport'] = athlete_medal_counts['Sport'].astype(str)

    # Display the top athletes based on medal count
    st.write("Top Athletes by Medal Count")
    st.dataframe(athlete_medal_counts.head(10))  # Show the top 10 athletes

    # Optional: Visualizing the top athletes in a bar plot
    top_athletes_chart = athlete_medal_counts.head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_athletes_chart['Name'], top_athletes_chart['Medal'], color='#FFD700')
    ax.set_xlabel("Number of Medals")
    ax.set_title("Top Athletes by Medal Count")
    plt.gca().invert_yaxis()  # Invert y-axis to have the top athlete at the top
    st.pyplot(fig)

