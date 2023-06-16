# Import libraries
import os
import pandas as pd

def read_files():
    # Ask which files to read
    all_files = input("Do you want to read all files (y/n)?")

    # Read files to dictionary
    data_path = ".\..\..\Data\highd-dataset-v1.0\data"
    data_dict = {}
    trackMeta_dict = {}
    recordMeta_dict = {}

    if all_files == "y":
        n_files = 60
        for i in range(n_files):
            print(f"reading file {i+1}/{n_files}...\r", end="")
            file_name = f"{i+1:02d}_tracks.csv"
            file_path = os.path.join(data_path, file_name)
            data_dict[f"data_{i+1}"] = pd.read_csv(file_path)

            file_name2 = f"{i+1:02d}_tracksMeta.csv"
            file_path2 = os.path.join(data_path, file_name2)
            trackMeta_dict[f"data_{i+1}"] = pd.read_csv(file_path2)

            file_name3 = f"{i+1:02d}_recordingMeta.csv"
            file_path3 = os.path.join(data_path, file_name3)
            recordMeta_dict[f"data_{i+1}"] = pd.read_csv(file_path3)
        
        return list(range(1,n_files+1)), data_dict, trackMeta_dict, recordMeta_dict

    elif all_files == "n":
        file_numbers_input = input("What file numbers do you want to read? Give numbers separated by commas.")
        file_numbers_list = [int(i) for i in str.split(file_numbers_input, ',')]
        j=1
        for i in file_numbers_list:
            print(f"reading file {j}/{len(file_numbers_list)} ({i})...\r", end="")
            file_name = f"{i:02d}_tracks.csv"
            file_path = os.path.join(data_path, file_name)
            data_dict[f"data_{i}"] = pd.read_csv(file_path)

            file_name2 = f"{i:02d}_tracksMeta.csv"
            file_path2 = os.path.join(data_path, file_name2)
            trackMeta_dict[f"data_{i}"] = pd.read_csv(file_path2)

            file_name3 = f"{i:02d}_recordingMeta.csv"
            file_path3 = os.path.join(data_path, file_name3)
            recordMeta_dict[f"data_{i}"] = pd.read_csv(file_path3)

            j+=1
        return file_numbers_list, data_dict, trackMeta_dict, recordMeta_dict
            
    else:
        print('''The input was not valid. Please enter "y" or "n".''')