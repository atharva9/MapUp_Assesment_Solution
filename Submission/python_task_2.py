
import pandas as pd
import networkx as nx
from datetime import datetime
import datetime as dt

def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    

    # Create a graph using networkx
    G = nx.Graph()

    # Add edges and distances to the graph
    for _, row in df.iterrows():
        G.add_edge(row['id_start'], row['id_end'], distance=row['distance'])
        
    # Calculate all pairs shortest paths
    all_pairs_shortest_paths = dict(nx.all_pairs_dijkstra_path_length(G, weight='distance'))

    # Extract unique toll locations
    toll_locations = sorted(df['id_start'].unique())

    # Create a DataFrame to store the distance matrix
    distance_matrix = pd.DataFrame(index=toll_locations, columns=toll_locations)

    # Populate the distance matrix with cumulative distances
    for start_toll in toll_locations:
        for end_toll in toll_locations:
            if start_toll == end_toll:
                distance_matrix.loc[start_toll, end_toll] = 0
            else:
                # Check if the distance is known in either direction
                if start_toll in all_pairs_shortest_paths and end_toll in all_pairs_shortest_paths[start_toll]:
                    distance_matrix.loc[start_toll, end_toll] = all_pairs_shortest_paths[start_toll][end_toll]
                elif end_toll in all_pairs_shortest_paths and start_toll in all_pairs_shortest_paths[end_toll]:
                    distance_matrix.loc[start_toll, end_toll] = all_pairs_shortest_paths[end_toll][start_toll]
                else:
                    # If no direct path is known, set distance to NaN
                    distance_matrix.loc[start_toll, end_toll] = None

    return distance_matrix




def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Create a list to store the unrolled data
    unrolled_data = []

    # Iterate over the rows and columns of the distance matrix
    for id_start in distance_matrix.index:
        for id_end in distance_matrix.columns:
            if id_start != id_end:
                # Extract the distance value
                distance = distance_matrix.loc[id_start, id_end]

                # Append the data to the list
                unrolled_data.append({'id_start': id_start, 'id_end': id_end, 'distance': distance})

    # Create a DataFrame from the unrolled data
    unrolled_df = pd.DataFrame(unrolled_data)

    return unrolled_df




def find_ids_within_ten_percentage_threshold(df, reference_value)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Calculate the average distance for the reference value
    reference_avg_distance = df[df['id_start'] == reference_value]['distance'].mean()

    # Calculate the lower and upper bounds for the 10% threshold
    lower_threshold = reference_avg_distance - 0.1 * reference_avg_distance
    upper_threshold = reference_avg_distance + 0.1 * reference_avg_distance

    # Filter id_start values within the 10% threshold
    result_df = df[(df['distance'] >= lower_threshold) & (df['distance'] <= upper_threshold)]

    # Sort the result by id_start values
    result_df = result_df.sort_values(by='id_start')

    return result_df






def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Define rate coefficients for each vehicle type
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}

    # Calculate toll rates for each vehicle type
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        # Create a new column for the toll rate of the current vehicle type
        df[vehicle_type] = df['distance'] * rate_coefficient

    # Drop unnecessary columns from the DataFrame
    df = df.drop(columns=['distance'])

    return df







def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Define time ranges and discount factors
    time_ranges = {
        'morning': ('00:00:00', '10:00:00'),
        'day': ('10:00:00', '18:00:00'),
        'evening': ('18:00:00', '23:59:59')
    }
    weekday_discount_factors = {'morning': 0.8, 'day': 1.2, 'evening': 0.8}
    weekend_discount_factor = 0.7

    # Extract day of the week and time components
    df['start_day'] = pd.to_datetime(df['startDay'], errors='coerce').dt.day_name()
    df['end_day'] = pd.to_datetime(df['endDay'], errors='coerce').dt.day_name()
    df['start_time'] = pd.to_datetime(df['startTime'], errors='coerce').dt.time
    df['end_time'] = pd.to_datetime(df['endTime'], errors='coerce').dt.time

    # Calculate toll rates based on time ranges and discount factors
    for time_range, (start_time_range, end_time_range) in time_ranges.items():
        mask_weekday = (df['start_day'].isin(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])) & \
                       (df['start_time'] >= pd.to_datetime(start_time_range, format='%H:%M:%S').time()) & \
                       (df['start_time'] <= pd.to_datetime(end_time_range, format='%H:%M:%S').time())

        mask_weekend = (df['start_day'].isin(['Saturday', 'Sunday']))

        # Modify the names of the columns based on your dataset
        df.loc[mask_weekday, ['able2Hov2', 'able2Hov3', 'able3Hov2', 'able3Hov3']] *= weekday_discount_factors[time_range]
        df.loc[mask_weekend, ['able2Hov2', 'able2Hov3', 'able3Hov2', 'able3Hov3']] *= weekend_discount_factor

    return df[['id', 'name', 'id_2', 'startDay', 'startTime', 'endDay', 'endTime', 
               'able2Hov2', 'able2Hov3', 'able3Hov2', 'able3Hov3', 'able5Hov2', 
               'able5Hov3', 'able4Hov2', 'able4Hov3']]

