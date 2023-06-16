# File Documentation
In this document, one can find the documentation and structure of the project. Furthermore, all the classes and functions are explained in detail. Inheritance of classes is also explained in this document. For more information about the project, please read the [README.md](www.github.com) file. 

## Table of Contents
1. [File Structure](#file-structure)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [Aimsun](#aimsun)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [Data](#data)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [Environment](#environment)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [Pipeline](#pipeline)

2. [Functions/Classes](#Function/Classes)
   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [Open_files.py](#Open_filespy)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [Aimsun_parameters.py](#aimsun_parameterspy)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [AV_Aimsun_parameters.py](#AV_Aimsun_parameterspy)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [HighD_parameters.py](#HighD_parameterspy)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [Simulation_error.py](#Simulation_errorpy)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [PartialAutomationKL.py](#Partialautomationklpy)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [PenetrationRate.py](#PenetrationRatepy)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [SensitivityAnalysis.py](#SensitivityAnalysispy)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [AV_analysis_1.ipynb](#AV_analysis_2ipynb)

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- [AV_analysis_2.ipynb](#AV_analysis_2ipynb)




## File Structure 
The file structure of the project to use is as follows:

```
.
├── README.md
├── documentation.md
├── Aimsun
│   ├── Model
│   │   ├── AimsunModel.ang
│   │   ├── Results
│   │   │    └── AimsunModel.sqlite
│   │   └── AV-penetration
│   │       ├── Aimsun model
│   │       │   └── AVAimsunModel.ang
│   │       ├── Assertive
│   │       ├── Cautious
│   │       └── Auto-AV
│   │           ├── Assertive
│   │           └── Cautious
│   └── Micro API
│       ├── PenetrationRate.py
│       └── SensitivityAnalysis.py
├── data
│   └── HighD data - extracted files
├── environment
│   └── environment.yml
└── Pipeline
    ├── results.csv
    ├── AV_analysis_1.ipynb
    ├── AV_analysis_2.ipynb
    ├── run_calibration.ipynb
    ├── aimsun_parameters.py
    ├── AV_aimsun_parameters.py
    ├── HighD_parameters.py
    ├── open_files.py
    ├── PartialAutomationKL.py
    └── simulation_error.py


```

### Aimsun
Aimsun Folder will contain all the files that will be used for Aimsun Next 22. This folder will contain the model that will be used and also the results of that simulation. Moreover, it contains a folder pertaining to the AV Analysis, and the model used for this task.

From this folder, the model can be opened in Aimsun Next 22. 
The results will be read from the AimsunModel.sqlite file, which is located in the results folder. How the data is read from this file is explained in the [aimsun_parameters.py](#Aimsun_parameters.py) file.

The model is created in Aimsun Next 22. The model is created in the following way:
1. Create a new file
2. Create a new network based on the physical map of the dataset used.
3. Create a new dynamical scenario based on the network created in step 2.
4. Create a new demand based on the scenario created in step 3.
5. Create a new simulation based on the demand created in step 4.
6. Run the simulation --> This will create the results file.

### Data
The data folder will contain all the data that is used for the project. This data is extracted from the HighD dataset. The data is extracted in the following way:
1. Download the HighD dataset from the [HighD website](https://www.highd-dataset.com/).
2. Extract the data from the HighD dataset in this folder (meaning all files -> [XX_highway.png, XX_recordingMeta.csv, XX_tracks.csv, XX_tracksMeta.csv])

### Environment
The environment folder will contain the environment.yml file. This file can be used to create a conda environment. This environment will contain all the packages that are needed to run the project.

### Pipeline
The pipeline folder will contain all the Python scripts that are used for the project. These scripts are explained in detail in the [Python-Scripts](#python-scripts) section.

## Functions/Classes
The class hierarchical structure is given by 
```
PartialAutomationKL
└── SPSA
    ├── AimsunData
    └── HighDData
        └── open_files (function) 
```

### Open_files.py
This file contains the function `open_files` which is used to open the HighD data files in the data folder. The function has the following inputs:
- `all_files`: a string that contains if the user wants to use all the files, default is 'n'-> no. The other input possibility is 'y'-> yes. 
- `file_numbers_input`: a string that contains the file numbers that the user wants to use. The default is '1'-> data file 1. The other input possibility is a string with the file numbers separated by a comma. For example '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15', which will load datasets 1-15.

### Aimsun_parameters.py
This file contains the class `AimsunData` which is used to extract data and compute the parameters of interest(POI) from the SQLite output from the Aimsun simulation.
The class has the following functions:

- `__init__`: The constructor of the class. It takes the name of the SQLite file as input and calls `getconnection` function to get the connection to the database.
- `getconnection`: This function takes the name of the SQLite file as input and returns the connection to the database.
- `change_connection`: This function changes the connection to the database. It takes the name of the SQLite file as input and calls `getconnection` function to get the connection to the database.
- `close_connection`: This function closes the connection to the database.
- `_getCarSpeedAimsun`: This function extracts and returns the speed of the cars as a list.
- `_getTruckSpeedAimsun`: This function extracts and returns the speed of the trucks as a list.
- `_getDensityAimsun`: This function extracts and returns the traffic density as a list.
- `_getLeaderAimsun`: This function extracts and returns the parameters(followerID, distance, timeStamp, speedDifference) necessary to calculate the TTC and DRAC as a pandas dataframe "leaderTable".
- `_getTTCAimsun`: This function takes the dataframe "leaderTable" to calculate the minimum TTC per vehicle.
- `_getDRACAimsun`: This function takes the dataframe "leaderTable" to calculate the maximum DRAC per vehicle.
- `Aggregated_Aimsun_values`: This functions uses the 5 functions above to calculate the  form the database and return them as a dictionary.

### AV_Aimsun_parameters.py
Similar to aimsun_parameters.py, however, the SQL queries defined in the following functions were modified to include the AV vehicle IDs:
- `_getCarSpeedAimsun`: This function extracts and returns the speed of the cars and AVs as a list.

### HighD_parameters.py
This file contains the class `HighDData` which is used to extract data and compute the parameters of interest(POI) from the CSV files from the HighD dataset.
The class has the following functions:

- `__init__`: It is the constructor of the class. It takes the name of the CSV files as input and calls the functions to read the CSV files. The data and metadata are merged into one dataframe.
- `_getCarSpeedHighD1Dir`: This function extracts and returns the speed of the cars in one direction as a list.
- `_getTruckSpeedHighD1Dir`: This function extracts and returns the speed of the trucks in one direction as a list.
- `_getDensityHighD`: This function extracts and returns the traffic density as a list. The calculation is based on the Aimsun documentation (Density of a section DEN<sub>sec</sub> https://docs.aimsun.com/next/22.0.1/UsersManual/CalculationOfTrafficStatistics.html).
- `_getTTC1DirHighD`: This function extracts and returns the minimum TTC per vehicle in one direction as a list.
- `_compDRACHighD`: This function extracts and returns the DRAC as a dataframe.
- `_getDRAC1DirHighD`: This function extracts and returns the maximum DRAC per vehicle in one direction as a list.
- `Aggregated_HighD_values`: This function uses the 6 functions above to calculate the POI and return them as a dictionary.

### Simulation_error.py
This file contains the class `SPSA` which is used to compute the loss between the simulation and the data. The class has the following functions:
- `__init__`: The constructor of the class. It takes the name of the SQLite file as input and calls `getconnection` function to get the connection to the database.
- `KL_divergence`: This function takes the data and simulation as input and returns the KL divergence between the two as a float.
- `param_clip`: This function takes the parameters as input and clips them to the range of the parameters based on the literature.
- `get_new_params`: This function determines the new testing parameters based on the current parameters and random values (perturbation). 
- `update_params`: This function takes the parameters as input and returns the new parameters based on the SPSA algorithm using the KL_divergence loss.

This class inherits functions from the `AimsunData` and `HighDData` classes. These functions are explained in the [aimsun_parameters.py](#Aimsun_parameterspy) and [HighD_parameters.py](#HighD_parameterspy) files.

### PartialAutomationKL.py
This file contains the class `PartialAutomationKL` which uses the Class SPSA. The PartialAutomationKL class is an overarching class that contains the functions to run the simulation and compute the error and store these results. 

The class has the following functions:
- `__init__`: The constructor of the class. It takes the name of the SQLite file as input and calls `getconnection` function to get the connection to the database.
- `read_csv`: This function takes the name of the CSV file as input and returns the data in the CSV file as a pandas dataframe. This data can be called using self.results. If the path is empty, the function will return an empty dataframe.
- `write_to_csv`: This function takes the name of the CSV file as input and writes the data in the self.results dataframe to the CSV file. If the path is empty, the function will not write the data to a CSV file and prints an error message.
- `_preset_values`: This function sets initial preset values for calibration. If parameters must be changed use this function to change the preset values.
- `load_from_dict`: This function loads the set parameters from the results file. If the results file is empty, the function will raise an AssertionError.
- `SPSA_Iteration`: This function is called to run a calibration of a system. The function has as input write_to_csv, which is a boolean that determines if the results should be written to a CSV file. The function will store everything internally. If write_to_csv is True, the results will be written to a CSV file using `write_to_csv`. If write_to_csv is False, the results will not be written to a CSV file.

This class inherits from the following classes:
- `SPSA`: This class contains the SPSA algorithm. This class is used to compute the next parameter values. This class is explained in detail in the [SPSA](#Simulation_errorpy) section. SPSA uses the following classes:
    - `AimsunData`: This class is used to extract data from the Aimsun simulation. This class is explained in detail in the [aimsun_parameters.py](#Aimsun_parameterspy) section.
    - `HighDData`: This class is used to extract data from the HighD dataset. This class is explained in detail in the [HighD_parameters.py](#HighD_parameterspy) section. This class also uses the function `open_files` which is explained in detail in the [open_files.py](#Open_filespy) section.

### AV_analysis_1.ipynb
This file contains the class `AV_analysis` which is used to extract data and compute graphs from the SQLite output of the Aimsun simulation with the AV.

The class has the following functions:
- `__init__`: The constructor of the class. It takes the name of the SQLite file as input and calls `getconnection` function to get the connection to the database.
- `AV_params`: Calls the `Aggregated_Aimsun_values` function in the AV_Aimsun_parameters.py file that calculates the form of the database and returns them as a dictionary.

This class inherits from the class [AV_Aimsun_parameters.py](#avaimsun_parameterspy).

### AV_analysis_2.ipynb
This file contains the class `AV_analysis` which is used to extract data and compute graphs from the SQLite output of the Aimsun simulation with the AV.

The class has the following functions:
- `__init__`: The constructor of the class. It takes the name of the SQLite file as input and calls `getconnection` function to get the connection to the database.
- `AV_params`: Calls the `Aggregated_Aimsun_values` function in the AV_Aimsun_parameters.py file that calculates the form of the database and returns them as a dictionary.

This class inherits from the class [AV_Aimsun_parameters.py](#avaimsun_parameterspy).

### PenetrationRate.py
This file is used in Aimsun Next as an executable Script and contains a number of functions used to automatically compute multiple Aimsun replications at different penetration rates using the AV Aimsun Model.
These functions are:
- `getVehicleObject`: This function returns a vehicle object based on its ID.
- `setVehicleObject`: This function sets a vehicle object type into the OD matrix.
- `apply_replication`: This function runs a replication in Aimsun Next based on the replication ID.
- `change_database_name`: This function changes the output trajectory file directory in Aimsun Next.
- `changeFactorDemand`: This function changes the factor demand for each traffic demand item.
- `changeFactor`: This function gets the GKTrafficDemand object based on its ID and calls the `changeFactorDemand` function.

### SensitivityAnalysis.py
This file is used in Aimsun Next as an executable Script and contains a number of function calls to automatically modify a number of parameters in the Aimsun Model, in order to execute the Sensitivity Analysis. This file needs to be extended to modify all relevant parameters of the Sensitivity Analysis and automate the replication execution. The following resource can be used (Aimsun Next Scripting<sub>sec</sub> https://docs.aimsun.com/next/22.0.1/UsersManual/ScriptLibrary.html)
