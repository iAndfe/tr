# chaintools suite

# Function: dividechain
def dividechain(road, precision):
    from shapely.geometry import LineString, MultiPoint, MultiLineString
    from shapely.ops import split
    import pandas as pd
    import numpy as np

    road_x = road["x"]
    road_y = road["y"]

    num_lines = len(road_x)-1
    lines = [0]*num_lines

    for i in range(num_lines):
        lines[i] = LineString([(road_x[i], road_y[i]), (road_x[i+1], road_y[i+1])])

    road_line = MultiLineString(lines)
    road_length = road_line.length

    di = round(road_length*1000000000)

    interval = 1000000000*precision

    chainage_points = MultiPoint([road_line.interpolate(((i*interval)/di), normalized=True) for i in range(0, int(di/interval))])
    chainage_points_x = [p.x for p in chainage_points.geoms]
    chainage_points_y = [p.y for p in chainage_points.geoms]
    chainage_points_chain_array = np.arange(start=0, stop=len(chainage_points_x)*precision, step=precision)
    chainage_points_chain = chainage_points_chain_array.tolist()

    df = pd.DataFrame(chainage_points_x, columns = ['x'])
    df['y'] = chainage_points_y
    df['chain'] = chainage_points_chain

    return df

# Function: chainget
def chainget(chainage, points):
    # input and chainage files, must have 'x' and 'y' columns.
    # chainage file must have 'chain' column

    import pandas as pd
    import numpy as np

    chainage_x = chainage["x"]
    chainage_y = chainage["y"]
    chainage_chain = chainage["chain"]
    points_x = points["x"]
    points_y = points["y"]

    num_points = len(points_x)
    num_chainage = len(chainage_x)

    # Obtain arrays from lists
    chainage_x_array = np.tile(chainage_x, (num_points, 1))
    chainage_y_array = np.tile(chainage_y, (num_points, 1))

    points_x_array = np.tile(points_x, (num_chainage, 1))
    points_y_array = np.tile(points_y, (num_chainage, 1))

    points_x_array = np.transpose(points_x_array)
    points_y_array = np.transpose(points_y_array)

    # Calculate distance/difference between points
    difference = np.sqrt(np.square(chainage_x_array - points_x_array) + np.square(chainage_y_array - points_y_array))
    difference2 = np.transpose(difference)

    # Export data to lists and csv
    points_chainage = [0]*num_points
    points_offset = [0]*num_points

    points_offset = np.amin(difference2, axis = 0)
    points_offset = np.ndarray.tolist(points_offset)

    points_chainage_locations = np.where(difference2 == np.amin(difference2, axis = 0))
    points_chainage_locations_values = points_chainage_locations[0]
    points_chainage_locations_index = points_chainage_locations[1]

    for i in range(num_points):
        points_chainage[points_chainage_locations_index[i]] = chainage_chain[points_chainage_locations_values[i]]

    points['Chainage'] = points_chainage
    points['Offset'] = points_offset

    return points

## Plot points and road function
def plot_points(points, road, limit):

    # Import matplotlib and pandas library
    import pandas as pd
    from matplotlib import pyplot as plt

    # Load road and points from .csv
    road_x = road["x"]
    road_y = road["y"]
    points_x = points["x"]
    points_y = points["y"]

    # Set limit of plot boundaries from min/max co-ords
    min_x = min(min(points_x), min(road_x)) - limit
    min_y = min(min(points_y), min(road_y)) - limit

    max_x = max(max(points_x), max(road_x)) + limit
    max_y = max(max(points_y), max(road_y)) + limit

    plt.xlim(min_x, max_x)
    plt.ylim(min_y, max_y)

    # Add points and road to plot
    plt.plot(road_x, road_y)
    plt.plot(points_x, points_y, 'ko', markersize = 1)

    plt.gca().set_aspect('equal', adjustable='box')

    # Print plot to pdf
    plt.savefig('plot.pdf')

    return print('...Saved to pdf')

