import pandas as pd
import geopandas as gpd
import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
import numpy as np
warnings.filterwarnings('ignore')



def extract_data(folder_name):
    all_data = pd.DataFrame()
    file_list = []
    for filename in os.listdir(folder_name):
        if filename.endswith(".csv"):
            year = filename[-8:-4]  # Extract the year from the filename
            file_path = os.path.join(folder_name, filename)
            file_list.append((year, file_path))

    # Sort the file list in descending order based on the year
    file_list.sort(reverse=True)

    # Append all the dataframes into a single dataframe
    for year, file_path in file_list:
        df = pd.read_csv(file_path)
        df["year"] = year  # Add the "year" column
        all_data = all_data._append(df, ignore_index=True)
    return all_data

def create_us_heatmap(all_data, hcpcs_code, year):
    all_data = all_data[all_data["year"] == year]
    filtered_data = all_data[all_data["HCPCS_Cd"] == hcpcs_code]
    grouped_data = filtered_data.groupby("Rfrg_Prvdr_Geo_Desc")["Avg_Suplr_Sbmtd_Chrg"].median()
    unwanted_items = ["Puerto Rico", "Armed Forces Europe", "Armed Forces Pacific", "Foreign Country", "Northern Mariana Islands", "Unknown", "Guam", "Virgin Islands"]
    grouped_data = grouped_data[~grouped_data.index.isin(unwanted_items)]

    # Read the shapefile
    shapefile_path = "shapefiles/tl_2022_us_state.shp"
    shapefile_data = gpd.read_file(shapefile_path)

    merged_data = shapefile_data.merge(grouped_data, left_on="NAME", right_index=True)
    # Plot the heatmap with borders
    merged_data.plot(column="Avg_Suplr_Sbmtd_Chrg", cmap="YlGnBu", legend=True, edgecolor="black")

    # Add a title to the plot
    default_title = f"Cost of {filtered_data.iloc[0]['HCPCS_Desc']} ({hcpcs_code}) by State"
    user_title = input(f"Enter a title for the heatmap (or press Enter to keep the default title '{default_title}'): ")
    if user_title:
        plt.title(user_title, loc='center', wrap=True)
    else:
        plt.title(default_title, loc='center', wrap=True)

    # Set the limits for the x-axis and y-axis to zoom in on specific region
    plt.xlim(-190, -60)  # Replace x_min and x_max with your desired x-axis limits
    plt.ylim(15, 75)  # Replace y_min and y_max with your desired y-axis limits

    # Remove x-axis and y-axis
    plt.axis('off')

    # Save the plot
    save_folder = "graphs"
    filename = f"{hcpcs_code}_{year}_heatmap.png"
    save_path = os.path.join(save_folder, filename)
    plt.savefig(save_path)
    print("A heatmap has been saved as a .png file in the 'Graphs' folder.\n")
    plt.clf()

def create_line_chart(all_data, hcpcs_code):
    national_data = all_data[all_data["Rfrg_Prvdr_Geo_Lvl"] == "National"]
    national_data = national_data[national_data["HCPCS_Cd"] == hcpcs_code]
    national_data['year'] = national_data['year'].astype(int)
    # Create a sorted list of years from 2013 to 2021
    years = np.arange(2013, 2022)

    # Create a list of charges for each year
    charges = [round(national_data[national_data["year"] == year]["Avg_Suplr_Sbmtd_Chrg"].median(), 2) for year in years]

    # Create a line graph
    plt.plot(years, charges)

    # Set the labels for the X-axis and Y-axis
    plt.xlabel("Year")
    plt.ylabel("Average Supplier Charge (USD)")

    # Set the title of the graph
    default_title = f"Average Supplier Charge for ({hcpcs_code}) over the Years"
    user_title = input(f"Enter a title for the line chart (or press Enter to keep the default title '{default_title}'): ")
    if user_title:
        plt.title(user_title, loc='center', wrap=True)
    else:
        plt.title(default_title, loc='center', wrap=True)

    # Add labels to each point on the line chart
    for i, charge in enumerate(charges):
        plt.scatter(years[i], charge, color='black')
        plt.text(years[i], charge, f"${charge}", ha='center', va='bottom')

    # Save the plot
    save_folder = "graphs"
    filename = f"{hcpcs_code}_{str(year)}_historic_prices.png"
    save_path = os.path.join(save_folder, filename)
    plt.savefig(save_path)
    print("A line chart has been saved as a .png file in the 'graphs' folder.\n")
    plt.clf()

