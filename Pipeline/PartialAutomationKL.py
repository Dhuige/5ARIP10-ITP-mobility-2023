import os
import pandas as pd
from simulation_error import *


class KL_automation(SPSA):
    """
    The SPSA iteration method is used to optimize the Aimsun parameters.
    The storing and reading and writing of KL-tests is performed using this class. 
    """
    # IF we have an API switch this with the init such that we can automate this. 
    # by running preset values and changing these over runs or random initial state within a range.

    def __init__(self, filename1, filename2, file_input:str = '1'):
        super().__init__(filename1, filename2, file_input=file_input)
        
        try:
            self.c1
        except AttributeError:
            self.getconnection(filename1, filename2)
        
        # self._getAimsunValues()
        self._preset_values()

        # Define database file paths
        self.PIPELINE_DIR = os.getcwd()
        # Mself_DIR = os.path.join("..",PIPELINE_DIR)
        self.FILELOC_results = os.path.join(self.PIPELINE_DIR,"results.csv")
        
        self.read_csv()

        self.amp = [5, 3, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05, 0.1, 0.1, 10, 5, 0.2, 0.2]
        self.alpha = 0.01
        self.iteration = 1
    
    
    def read_csv(self)->None:
        """Read the CSV results file and check if it exists
        
        Parameters:
            None
            
        Returns:
            None -> self.results is updated with the results of the CSV file
        """

        # Check if the file exists
        if os.path.isfile(self.FILELOC_results) == True:
            print("Results file is being read")
            self.results = pd.read_csv(self.FILELOC_results, index_col=0)
        else:
            print("Save file did not exist, a new file will be created after running write_to_csv of this class")
            self.results = pd.DataFrame()
    
    def write_to_csv(self, FILELOC_results:str)->None:
        """Saves the results to a filelocation
        
        Parameters:
            FILELOC_results (str): File location to save the results to
        
        Returns:
            None -> writes to a csv file (directly store data)"""
        
        # Test if given location is a string and non-empty
        if type(FILELOC_results) != str:
            raise NameError("File is not a string")
        elif not FILELOC_results: # If not empty (Falsy variable)
            raise TypeError("File location provided is empty")
        else:
            self.results.to_csv(FILELOC_results) # writes file to csv

    def _preset_values(self):
        """Function sets preset values, note this is bad since it will nolonger accurately depict from input
        
        Parameters:
            None
        
        Returns:
            None -> self.params is updated with the preset values
        """

        CarMaxdesiredSpeed = 130
        TruckMaxdesiredSpeed = 88
        CarMaxAcceleration = 3.0
        TruckMaxAccerlation = 1.0
        CarNormalDeceleration = 4.0
        TruckNormalDeceleration = 3.0
        CarSensitivityFactor = 0.5  
        TruckSensistivityFactor = 0.5
        CarReactionTime = 1.0
        TruckReactionTime = 1.0
        CarVehicleDemand = 505
        TruckVehicleDemand = 90
        CarGap = 2.0
        TruckGap = 2.0
        
        params = [CarMaxdesiredSpeed, TruckMaxdesiredSpeed, CarMaxAcceleration, TruckMaxAccerlation, CarNormalDeceleration,
                        TruckNormalDeceleration, CarSensitivityFactor, TruckSensistivityFactor, CarReactionTime, TruckReactionTime,
                        CarVehicleDemand, TruckVehicleDemand, CarGap, TruckGap]

        self.params = params

    def load_from_dict(self, location:int):
        """Load the results from a dictionary (From results file)

        Parameters:
            location: the location from which the results are to be loaded (index of the dataframe)
        
        Returns:
            None -> self.results is updated with the results of the dictionary
        """
        results = self.results.loc[location]
        CarMaxdesiredSpeed = results["CarMaxdesiredSpeed"]
        TruckMaxdesiredSpeed = results["TruckMaxdesiredSpeed"]
        CarMaxAcceleration = results["CarMaxAcceleration"]
        TruckMaxAccerlation = results["TruckMaxAccerlation"]
        CarNormalDeceleration = results["CarNormalDeceleration"]
        TruckNormalDeceleration = results["TruckNormalDeceleration"]
        CarSensitivityFactor = results["CarSensitivityFactor"]
        TruckSensistivityFactor = results["TruckSensistivityFactor"]
        CarReactionTime = results["CarReactionTime"]
        TruckReactionTime = results["TruckReactionTime"]
        CarVehicleDemand = results["CarVehicleDemand"]
        TruckVehicleDemand = results["TruckVehicleDemand"]
        CarGap = results["CarGap"]
        TruckGap = results["TruckGap"]

        params = [CarMaxdesiredSpeed, TruckMaxdesiredSpeed, CarMaxAcceleration, TruckMaxAccerlation, CarNormalDeceleration,
                        TruckNormalDeceleration, CarSensitivityFactor, TruckSensistivityFactor, CarReactionTime, TruckReactionTime,
                        CarVehicleDemand, TruckVehicleDemand, CarGap, TruckGap]
        
        self.params = params      
    
    def SPSA_Iteration(self, write_to_csv:bool=True):
        """
        Write the Aimsun input parameters and the results of the KL test to the file location given by FILELOC_results.
        Parameters:
            write_to_csv: 1 if you want to write to csv, 0 if you don't want to write to csv
        
        Returns:
            None -> self.results is updated with the results of the CSV file
            if write_to_csv == True: writes to a csv file (directly store data)
        """

        # Get data and storage
        new_row = {}

        # Make sure that our delta change will slow down after many iterations.
        self.iteration += 1
        if self.iteration%5==0:
            self.alpha/=5

        self.get_new_params(self.params, self.amp)
        new_filename1 = input("Name of first params file results: ")
        new_filename2 = input("Name of second params file results: ")
        self.change_connection(new_filename1, new_filename2)
        nparams, params, loss = self.update_params(self.params, alpha=self.alpha)

        # Add Data as input
        desired_speed_dict = {"CarMaxdesiredSpeed":params[0], "TruckMaxdesiredSpeed":params[1]} 
        new_row.update(desired_speed_dict)
        max_acceleration_dict = {"CarMaxAcceleration":params[2], "TruckMaxAccerlation":params[3]}
        new_row.update(max_acceleration_dict)
        Normal_deceleration_dict = {"CarNormalDeceleration":params[4], "TruckNormalDeceleration":params[5]}
        new_row.update(Normal_deceleration_dict)
        SensitivityFactor_dict = {"CarSensitivityFactor":params[6], "TruckSensistivityFactor":params[7]}
        new_row.update(SensitivityFactor_dict)
        Reaction_time_dict = {"CarReactionTime":params[8], "TruckReactionTime":params[9]}
        new_row.update(Reaction_time_dict)
        Vehicle_demand_dict = {"CarVehicleDemand":params[10], "TruckVehicleDemand":params[11]}
        new_row.update(Vehicle_demand_dict)
        Gap_dict = {"CarGap":params[12], "TruckGap":params[13]}
        new_row.update(Gap_dict)
        loss_dict = {"Loss":loss, "sumloss":sum(loss)}

        new_row.update(loss_dict)
        
        # Create a new PD if needed
        if self.results.empty:
            self.results = pd.DataFrame([new_row])
        else:
            self.results = pd.concat([self.results,pd.DataFrame([new_row])], ignore_index=True)

        if write_to_csv == True:
            self.write_to_csv(self.FILELOC_results)
        
        # Update Params after the loop
        self.params = self.param_clip(nparams)  