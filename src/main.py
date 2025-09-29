import rasterio
import geopandas as gpd
from shapely import centroid

# Modify these variables to point to the correct locations of .tif and .geojson files
heat_data_path = '../data/akron_heat.tif'
buildings_data_path = '../data/akron_buildings.geojson'
footways_data_path = '../data/akron_footways.geojson'

# LANDSAT8 Thermal Data
heat_data = rasterio.open(heat_data_path)

# Buildings and Footways
buildings = gpd.read_file(buildings_data_path)
footways = gpd.read_file(footways_data_path)

# Match geojson CRS to raster data
buildings = buildings.to_crs("EPSG:32617")
footways = footways.to_crs("EPSG:32617")

# Get raw integers array from imagery
band = heat_data.read(1)

# Apply raster data polygons
def set_heat_value_polygon(row):
    
    # Calculate the centriod of each polygon.
    # Georeference the raster data by index.
    # Apply the corresponding heat value.
    center = centroid(row['geometry'])
    x, y = heat_data.index(center.x, center.y)
    row['heat_index'] = band[x, y]
    return row

buildings = buildings.apply(set_heat_value_polygon, axis=1)

# Apply raster data to linestrings
def set_heat_value_linestring(row):

    # Calculate average raster value over length of linestring.
    coords = row['geometry'].coords

    total = 0
    for i in range(len(coords)):
        x, y = heat_data.index(coords[i][0], coords[i][1])
        total = total + int(band[x, y])

    row['heat_index'] = total / len(coords)

    return row

footways = footways.apply(set_heat_value_linestring, axis=1)

# Get load geojsons for various areas of interest
UA_path = '../data/UofA.geojson'
highland_path = '../data/highland_square.geojson'
downtown_path = '../data/downtown.geojson'

UofA = gpd.read_file(UA_path)
highland_square = gpd.read_file(highland_path)
downtown = gpd.read_file(downtown_path)

UofA = UofA.to_crs("EPSG:32617")
highland_square = highland_square.to_crs("EPSG:32617")
downtown = downtown.to_crs("EPSG:32617")

# Function to return Avg, Max, and Min heat index data in a given boundary.
def get_stats(bbox, heat_data):

    filtered = heat_data[heat_data.intersects(bbox)]

    mean = filtered["heat_index"].mean()
    mini = filtered["heat_index"].min()
    maxi = filtered["heat_index"].max()

    return (mean, mini, maxi)

# U of A data

mean, mini, maxi = get_stats(UofA.iloc[0]["geometry"], footways)

print(f"University of Akron Footways:\n Mean:{mean}\n Min:{mini}\n Max:{maxi}")

mean, mini, maxi = get_stats(UofA.iloc[0]["geometry"], buildings)

print(f"University of Akron Buildings:\n Mean:{mean}\n Min:{mini}\n Max:{maxi}")


# Downtown data

mean, mini, maxi = get_stats(downtown.iloc[0]["geometry"], footways)

print(f"Downtown Akron Footways:\n Mean:{mean}\n Min:{mini}\n Max:{maxi}")

mean, mini, maxi = get_stats(downtown.iloc[0]["geometry"], buildings)

print(f"Downtown Akron Buildings:\n Mean:{mean}\n Min:{mini}\n Max:{maxi}")


# Highland Square data

mean, mini, maxi = get_stats(highland_square.iloc[0]["geometry"], footways)

print(f"Highland Square Footways:\n Mean:{mean}\n Min:{mini}\n Max:{maxi}")

mean, mini, maxi = get_stats(highland_square.iloc[0]["geometry"], buildings)

print(f"Highland Square Buildings:\n Mean:{mean}\n Min:{mini}\n Max:{maxi}")
