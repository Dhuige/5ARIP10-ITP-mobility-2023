from open_files import *
import numpy as np

class HighDData():
    """
    Class to store and compute parameters for HighD data
    Parameters:
        Carspeed, Truckspeed, Intensity, Density, TTC, DRAC
    """

    def __init__(self, all_files:str='n', file_input:str = '1')->None:
        """
        Initialize the HighDData class by importing the requested data

        Parameters:
            all_files (str): Whether to import all files or only one file ('y'/'n')
            file_input (str): File number to import (if all_files = 'n')

        Returns:
            None -> data imported and stored in class variables: data_merged, trackMeta_dict, recordMeta_dict

        NOTE: file_input can import multiple files by separating with commas -> '1,2,3'
        """

        # Import HighD data and merge meta
        self.file_numbers, self.data_dict, self.trackMeta_dict, self.recordMeta_dict = read_files(all_files, file_input)

        if len(self.file_numbers)==1:
            num = self.file_numbers[0]
        else:
            num = input(f"Which file number do you want to calculate the parameters for? {self.file_numbers}")
        
        # Store data in class variables
        self.data_dict = pd.DataFrame(self.data_dict[f"data_{num}"])
        self.trackMeta_dict = pd.DataFrame(self.trackMeta_dict[f"data_{num}"])
        self.recordMeta_dict = pd.DataFrame(self.recordMeta_dict[f"data_{num}"])

        # Merge data and meta
        self.data_merged = pd.merge(self.data_dict, self.trackMeta_dict[["id", "class", "drivingDirection"]], on="id")

        # Check if data is loaded
        if self.data_merged is None:
            raise ValueError("self.data_merged is not loaded")
        if self.trackMeta_dict is None:
            raise ValueError("Track meta data is not loaded")
        if self.recordMeta_dict is None:
            raise ValueError("Record meta data is not loaded")
    
    def _getCarSpeedHighD1Dir(self, dir:int = 1)->list:
        """
        returns the carspeeds for one of the given input directions

        Parameters:
            dir (int): Driving direction (1 or 2)
        
        Returns:
            car_speed (list): List of car speeds
        """
        if dir not in [1,2]:
            raise ValueError("Driving direction must be 1 or 2")

        cars_dir = self.data_merged.loc[(self.data_merged["class"] == "Car") & (self.data_merged["drivingDirection"] == dir)]

        # m/s to km/h
        car_xSpeed = cars_dir["xVelocity"]*3.6
        car_ySpeed = cars_dir["yVelocity"]*3.6

        # Calculate speed
        car_speed = list(np.sqrt(car_xSpeed**2 + car_ySpeed**2))

        return car_speed

    def _getTruckSpeedHighD1Dir(self, dir:int = 1)->list:
        """
        Returns the speed of trucks in the specified direction
        
        parameters:
            dir (int): Driving direction (1 or 2)

        returns:
            truck_speed (list): List of truck speeds
        """
        if dir not in [1,2]:
            raise ValueError("Driving direction must be 1 or 2")
        
        trucks_dir = self.data_merged.loc[(self.data_merged["class"] == "Truck") & (self.data_merged["drivingDirection"] == dir)]
        truck_xSpeed = trucks_dir["xVelocity"]*3.6
        truck_ySpeed = trucks_dir["yVelocity"]*3.6
        truck_speed = np.sqrt(truck_xSpeed**2 + truck_ySpeed**2)

        return truck_speed
    
    def _getDensityHighD(self)->list:
        """
        Returns the density of the traffic
        (The density calculation is based on the Aimsun calculation: https://docs.aimsun.com/next/22.0.1/UsersManual/CalculationOfTrafficStatistics.html)

        parameters:
            NOTE: The density is calculated for the whole road (both directions) and the input parameters depend on the road geometry these have to be filled in manually by the user in the function itself.

        returns:
            densities (list): List of densities
        """
        # Input parameters
        x1 = 0
        x2 = 400*2 # 2 lanes
        lane_length = x2 - x1

        time_span = 900 # seconds
        time_interval = 15 # seconds

        densities = []

        for t in range(0, time_span, time_interval):
            # Calculating Forward Traffic Flow
            mask = (self.data_dict["frame"] >= t * self.recordMeta_dict["frameRate"][0]) & (self.data_dict["frame"] < (t + time_interval) * self.recordMeta_dict["frameRate"][0]) & (self.data_dict["x"] >= x1) & (self.data_dict["x"] <= x2)
            vehicles = self.data_dict[mask & (self.data_dict["y"] >= 8.51) & (self.data_dict["y"] <= 12.59)]["id"].unique()
            count = len(vehicles)

            density = count / lane_length * 1000
            densities.append(density)

        return densities
    
    def _getTTC1DirHighD(self, direction:int = 1)->list:
        """
        Returns the minimum TTC for the specified direction
        
        parameters:
            direction (int): Driving direction (1 or 2)

        returns:
            minTTC (list): List of minimum TTCs
        """
        if direction not in [1,2]:
            raise ValueError("Driving direction must be 1 or 2")
        
        minTTC = self.trackMeta_dict[(self.trackMeta_dict["drivingDirection"] == direction) & (self.trackMeta_dict["minTTC"]>=0)]["minTTC"]
        
        return list(minTTC)  

    def _compDRACHighD(self)->None:
        """Computes DRAC and stores the data in the data_merged table
        
        Parameters:
            None
        
        Returns:
            None -> Stores the data in the data_merged table"""
        delxvel = (self.data_merged["precedingXVelocity"] - self.data_merged["xVelocity"])
        self.data_merged["DRAC"] = delxvel**2/(self.data_merged["dhw"])
        self.data_merged["DRAC"].replace([np.inf, -np.inf], np.nan, inplace=True)

    def _getDRAC1DirHighD(self, direction = 1):
        """
        Returns the maximum DRAC for the specified direction

        Parameters:
            direction (int): Driving direction (1 or 2)

        Returns:
            maxDRAC (list): List of maximum DRACs
        """
        if direction not in [1,2]:
            raise ValueError("Driving direction must be 1 or 2")
        
        maxDRAC = []

        try:
            maxDRAC = self.data_merged.loc[(self.data_merged['drivingDirection']==direction) & (self.data_merged.DRAC.eq(self.data_merged.groupby('id').DRAC.transform('max')))]["DRAC"]
        except:
            self._compDRACHighD()
            maxDRAC = self.data_merged.loc[(self.data_merged['drivingDirection']==direction) & (self.data_merged.DRAC.eq(self.data_merged.groupby('id').DRAC.transform('max')))]["DRAC"]

        maxDRAC = [x for x in maxDRAC if not np.isnan(x)]

        return maxDRAC
    
    def Aggregated_HighD_values(self, direction:int = 1)->dict:
        """
        Compute the aggregated parameters for the specified direction as a dictionary

        Parameters:
            direction (int): Driving direction (1 or 2)

        Returns:
            HighD_values (dict): Dictionary of aggregated parameters
        """
        if direction not in [1,2]:	
            raise ValueError("Driving direction must be 1 or 2")
        
        HighD_values = {}
        HighD_values["TTC"] = self._getTTC1DirHighD(direction=direction)
        HighD_values["DRAC"] = self._getDRAC1DirHighD(direction=direction)        
        HighD_values["Density"] = self._getDensityHighD()
        HighD_values["Car_speed"] = self._getCarSpeedHighD1Dir(dir=direction)
        HighD_values["Truck_speed"] = self._getTruckSpeedHighD1Dir(dir=direction)
        return HighD_values
