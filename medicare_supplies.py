import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

file_path = "data/Medicare_Durable_Medical_Equipment_Devices_Supplies_by_Geography_and_Service_Data_2020.csv"
data = pd.read_csv(file_path)

# Filter the database by "BETOS_Cd" column where the value is "D1A"
filtered_data = data[(data["BETOS_Cd"] == "D1F") & (data["Rfrg_Prvdr_Geo_Lvl"] == "State")]

# Filter the data further to include only rows with HCPCS_Cd values that appear at least 50 times
filtered_data = filtered_data[filtered_data["HCPCS_Cd"] == "L4387"]
grouped_data = filtered_data.groupby("Rfrg_Prvdr_Geo_Desc")["Avg_Suplr_Sbmtd_Chrg"].median()
unwanted_items = ["Puerto Rico", "Armed Forces Europe", "Armed Forces Pacific", "Foreign Country", "Northern Mariana Islands", "Unknown", "Guam", "Virgin Islands"]
grouped_data = grouped_data[~grouped_data.index.isin(unwanted_items)]

# Read the shapefile
shapefile_path = "2022_census_shapefiles/tl_2022_us_state.shp"
shapefile_data = gpd.read_file(shapefile_path)

merged_data = shapefile_data.merge(grouped_data, left_on="NAME", right_index=True)
# Plot the heatmap with borders
merged_data.plot(column="Avg_Suplr_Sbmtd_Chrg", cmap="YlGnBu", legend=True, edgecolor="black")

# Add a title to the plot
plt.title("Cost of a Walking Boot (non-custom, off the shelf) (L4387) by State")

# Set the limits for the x-axis and y-axis to zoom in on specific region
plt.xlim(-190, -60)  # Replace x_min and x_max with your desired x-axis limits
plt.ylim(15, 75)  # Replace y_min and y_max with your desired y-axis limits

# Show the plot
plt.show()