def create_differential_abundance_plot(all_data, hcpcs_code, year):
    all_data = all_data[all_data["year"] == year]
    filtered_data = all_data[all_data["HCPCS_Cd"] == hcpcs_code]
    # END: be15d9bcejpp
    grouped_data = filtered_data.groupby("Rfrg_Prvdr_Geo_Desc")["Avg_Suplr_Sbmtd_Chrg"].median()
    unwanted_items = ["Puerto Rico", "Armed Forces Europe", "Armed Forces Pacific", "Foreign Country", "Northern Mariana Islands", "Unknown", "Guam", "Virgin Islands", "National"]
    grouped_data = grouped_data[~grouped_data.index.isin(unwanted_items)]
    # Sort the grouped data by median value
    sorted_data = grouped_data.sort_values()

    # Calculate the median value
    median_value = sorted_data.median()

    # Get the top and bottom 5 values
    top_values = sorted_data.tail(5)
    bottom_values = sorted_data.head(5)

    # Create a differential abundance plot
    plt.bar(bottom_values.index, bottom_values - median_value, color='green')
    plt.bar(top_values.index, top_values - median_value, color='red')

    # Add labels to the top and bottom bars
    for i, value in enumerate(sorted_data):
        if i < 5 or i >= len(sorted_data) - 5:
            if value > median_value:
                if value - median_value > 100 or value - median_value < -100:
                    label = f"+${int(value - median_value)}"
                else:
                    label = f"+${value - median_value:.2f}"
            else:
                if value - median_value > 100 or value - median_value < -100:
                    label = f"${int(value - median_value)}"
                else:
                    label = f"${value - median_value:.2f}"
            if value > median_value:
                plt.text(i-41, value - median_value, label, ha='center', va='bottom', color='black')
            else:
                plt.text(i, value - median_value, label, ha='center', va='top', color='black')
    
    # Add a horizontal line at the median value
    plt.axhline(0, color='black', linestyle='--')

    # Set the labels for the X-axis and Y-axis
    plt.xlabel("State")
    plt.ylabel("Supplier Charges (USD)")

    # Set the title of the graph
    default_title = "Supplier Charges for " + hcpcs_code + " in " + str(year)
    user_title = input(f"Enter a title for the barplot (or press Enter to keep the default title '{default_title}'): ")
    if user_title:
        plt.title(user_title, loc='center', wrap=True)
    else:
        plt.title(default_title, loc='center', wrap=True)

    # Add the median value to every value of the y-axis
    plt.yticks([sorted_data.min() - median_value, 0, sorted_data.max() - median_value], [f"${sorted_data.min():.2f}", f"${median_value:.2f}", f"${sorted_data.max():.2f}"])

    # Rotate the x-axis labels for better visibility
    plt.xticks(rotation=45)

    # Save the plot
    save_folder = "graphs"
    filename = f"{hcpcs_code}_{year}_barplot.png"
    save_path = os.path.join(save_folder, filename)
    plt.savefig(save_path)
    print("A barplot has been saved as a .png file in the 'graphs' folder.\n")
    plt.clf()

