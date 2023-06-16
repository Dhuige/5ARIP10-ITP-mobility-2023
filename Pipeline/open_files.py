# Import libraries
import os
import pandas as pd

def read_files(all_files:str='n', file_numbers_input:str='1'):
    """
    Read files to dictionary

    Parameters:
        all_files (str): Whether to import all files or only one file ('y'/'n')
        file_input (str): File number to import (if all_files = 'n')

    Returns if 'y':
        file_numbers_list (list), reference numbers to the files imported
        data_dict (dict): Dictionary with trajectory data

    Returns 'n':	
        file_numbers_list
        data_dict (dict): Dictionary with trajectory data
        trackMeta_dict (dict): Dictionary with track meta data
        recordMeta_dict (dict): Dictionary with record meta data

    NOTE: file_input can import multiple files by separating with commas -> '1,2,3'
    """

    # Read files to dictionary
    data_path = ".\..\..\Data\highd-dataset-v1.0\data"
    data_dict = {}
    data_dict_meta = {}
    data_dict_tracksmeta = {}

    if all_files == "y":
        n_files = 60
        for i in range(n_files):
            print(f"reading file {i+1}/{n_files}...\r", end="")
            file_name = f"{i+1:02d}_tracks.csv"
            file_path = os.path.join(data_path, file_name)
            data_dict[f"data_{i+1}"] = pd.read_csv(file_path)
        return [list(range(1,n_files+1)), data_dict]

    elif all_files == "n":
        file_numbers_list = [int(i) for i in str.split(file_numbers_input, ',')]
        for i in file_numbers_list:
            file_name = f"{i:02d}_tracks.csv"
            file_path = os.path.join(data_path, file_name)
            data_dict[f"data_{i}"] = pd.read_csv(file_path)

            file_name= f"{i:02d}_recordingMeta.csv"
            file_path = os.path.join(data_path, file_name)
            data_dict_meta[f"data_{i}"] = pd.read_csv(file_path)

            file_name= f"{i:02d}_tracksMeta.csv"
            file_path = os.path.join(data_path, file_name)
            data_dict_tracksmeta[f"data_{i}"] = pd.read_csv(file_path)
            
        
        return [file_numbers_list, data_dict, data_dict_tracksmeta, data_dict_meta]
            
    else:
        print('''The input was not valid. Please enter "y" or "n".''')