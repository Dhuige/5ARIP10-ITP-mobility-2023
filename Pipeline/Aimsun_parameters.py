# Import libraries
import os
import sqlite3
import pandas as pd
from numpy import inf, nan, where

class AimsunData():
    def __init__(self, filename1, filename2, model_name)->None:
        """Initialize the class and connects to two Aimsun database files (SQLite) stored in Aimsun\<model_name>\Speed_calibration folder"""
        self.getconnection(filename1, filename2, model_name)


    def getconnection(self, filename1, filename2, model_name = "TwoLaneOneWay")->None:
        """Establish connection to the Aimsun database file (SQLite) stored in Aimsun\<model_name>\Results folder

        Parameters:
            filename1 (str): Name of the first Aimsun database file
            filename2 (str): Name of the second Aimsun database file
            model_name (str): Name of the Aimsun model

        Returns:
            None -> Establishes connection to self.c1 and self.c2
        """

        data_folder = os.path.join(f".\..\Aimsun\{model_name}\Results")
        data_path1 = os.path.join(data_folder, filename1)
        data_path2 = os.path.join(data_folder, filename2)

        conn1 = sqlite3.connect(data_path1)
        conn2 = sqlite3.connect(data_path2)
        self.c1 = conn1.cursor()
        self.c2 = conn2.cursor()

    def change_connection(self, new_filename1:str, new_filename2:str, model_name:str="TwoLaneOneWay"):
        """Changes the current connection to another file in the folder: Aimsun\<model_n>\Speed_calibration
        Input:
            new_filename1: name of the first file
            new_filename2: name of the second file
        Returns:
            None -> connections self.c1 and self.c2 are established with the new files
        """
        
        # close current connection
        try:
            self.close_connection() 
        except:
            print("No Connection had to be closed")
        
        self.getconnection(new_filename1, new_filename2, model_name)
        print(f"Connection succesfully changed to: {new_filename1} and {new_filename2}")

    def close_connection(self):
        """Close the connection to all the Aimsun database file
        
        Parameters:
            None
        
        Returns:
            None -> (self.c1 and self.c2 is closed)"""

        self.c1.close()
        self.c2.close()

    def _getCarSpeedAimsun(self, connection_var:sqlite3.Connection)->list:   
        """Get the car speed from the Aimsun database file

        Parameters:
        connection_var (sqlite3.Connection): Connection to the Aimsun database file

        Returns:
        detail_speed_car_float (list(float,..)): List of floats containing the car speed
        """	

        detail_speed_car_query = 'SELECT speed FROM MIVEHDETAILEDTRAJECTORY INNER JOIN MIVEHTRAJECTORY ON MIVEHDETAILEDTRAJECTORY.oid = MIVEHTRAJECTORY.oid WHERE MIVEHTRAJECTORY.sid = 154 ';
        detail_speed_car = connection_var.execute(detail_speed_car_query).fetchall()
        
        detail_speed_car_float = [float(item[0]) for item in detail_speed_car]

        return detail_speed_car_float

    def _getTruckSpeedAimsun(self, connection_var:sqlite3.Connection)->list:   
        """Get the truck speed from the Aimsun database file
        
        Parameters:
            connection_var (sqlite3.Connection): Connection to the Aimsun database file
        
        Returns:
            detail_speed_truck_float (list(float,..)): List of floats containing the truck speed
        """

        detail_speed_truck_query = 'SELECT speed FROM MIVEHDETAILEDTRAJECTORY INNER JOIN MIVEHTRAJECTORY ON MIVEHDETAILEDTRAJECTORY.oid = MIVEHTRAJECTORY.oid WHERE MIVEHTRAJECTORY.sid = 159 ';
        detail_speed_truck = connection_var.execute(detail_speed_truck_query).fetchall()

        detail_speed_truck_float = [float(item[0]) for item in detail_speed_truck]

        return detail_speed_truck_float

    def _getDensityAimsun(self, connection_var:sqlite3.Connection)->list:
        """Get the density from the Aimsun database file
        
        Parameters:
            connection_var (sqlite3.Connection): Connection to the Aimsun database file
        
        Returns:
            density_float (list(float,..)): List of floats containing the traffic density
        """

        density_query = 'SELECT density FROM MISECT WHERE oid=391 AND sid=0 AND ent!= 0'
        density = connection_var.execute(density_query).fetchall()

        density_float = [float(item[0]) for item in density]
        
        return density_float
    
    def _getLeaderAimsun(self, connection_var:sqlite3.Connection)->None:
        """Get the leader from the Aimsun database file
        
        Parameters:
            connection_var (sqlite3.Connection): Connection to the Aimsun database file
        
        Returns:
            None -> Establishes self.leaderTable with parameters [followerID, distance, timeStamp, speedDifference]
        """	

        leader_query = 'SELECT follower.oid, (leader.travelledDistance - follower.travelledDistance) AS distance,\
        follower.stationaryTime,  (leader.speed-follower.speed) as speedDifference \
        FROM MIVEHDETAILEDTRAJECTORY follower \
        JOIN MIVEHDETAILEDTRAJECTORY leader ON \
        follower.oid != leader.oid \
        AND follower.sectionId = leader.sectionId \
        AND follower.laneIndex = leader.laneIndex \
        AND distance > 0 \
        AND follower.stationaryTime = leader.stationaryTime \
        GROUP BY follower.oid, follower.stationaryTime'
        Leader = connection_var.execute(leader_query).fetchall()
        self.leaderTable = pd.DataFrame(Leader)
        self.leaderTable.columns =['followerID', 'distance', 'timeStamp', 'speedDifference']


    def _getDRACAimsun(self, connection_var:sqlite3.Connection)->list:
        """Get the maximal DRAC per vehicle ID from the Aimsun database file
        
        Parameters:
            connection_var (sqlite3.Connection): Connection to the Aimsun database file
        
        Returns:
            DRAC (list(float,..)): List containing the maximum DRAC per vehicle ID
        """
        
        self._getLeaderAimsun(connection_var)
        self.leaderTable["DRAC"] = self.leaderTable["speedDifference"]**2/((3.6**2)*self.leaderTable["distance"])
        self.leaderTable["DRAC"] = where(self.leaderTable["speedDifference"]<=0,0,self.leaderTable["DRAC"]) # Fix issue with negative values -> 0 since it will not be counted
        self.leaderTable["DRAC"].fillna(0, inplace=True)

        # Return max DRAC per vehicle ID
        DRAC = self.leaderTable.groupby("followerID").max()["DRAC"] 
        
        # remove leader table to ensure correct connection to database
        self.__dict__.pop("leaderTable",None) 

        return list(DRAC)
    
    def _getTTCAimsun(self, connection_var:sqlite3.Connection)->list:
        """Get the minimal TTC per Vehicle ID from the Aimsun database file
        
        Parameters:
            connection_var (sqlite3.Connection): Connection to the Aimsun database file
        
        Returns:
            TTC (list): List containing the minimum TTC per vehicle ID
        """

        self._getLeaderAimsun(connection_var)
        self.leaderTable["TTC"] = 3.6*self.leaderTable["distance"]/self.leaderTable["speedDifference"]
        self.leaderTable = self.leaderTable.replace([inf, -inf], 0) # Fix issue with inf values -> 0 since it will not be counted 
        
        # Return min TTC per vehicle ID
        TTC = self.leaderTable[self.leaderTable["TTC"]>0].groupby("followerID").min()["TTC"]
        
        # remove leader table to ensure correct connection to database
        self.__dict__.pop("leaderTable",None) 

        return list(TTC)
    
    def Aggregated_Aimsun_values(self, connection_var:sqlite3.Connection)->dict:
        """Get all Aimsun emergengent parameter values (TTC, DRAC, Density, Car_speed, Truck_speed)
        
        Parameters:
            connection_var (sqlite3.Connection): Connection to the Aimsun database file
        
        Returns:
            Aimsun_values (dict): Dictionary containing all emergent parameter values"""

        Aimsun_values = {}
        Aimsun_values["TTC"] = self._getTTCAimsun(connection_var)
        Aimsun_values["DRAC"] = self._getDRACAimsun(connection_var)        
        Aimsun_values["Density"] = self._getDensityAimsun(connection_var)
        Aimsun_values["Car_speed"] = self._getCarSpeedAimsun(connection_var)
        Aimsun_values["Truck_speed"] = self._getTruckSpeedAimsun(connection_var)
        return Aimsun_values

        
