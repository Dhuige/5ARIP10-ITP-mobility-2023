from AAPI import *
from scipy import ks_2samp
import pandas as pd
import numpy as np
import os 

def read_files():
    # Ask which files to read
    all_files = 'n' #input("Do you want to read all files (y/n)?")

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
        return list(range(1,n_files+1)), data_dict

    elif all_files == "n":
        file_numbers_input = '1' #input("What file numbers do you want to read? Give numbers separated by commas.")
        file_numbers_list = [int(i) for i in str.split(file_numbers_input, ',')]
        j=1
        for i in file_numbers_list:
            print(f"reading file {j}/{len(file_numbers_list)} ({i})...\r", end="")
            file_name = f"{i:02d}_tracks.csv"
            file_path = os.path.join(data_path, file_name)
            data_dict[f"data_{i}"] = pd.read_csv(file_path)

            file_name= f"{i:02d}_recordingMeta.csv"
            file_path = os.path.join(data_path, file_name)
            data_dict_meta[f"data_{i}"] = pd.read_csv(file_path)

            file_name= f"{i:02d}_tracksMeta.csv"
            file_path = os.path.join(data_path, file_name)
            data_dict_tracksmeta[f"data_{i}"] = pd.read_csv(file_path)
            
            j+=1
        
        return file_numbers_list, data_dict, data_dict_tracksmeta, data_dict_meta
            
    else:
        print('''The input was not valid. Please enter "y" or "n".''')

class HighDData():
    def __init__(self):
        # Import HighD data and merge meta
        self.file_numbers, self.data_dict, self.trackMeta_dict, self.recordMeta_dict = read_files()

        if len(self.file_numbers)==1:
            num = self.file_numbers[0]
        else:
            num = input(f"Which file number do you want to calculate the parameters for? {self.file_numbers}")
        self.data_dict = pd.DataFrame(self.data_dict[f"data_{num}"])
        self.trackMeta_dict = pd.DataFrame(self.trackMeta_dict[f"data_{num}"])
        self.recordMeta_dict = pd.DataFrame(self.recordMeta_dict[f"data_{num}"])

        self.data_merged = pd.merge(self.data_dict, self.trackMeta_dict[["id", "class", "drivingDirection"]], on="id")
    
    def getCarSpeed(self):
        # Split cars based on driving direction
        cars_dir1 = self.data_merged.loc[(self.data_merged["class"] == "Car") & (self.data_merged["drivingDirection"] == 1)]
        cars_dir2 = self.data_merged.loc[(self.data_merged["class"] == "Car") & (self.data_merged["drivingDirection"] == 2)]
        car_xSpeed = cars_dir1["xVelocity"]
        car_ySpeed = cars_dir1["yVelocity"]
        car_ids = list(cars_dir1["id"])
        car_speed = list(np.sqrt(car_xSpeed**2 + car_ySpeed**2))

        return car_speed, car_ids

    def getTruckSpeed(self):
        # Split trucks based on driving direction
        trucks_dir1 = self.data_merged.loc[(self.data_merged["class"] == "Truck") & (self.data_merged["drivingDirection"] == 1)]
        trucks_dir2 = self.data_merged.loc[(self.data_merged["class"] == "Truck") & (self.data_merged["drivingDirection"] == 2)]
        truck_xSpeed = trucks_dir1["xVelocity"]
        truck_ySpeed = trucks_dir1["yVelocity"]
        truck_speed = np.sqrt(truck_xSpeed**2 + truck_ySpeed**2)

        return truck_speed
    
    def getIntensity(self):
        time_span = 1500 # seconds
        time_interval = 15 # seconds
        x1 = 0
        x2 = 400
        counts1 = []

        for t in range(0, time_span, time_interval):
            # Calculating Forward Traffic Flow
            mask1 = (self.data_dict["frame"] >= t * self.recordMeta_dict["frameRate"][0]) & (self.data_dict["frame"] < (t + time_interval) * self.recordMeta_dict["frameRate"][0]) & (self.data_dict["x"] >= x1) & (self.data_dict["x"] <= x2)
            vehicles1 = self.data_dict[mask1 & (self.data_dict["y"] >= 0)]["id"].unique()
            count1 = len(vehicles1)
            intensity1 = count1 / (time_interval / 60)*240
            counts1.append(intensity1)

        return counts1

    def getDensity(self):
        x1 = 0
        x2 = 400
        lane_length = x2 - x1

        time_span = 1500 # seconds
        time_interval = 15 # seconds

        counts = []
        densities = []

        for t in range(0, time_span, time_interval):
            # Calculating Forward Traffic Flow
            mask = (self.data_dict["frame"] >= t * self.recordMeta_dict["frameRate"][0]) & (self.data_dict["frame"] < (t + time_interval) * self.recordMeta_dict["frameRate"][0]) & (self.data_dict["x"] >= x1) & (self.data_dict["x"] <= x2)
            vehicles = self.data_dict[mask & (self.data_dict["y"] >= 0)]["id"].unique()
            count = len(vehicles)
            density = count / (time_interval / 60) / lane_length
            counts.append(count)
            densities.append(density)

        return densities
    
    def getTTC1Dir(self, direction = 1):
        """
        Returns the TTC for the specified direction default is 1
        """
        TTC = self.data_merged.loc[(self.data_merged["drivingDirection"] == direction) & (self.data_merged["ttc"]>=0)]['ttc']
        
        return list(TTC)
    
    def getTTC(self):
        """
        Returns the TTC for the both directions
        """
        TTC = self.data_merged.loc[(self.data_merged["ttc"]>=0)]['ttc']
        
        return list(TTC)
    

    def compDRAC(self):
        """Computes DRAC and stores the data in the data_merged table"""
        delxvel = (self.data_merged["precedingXVelocity"] - self.data_merged["xVelocity"])
        delyvel = (self.data_merged["yVelocity"])
        self.data_merged["DRAC"] = np.sqrt(delxvel**2+delyvel**2)/(self.data_merged["dhw"])
        self.data_merged["DRAC"].replace([np.inf, -np.inf], np.nan, inplace=True)

    def getDRAC1Dir(self, direction = 1):
        """
        Returns the DRAC for the specified direction default is 1
        """
        # Might need to add the 
        try:
            DRAC = self.data_merged.loc[self.data_merged['drivingDirection']==direction]["DRAC"]
        except KeyError:
            self.compDRAC()
            DRAC = self.data_merged.loc[self.data_merged['drivingDirection']==direction]["DRAC"]

        return list(DRAC)
    
    def getDRAC(self):
        """
        Returns the DRAC for the both directions
        """
        try:
            DRAC = self.data_merged["DRAC"]
        except KeyError:
            self.compDRAC()
            DRAC = self.data_merged["DRAC"]
        
        return list(DRAC)