def create_regional_table(all_data, hcpcs_code, year, title=None):
    # Load the CSV file
    regions_file = "census_tools/us census bureau regions and divisions.csv"
    regions_data = pd.read_csv(regions_file)
        
    # Filter the data to include only rows with the specified HCPCS code
    filtered_data = all_data[all_data["HCPCS_Cd"] == hcpcs_code]
    
    # Merge filtered_data with regions_data on the "Rfrg_Prvdr_Geo_Desc" column in filtered_data and "state" column in regions_data
    merged_data = pd.merge(filtered_data, regions_data, left_on="Rfrg_Prvdr_Geo_Desc", right_on="State")

    # Group the merged data by "Region" and calculate the mean and standard deviation of "Avg_Suplr_Sbmtd_Chrg", and the sum of "Tot_Suplr_Srvcs"
    regional_stats = merged_data.groupby("Region").agg({"Avg_Suplr_Sbmtd_Chrg": ["mean", "std"], "Tot_Suplr_Srvcs": "sum"})

    # Create a new DataFrame with the regional statistics
    table_data = pd.DataFrame(regional_stats).reset_index()
    table_data.columns = ["Region", "Mean", "SD", "n"]

    # Sort the table_data by the "Region" column
    sorted_table = table_data.sort_values("Region")
    sorted_table["Mean"] = "$" + sorted_table["Mean"].round(2).apply(lambda x: f'{x:.2f}')
    sorted_table["SD"] = "$" + sorted_table["SD"].round(2).apply(lambda x: f'{x:.2f}')
    
    # Set the title of the graph
    default_title = "Regional Differences in Pricing for " + hcpcs_code + " in " + str(year)
    title = input("Enter a custom title (press enter to keep default): ")
    if not title:
        title = default_title
    if title:
        plt.title(title, wrap=True, loc='center')
    else:
        plt.title(default_title, wrap=True, loc='center')

    # Create a table visualization
    fig, ax = plt.subplots()
    ax.axis('off')
    ax.axis('tight')
    ax.table(cellText=sorted_table.values, colLabels=sorted_table.columns, loc='center')

    # Save the table as a .png file
    save_folder = "graphs"
    filename = f"{hcpcs_code}_{year}_table.png"
    save_path = os.path.join(save_folder, filename)
    plt.savefig(save_path)
    print("A table has been saved as a .png file in the 'graphs' folder.\n")
    plt.clf()

def generate_scatterplot(all_data, hcpcs_code, year):
    all_data = all_data[all_data["year"] == year]
    filtered_data = all_data[(all_data["HCPCS_Cd"] == hcpcs_code)]
    filtered_data = filtered_data[filtered_data["Rfrg_Prvdr_Geo_Lvl"] == "State"]

    # Create a scatterplot
    plt.scatter(filtered_data["Tot_Suplr_Srvcs"], filtered_data["Avg_Suplr_Sbmtd_Chrg"], alpha=0.5)

    # Calculate the linear regression line
    x = filtered_data["Tot_Suplr_Srvcs"]
    y = filtered_data["Avg_Suplr_Sbmtd_Chrg"]
    m, b = np.polyfit(x, y, 1)
    plt.plot(x, m*x + b, color='red')

    # Calculate the correlation coefficient (R value)
    r_value = np.corrcoef(x, y)[0, 1]

    # Set the labels for the X-axis and Y-axis
    plt.xlabel("HCPCS Code")
    plt.ylabel("Average Supplier Charge (USD)")

    # Set the title of the graph
    default_title = f"Supplier Charges for {hcpcs_code} in {year}"
    user_title = input(f"Enter a title for the scatterplot (or press Enter to keep the default title '{default_title}'): ")
    if user_title:
        plt.title(user_title, loc='center', wrap=True)
    else:
        plt.title(default_title, loc='center', wrap=True)

    # Add the R value to the plot
    plt.text(0.95, 0.05, f"R = {r_value:.2f}", ha='right', va='center', transform=plt.gca().transAxes)

    # Save the plot
    save_folder = "graphs"
    filename = f"{hcpcs_code}_{year}_scatterplot.png"
    save_path = os.path.join(save_folder, filename)
    plt.savefig(save_path)
    print("A scatterplot has been saved as a .png file in the 'graphs' folder.\n")
    plt.clf()

# Extract all data from the folder "data"
data_folder = "data"
all_data = extract_data(data_folder)
all_data['year'] = all_data['year'].astype(int)

# Find the latest year of data in the dataset and filter it to have the latest data
highest_year = all_data["year"].max()
lowest_year = all_data["year"].min()

# Filter the data further to include only rows with HCPCS_Cd values that appear at least 50 times
while True:
    hcpcs_code = input("Enter the HCPCS code of interest: ")
    if hcpcs_code in all_data["HCPCS_Cd"].unique():
        break
    print(f"The HCPCS code {hcpcs_code} is not in the dataset. Please try again.\n")

while True:
    year = int(input(f'Enter the year of interest ({lowest_year}-{highest_year}): '))
    if int(lowest_year) <= int(year) <= int(highest_year):
        break
    print(f"Invalid input. Please enter a valid year between {lowest_year} and {highest_year}.\n")

create_differential_abundance_plot(all_data, hcpcs_code, year)
create_line_chart(all_data, hcpcs_code)
create_regional_table(all_data, hcpcs_code, year)
create_us_heatmap(all_data, hcpcs_code, year)
generate_scatterplot(all_data, hcpcs_code, year)
