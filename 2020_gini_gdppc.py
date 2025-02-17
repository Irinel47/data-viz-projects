# -*- coding: utf-8 -*-
"""
Created on Fri Feb 14 13:00:10 2025

@author: Irinel
"""

import pandas as pd
import requests
import matplotlib.pyplot as plt

# Set Global Font and Text Color
plt.rcParams["font.family"] = "Gill Sans MT"

# List of EU country ISO 3-letter codes (World Bank expects these)
eu_countries = ["AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA",
                "DEU", "GRC", "HUN", "IRL", "ITA", "LVA", "LTU", "LUX", "MLT", "NLD",
                "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE"]

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
                all_data.extend(data[1])  # Append data for each country
            else:
                print(f"Warning: No valid data for {country}")
        else:
            print(f"Error fetching data for {country} (Status Code: {response.status_code})")
    
    if not all_data:
        raise ValueError("No valid data retrieved from World Bank API.")
    
    return pd.DataFrame(all_data)

# Fetch data for all EU countries
gini_df = fetch_world_bank_data(gini_url, eu_countries)
gdp_df = fetch_world_bank_data(gdp_url, eu_countries)
population_df = fetch_world_bank_data(population_url, eu_countries)

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

# Filter for the year 2020
filtered_df = merged_df[merged_df['date'] == 2020].copy()

# Scale GDP per capita (convert to thousands for better readability)
filtered_df.loc[:, 'gdp_per_capita'] = filtered_df['gdp_per_capita'] / 1_000

# Scale GDP for Bubble Size
bubble_size = filtered_df['gdp'] / 100_000_000

# Define a function to assign colors based on population range
def assign_population_color(population):
    if population < 1_000_000:
        return "bisque"     # 0 - 1 million
    elif 1_000_000 <= population < 10_000_000:
        return "darksalmon"   # 1 - 10 million
    elif 10_000_000 <= population < 20_000_000:
        return "plum"   # 10 - 20 million
    else:
        return "royalblue"    # 20 million and above

# Assign colors based on population
filtered_df.loc[:, "color"] = filtered_df["population"].apply(assign_population_color)

# Scatter Plot with Population-Based Colors
plt.figure(figsize=(25, 15), facecolor='floralwhite')
plt.scatter(filtered_df['gdp_per_capita'], filtered_df['gini_index'], c=filtered_df['color'], alpha=0.7, s=bubble_size, edgecolors='antiquewhite')

# Add labels using ISO 3-letter country codes
for i, row in filtered_df.iterrows():
    label_size = max(12, bubble_size[i] / 750)
    plt.text(row['gdp_per_capita'], row['gini_index'], row['country'],
             fontsize=label_size, ha='center', va='center', color='black', fontweight='bold')

# Legend for Population Ranges
legend_labels = ["0 - 1M", "1M - 10M", "10M - 20M", "20M +"]
legend_colors = ["bisque", "darksalmon", "plum", "royalblue"]
handles = [plt.Line2D([0], [0], marker='o', color='w', markersize=15, markerfacecolor=color) for color in legend_colors]
plt.legend(handles, legend_labels, title="Population Range", title_fontsize=20, fontsize=18, loc="upper right", facecolor="floralwhite", labelcolor='black')

# Customize plot
plt.xlabel("GDP per Capita (USD)", fontsize=20, color="black")
plt.ylabel("GINI Index (Inequality)", fontsize=20, color="black")
plt.xticks([20,40,60,80,100,120], ['20k','40k','60k','80k','100k','120k'], fontsize=15, color="dimgray")
plt.yticks([20,22.5,25,27.5,30,32.5,35,37.5,40,42.5], ['20.0%','22.5%','25.0%','27.5%','30.0%','32.5%','35.0%','37.5%','40.0%','42.5%'], fontsize=15, color="dimgray")
plt.title("GDP per Capita vs GINI Index - EU Countries, 2020", fontsize=30, color="black")
plt.grid(True, linestyle='--', alpha=0.8)

# Show the plot
plt.show()