tot_speed = [[] for i in range(700)]
vehicles_type = [[] for i in range(700)]

# Initialize data extraction
HighD = HighDData()

# Aggregated values
HighD_car_speeds, HighD_car_ids = HighD.getCarSpeed()
HighD_truck_speeds = HighD.getTruckSpeed()

HighD_car_speeds1 = np.array(HighD_car_speeds)*3.6
HighD_truck_speeds1 = np.array(HighD_truck_speeds)*3.6

mu1 = np.mean(HighD_car_speeds1)
sigma1 = np.std(HighD_car_speeds1)
x1 = np.linspace(mu1 - 3*sigma1, mu1 + 3*sigma1, 100)
y1 = stats.norm.pdf(x1, mu1, sigma1)

mu1 = np.mean(HighD_truck_speeds1)
sigma1 = np.std(HighD_truck_speeds1)
x3 = np.linspace(mu1 - 3*sigma1, mu1 + 3*sigma1, 100)
y3 = stats.norm.pdf(x3, mu1, sigma1)

def AAPILoad():
    return 0

def AAPIInit():
    return 0

def AAPISimulationReady():
    return 0

def AAPIManage(time, timeSta, timTrans, SimStep):
    
    nba = AKIInfNetNbSectionsANG()

    for i in range(nba):
        id = AKIInfNetGetSectionANGId(i)
        nb = AKIVehStateGetNbVehiclesSection(id,True)
        
        for j in range(nb):
            infVeh = AKIVehStateGetVehicleInfSection(id,j)
            tot_speed[infVeh.idVeh].append(infVeh.CurrentSpeed)
            veh_type = infVeh.type # car: 1, truck: 2
            if(len(vehicles_type[infVeh.idVeh]) == 0):
                vehicles_type[infVeh.idVeh].append(veh_type)
            # print("total speed", tot_speed)
            
            # astring = "Vehicle " + str(infVeh.idVeh) + ", CurrentSpeed " + str(tot_speed[infVeh.idVeh])
            # print(astring)
            # AKIPrintString(astring)

    return 0

def AAPIPostManage(time, timeSta, timTrans, SimStep):
    return 0

def AAPIFinish():
    for i in range(1,len(tot_speed)):
        if(len(tot_speed[i]) != 0):
            length_speed = len(tot_speed[i])
            tot_speed[i] = sum(tot_speed[i])/length_speed
    # print("final total speed: ", tot_speed[1:5])
    # print("final vehicle types: ", vehicles_type[1:5])

    car_speeds = []
    truck_speeds = []
    for i in range(len(tot_speed)):
        if(vehicles_type == 1):
            car_speeds.append(tot_speed[i])
        else:
            truck_speeds.append(tot_speed[i])

    mu2 = np.mean(np.array(car_speeds))
    sigma2 = np.std(np.array(car_speeds))

    y2 = stats.norm.pdf(x1, mu2, sigma2)

    mu2 = np.mean(truck_speeds)
    sigma2 = np.std(truck_speeds)

    y4 = stats.norm.pdf(x3, mu2, sigma2)

    # K-S test
    KS_car_speeds = ks_2samp(y1, y2)
    KS_truck_speeds = ks_2samp(y3, y4)

    # print(KS_car_speeds)
    # print(KS_truck_speeds)
    # Score (Values:0~1, higher the better)
    score = (KS_car_speeds.pvalue + KS_truck_speeds.pvalue)/2
    print("Scores: ", score)

    return 0

def AAPIUnLoad():
    return 0

def AAPIEnterVehicle(idveh,idsection):
    return 0

def AAPIExitVehicle(idveh,idsection):
    return 0


