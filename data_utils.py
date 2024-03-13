import pandas as pd
import numpy as np

def load_baseline_data(csv_file_path):
    """
    Load and return the baseline data from the given CSV file path.

    Args:
        csv_file_path (str): Path to the CSV file containing the baseline data.

    Returns:
        pd.DataFrame: Baseline data as a Pandas DataFrame.
    """
    return pd.read_csv(csv_file_path)

def month_to_index(month_name):
    """
    Convert a month name or number to its corresponding numerical index.

    Args:
        month_name (str or int): Month name or number.

    Returns:
        tuple: Numerical index of the month and the number of days in the month.
    """
    if isinstance(month_name, int):
        if month_name < 1 or month_name > 12:
            raise ValueError("Invalid month number")
        return month_name, 31  # Assuming all months have 31 days
    else:
        months = {
            (1, 31): ['jan', 'january', 'janeiro', 'ene', 'enero', 'janvier', 'januar'],
            (2, 28): ['feb', 'february', 'fev', 'fevereiro', 'febrero', 'fév', 'février', 'februar'],
            (3, 31): ['mar', 'march', 'março', 'marzo', 'mars', 'mär', 'märz'],
            (4, 30): ['apr', 'april', 'abr', 'abril', 'avr', 'avril'],
            (5, 31): ['may', 'mai', 'maio', 'mayo'],
            (6, 30): ['jun', 'june', 'junho', 'junio', 'juin', 'juni'],
            (7, 31): ['jul', 'july', 'julho', 'julio', 'juillet', 'juli'],
            (8, 31): ['aug', 'august', 'ago', 'agosto', 'aoû', 'août'],
            (9, 30): ['sep', 'september', 'set', 'setembro', 'septiembre', 'septembre'],
            (10, 31): ['oct', 'october', 'out', 'outubro', 'octubre', 'octobre', 'okt', 'oktober'],
            (11, 30): ['nov', 'november', 'novembro', 'noviembre', 'novembre'],
            (12, 31): ['dec', 'december', 'dez', 'dezembro', 'dic', 'diciembre', 'déc', 'décembre', 'dezember']
        }


        # Return month index and days in the month
        month_name = month_name.lower()
    
        # Iterate through the dictionary to find the month info
        for month_info, names in months.items():
            if month_name in names:
                return month_info
        return (0, 0)

def preprocess_baseline_data(baseline_data):
    """
    Preprocess the baseline data by expanding monthly data to a daily format and adjusting values.
    Additionally, generate a unique, continuous day count across all months.

    Args:
        baseline_data (pd.DataFrame): Baseline data as a Pandas DataFrame.

    Returns:
        pd.DataFrame: Preprocessed baseline data in a daily format with a continuous day count.
    """
    daily_data = []
    cumulative_day_count = 0  # Initialize cumulative day count

    for _, row in baseline_data.iterrows():
        month_index, days_in_month = month_to_index(row['Month'])
        for day in range(1, days_in_month + 1):
            daily_row = row.to_dict()
            daily_row['Day'] = day
            cumulative_day_count += 1  # Increment cumulative day count for each new day
            daily_row['Cumulative Day'] = cumulative_day_count
            daily_row['Month Index'] = month_index
            daily_row['Total Cases'] /= days_in_month
            daily_row['Contact Center COST'] /= days_in_month
            daily_data.append(daily_row)
    
    return pd.DataFrame(daily_data)
