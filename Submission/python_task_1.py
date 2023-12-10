import pandas as pd

def generate_car_matrix(df)->pd.DataFrame:
    """
    Creates a DataFrame  for id combinations.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values, 
                          where 'id_1' and 'id_2' are used as indices and columns respectively.
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Create a pivot table using id_1, id_2, and car columns
    p_car_matrix = df.pivot_table(index='id_1', columns='id_2', values='car', aggfunc='first', fill_value=0)

    # Set the diagonal values to 0
    for index in p_car_matrix.index:
        if index in p_car_matrix.columns:
            p_car_matrix.loc[index, index] = 0

    return p_car_matrix



def get_type_count(df)->dict:
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    # Add a new categorical column 'car_type' based on values of the column 'car'
    df['car_type'] = pd.cut(df['car'], bins=[-float('inf'), 15, 25, float('inf')],
                            labels=['low', 'medium', 'high'], include_lowest=True)

    # Calculate the count of occurrences for each 'car_type' category
    type_counts = df['car_type'].value_counts().to_dict()

    # Sort the dictionary alphabetically based on keys
    sorted_type_counts = {key: type_counts[key] for key in sorted(type_counts)}

    return sorted_type_counts


def get_bus_indexes()->list:
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Calculate the mean value of the 'bus' column
    bus_mean = df['bus'].mean()

    # Identify indices where 'bus' values are greater than twice the mean
    bus_indexes = df[df['bus'] > 2 * bus_mean].index.tolist()

    # Sort the indices in ascending order
    bus_indexes.sort()

    return bus_indexes


def filter_routes()->list:
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Group by 'route' and calculate the average of 'truck' column for each route
    route_avg_truck = df.groupby('route')['truck'].mean()

    # Filter routes where the average truck value is greater than 7
    filtered_routes = route_avg_truck[route_avg_truck > 7].index.tolist()

    # Sort the list of routes in ascending order
    filtered_routes.sort()

    return filtered_routes




def multiply_matrix(input_matrix)->pd.DataFrame:
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    # Copy the input matrix to avoid modifying the original DataFrame
    modified_matrix = input_matrix.copy()

    # Apply the modification logic to each value in the DataFrame
    modified_matrix = modified_matrix.applymap(lambda x: x * 0.75 if x > 20 else x * 1.25)

    # Round the values to 1 decimal place
    modified_matrix = modified_matrix.round(1)

    return modified_matrix



def time_check(df)->pd.Series:
    """
    Use shared dataset-2 to verify the completeness of the data by checking whether the timestamps for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period

    Args:
        df (pandas.DataFrame)

    Returns:
        pd.Series: return a boolean series
    """
    # Combine 'startDay' and 'startTime' to create a 'startTimestamp' column
    df['startTimestamp'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'], errors='coerce')

    # Combine 'endDay' and 'endTime' to create an 'endTimestamp' column
    df['endTimestamp'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'], errors='coerce')

    # Drop rows with invalid timestamps
    df = df.dropna(subset=['startTimestamp', 'endTimestamp'])

    # Calculate the time duration for each record
    df['duration'] = df['endTimestamp'] - df['startTimestamp']

    # Check if the duration covers a full 24-hour period and spans all 7 days
    completeness_check = (
        (df['duration'] >= pd.Timedelta(days=1)) &
        (df['duration'] < pd.Timedelta(days=2)) &
        (df['startTimestamp'].dt.hour == 0) &
        (df['startTimestamp'].dt.minute == 0) &
        (df['startTimestamp'].dt.second == 0) &
        (df['endTimestamp'].dt.hour == 23) &
        (df['endTimestamp'].dt.minute == 59) &
        (df['endTimestamp'].dt.second == 59)
    )

    # Create a multi-index with (id, id_2)
    multi_index = df.set_index(['id', 'id_2']).index

    # Create a boolean series with multi-index
    completeness_series = pd.Series(completeness_check.values, index=multi_index)

    return completeness_series
