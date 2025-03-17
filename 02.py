import pandas as pd
import numpy as np
import time
from datetime import datetime
from scipy.stats import variation
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import csv
import os
import glob

# Function to get all CSV filenames in a directory
def get_csv_filenames(directory):
    os.chdir(directory)
    return [i for i in glob.glob("*.csv")]

# Function to identify event and non-event tables
def identify_event_tables(all_filenames):
    event_table = []
    non_event_table = []
    time_cols_dict = {}
    time_cols = []
    get_c = []

    for file in all_filenames:
        df = pd.read_csv(file, nrows=10000, low_memory=False)
        is_time_format = df.astype(str).apply(lambda x: x.str.match(r'\d{2,4}-\d{2}-\d{2,4} \d{2}\:\d{2}\:\d{2}').all())
        df.loc[:, is_time_format] = df.loc[:, is_time_format].apply(pd.to_datetime)
        is_time_columns = df.select_dtypes(include='datetime')
        if not is_time_columns.empty:
            for c in is_time_columns.columns:
                c_max = is_time_columns[c].astype(str).str.len().max()
                get_c.append(c_max)
    get_max = max(get_c)

    for file in all_filenames:
        df = pd.read_csv(file, low_memory=False)
        target_type = df.select_dtypes(include=['object', 'datetime'])
        temp_timecols = []
        for column in target_type:
            col_max = df[column].astype(str).str.len().max()
            test = df[~df[column].isnull()]
            test1 = test[column]
            col_min = test1.astype(str).str.len().min()
            gap = col_max - col_min
            if (col_max == get_max or col_min == get_max) and (gap == 0 and column != 'DOB'):
                temp_timecols.append(column)
                time_cols.append(column)
        is_time_format = df.astype(str).apply(lambda x: x.str.match(r'\d{2,4}-\d{2}-\d{2,4} \d{2}\:\d{2}\:\d{2}').all())
        df.loc[:, is_time_format] = df.loc[:, is_time_format].apply(pd.to_datetime)
        is_time_columns = df.select_dtypes(include='datetime')
        temp_cols = list(is_time_columns.columns)
        for i in temp_cols:
            if i == 'DOB':
                temp_cols.remove('DOB')
        temp_timecols.extend(temp_cols)
        temp_timecols0 = list(set(temp_timecols))
        if temp_timecols0:
            time_cols_dict[file] = temp_timecols0
            event_table.append(file)
        else:
            non_event_table.append(file)

    return event_table, non_event_table, time_cols_dict, time_cols

# Function to suggest primary keys from non-event tables
def suggest_primary_keys(non_event_table):
    sug_pm_keys = []
    for file in non_event_table:
        df = pd.read_csv(file, low_memory=False)
        ob_type = df.select_dtypes(include=['integer', 'object'])
        row_count = len(df.index)
        temp_count_list = []
        temp_colList = []
        for col in ob_type:
            check = len(df[col].unique())
            temp_count_list.append(check)
            temp_colList.append(col)
        loc = temp_count_list.index(max(temp_count_list))
        sug_pm_keys.append(temp_colList[loc])
    return sug_pm_keys

# Function to suggest case IDs from event tables
def suggest_case_ids(event_table, timestamp_list, sug_pm_keys):
    caseID = []
    sug_caseID = []
    for file in event_table:
        df = pd.read_csv(file, nrows=10000, low_memory=False)
        ob_int_type = df.select_dtypes(include=['integer'])
        null_count = df.isnull().sum()
        null_list = np.array(null_count).tolist()
        df_nullcount = pd.DataFrame(list(zip(ob_int_type, null_list)))
        df_nullcount.columns = ['Column Name', 'x']
        filter_null = df_nullcount[df_nullcount['x'] < 10]
        no_null_cols = df_nullcount['Column Name'].tolist()
        for column in ob_int_type:
            col_max = df[column].astype(str).str.len().max()
            col_min = df[column].astype(str).str.len().min()
            gap = col_max - col_min
            check = len(df[column].unique())
            if col_max > 1 and gap == 0:
                if column not in timestamp_list:
                    caseID.append(column)
    sug_caseID = list(dict.fromkeys(caseID))
    caseID = [element for element in sug_caseID if element not in sug_pm_keys]
    return caseID

# Main function to execute the process
def main():
    address = input("Folder location for data tables (*.csv): ")
    all_filenames = get_csv_filenames(address)
    event_table, non_event_table, time_cols_dict, time_cols = identify_event_tables(all_filenames)
    sug_pm_keys = suggest_primary_keys(non_event_table)
    caseID = suggest_case_ids(event_table, time_cols, sug_pm_keys)
    print('Event tables are:', event_table)
    print('Non-event tables are:', non_event_table)
    print('Suggested primary keys from non-event tables:', sug_pm_keys)
    print('Case IDs are:', caseID)

if __name__ == "__main__":
    main()
