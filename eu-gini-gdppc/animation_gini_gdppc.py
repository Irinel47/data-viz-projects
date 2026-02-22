# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 12:48:55 2025

@author: Irinel
"""

import pandas as pd
import requests
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyArrowPatch
import numpy as np

# Set Global Font and Text Color
plt.rcParams["font.family"] = "Gill Sans MT"

# Define the interval of years
years = list(range(2010, 2021))  # From 2010 to 2020

# Dictionary mapping ISO-3 to ISO-2 country codes
eu_countries = {
    "AUT": "AT", "BEL": "BE", "BGR": "BG", "HRV": "HR", "CYP": "CY",
    "CZE": "CZ", "DNK": "DK", "EST": "EE", "FIN": "FI", "FRA": "FR",
    "DEU": "DE", "GRC": "GR", "HUN": "HU", "IRL": "IE", "ITA": "IT",
    "LVA": "LV", "LTU": "LT", "LUX": "LU", "MLT": "MT", "NLD": "NL",
    "POL": "PL", "PRT": "PT", "ROU": "RO", "SVK": "SK", "SVN": "SI",
    "ESP": "ES", "SWE": "SE", "GBR": "UK"
}

# Extract the list of ISO-3 codes
country_iso3_list = list(eu_countries.keys())

# Base URLs for World Bank API
gini_url = "http://api.worldbank.org/v2/country/{}/indicator/SI.POV.GINI?format=json"
gdp_url = "http://api.worldbank.org/v2/country/{}/indicator/NY.GDP.MKTP.CD?format=json"
population_url = "http://api.worldbank.org/v2/country/{}/indicator/SP.POP.TOTL?format=json"

# Function to fetch World Bank data
def fetch_world_bank_data(url, countries):
    all_data = []
    for country in countries:
        response = requests.get(url.format(country))
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and isinstance(data[1], list):
                all_data.extend(data[1])
            else:
                print(f"Warning: No valid data for {country}")
        else:
            print(f"Error fetching data for {country} (Status Code: {response.status_code})")
    
    if not all_data:
        raise ValueError("No valid data retrieved from World Bank API.")
    
    return pd.DataFrame(all_data)

# Fetch data for all years (2010-2020)
gini_df = fetch_world_bank_data(gini_url, country_iso3_list)
gdp_df = fetch_world_bank_data(gdp_url, country_iso3_list)
population_df = fetch_world_bank_data(population_url, country_iso3_list)

# Extract country codes
gini_df['country'] = gini_df['countryiso3code']
gdp_df['country'] = gdp_df['countryiso3code']
population_df['country'] = population_df['countryiso3code']

# Select relevant columns
gini_df = gini_df[['country', 'date', 'value']].rename(columns={'value': 'gini_index'})
gdp_df = gdp_df[['country', 'date', 'value']].rename(columns={'value': 'gdp'})
population_df = population_df[['country', 'date', 'value']].rename(columns={'value': 'population'})

# Convert 'date' to integer
gini_df['date'] = gini_df['date'].astype(int)
gdp_df['date'] = gdp_df['date'].astype(int)
population_df['date'] = population_df['date'].astype(int)

# Merge GDP and Population data
gdp_per_capita_df = pd.merge(gdp_df, population_df, on=['country', 'date'], how='inner')

# Calculate GDP per capita
gdp_per_capita_df['gdp_per_capita'] = gdp_per_capita_df['gdp'] / gdp_per_capita_df['population']

# Merge GINI index with GDP per capita and Population
merged_df = pd.merge(gini_df, gdp_per_capita_df[['country', 'date', 'gdp_per_capita', 'gdp', 'population']], on=['country', 'date'], how='inner')

# Function to assign colors based on population range
def assign_population_color(population):
    if population < 1_000_000:
        return "bisque"     
    elif 1_000_000 <= population < 10_000_000:
        return "darksalmon"  
    elif 10_000_000 <= population < 20_000_000:
        return "plum"   
    else:
        return "royalblue"    

# Set up the figure
fig, ax = plt.subplots(figsize=(25, 15), facecolor='floralwhite')

# Static title
ax.set_title("GDP per Capita vs GINI Index - EU Countries", fontsize=30, color="black")

# Function to draw and label a compass
def draw_compass(ax, center_x, center_y):
    # Define the arrow style
    arrow_props = {
        'arrowstyle': '->',
        'mutation_scale': 25,
        'linewidth': 2,
        'color': 'black',
        'alpha': 0.8
    }
    
    # Create and add arrows
    arrows = [
        FancyArrowPatch((center_x, center_y), (center_x + 5, center_y), **arrow_props),  # Right arrow
        FancyArrowPatch((center_x, center_y), (center_x - 5, center_y), **arrow_props),  # Left arrow
        FancyArrowPatch((center_x, center_y), (center_x, center_y + 1), **arrow_props),   # Up arrow
        FancyArrowPatch((center_x, center_y), (center_x, center_y - 1), **arrow_props)    # Down arrow
    ]
    for arrow in arrows:
        ax.add_patch(arrow)

    # Label arrows
    ax.text(center_x + 6, center_y, 'Higher GDP per Capita', horizontalalignment='left', verticalalignment='center', fontsize=15, color='black', alpha=0.8)
    ax.text(center_x - 6, center_y, 'Lower GDP per Capita', horizontalalignment='right', verticalalignment='center', fontsize=15, color='black', alpha=0.8)
    ax.text(center_x, center_y + 1.5, 'More inequality', horizontalalignment='center', verticalalignment='bottom', fontsize=15, color='black', alpha=0.8)
    ax.text(center_x, center_y - 1.5, 'Less inequality', horizontalalignment='center', verticalalignment='top', fontsize=15, color='black', alpha=0.8)
    
# Function to update the animation
def update(year):
    ax.clear()
    
    # Redraw fixed axes and labels
    ax.set_xlim(0, 140)
    ax.set_ylim(22, 42.5)
    
    ax.set_xticks([0,20,40,60,80,100,120,140])
    ax.set_xticklabels(['0k','20k','40k','60k','80k','100k','120k','140k'], fontsize=15, color="dimgray")
    ax.set_yticks([20,22.5,25,27.5,30,32.5,35,37.5,40,42.5])
    ax.set_yticklabels(['20.0%','22.5%','25.0%','27.5%','30.0%','32.5%','35.0%','37.5%','40.0%','42.5%'], fontsize=15, color="dimgray")

    ax.set_xlabel("GDP per Capita (USD)", fontsize=20, color="black")
    ax.set_ylabel("GINI Index (Inequality)", fontsize=20, color="black")
    ax.set_title("GDP per Capita vs GINI Index - EU Countries", fontsize=30, color="black")
    ax.grid(True, linestyle='--', alpha=0.8)

    # Filter data for the given year
    filtered_df = merged_df[merged_df['date'] == year].copy()
    filtered_df.loc[:, 'gdp_per_capita'] = filtered_df['gdp_per_capita'] / 1_000
    filtered_df.loc[:, "color"] = filtered_df["population"].apply(assign_population_color)

    bubble_size = np.maximum(filtered_df['gdp'] / 200_000_000, 500)

    # Plot scatter
    ax.scatter(filtered_df['gdp_per_capita'], filtered_df['gini_index'], 
               c=filtered_df['color'], alpha=0.7, s=bubble_size, edgecolors='antiquewhite')

    # Add country labels
    for i, row in filtered_df.iterrows():
        country_code_2 = eu_countries.get(row['country'], row['country'])
        label_size = max(12, bubble_size[i] / 750)
        ax.text(row['gdp_per_capita'], row['gini_index'], country_code_2,
                fontsize=label_size, ha='center', va='center', color='black', fontweight='bold')

    # Add year in bottom right
    ax.text(125, 22.5, str(year), fontsize=40, color="dimgray", fontweight='bold')

    # Legend
    legend_labels = ["0 - 1M", "1M - 10M", "10M - 20M", "20M +"]
    legend_colors = ["bisque", "darksalmon", "plum", "royalblue"]
    handles = [plt.Line2D([0], [0], marker='o', color='w', markersize=15, markerfacecolor=color) for color in legend_colors]
    ax.legend(handles, legend_labels, title="Population Range", title_fontsize=20, fontsize=18, loc="upper right", facecolor="floralwhite", labelcolor='black')
    
    # Draw compass at the specified location
    draw_compass(ax, 90, 37.5)

# Create animation
ani = animation.FuncAnimation(fig, update, frames=years, interval=1000, repeat=True)

# Save as GIF
ani.save("gdp_gini_eu.gif", writer="pillow", fps=1)

print("GIF saved as gdp_gini_eu.gif")