# Import libraries
import os
import sqlite3
import pandas as pd
from numpy import inf, nan

class AimsunData():
    def __init__(self, filename1, folder_name):
        """Initialize the class"""
        self.getconnection(filename1, folder_name)


    def getconnection(self, filename1, folder_name = "Speed_calibration"):
        """Establish connection to the Aimsun database file (SQLite) stored in Aimsun\TwoLaneOneWay\Speed_calibration folder"""

        data_folder = os.path.join(".\..\Aimsun\TwoLaneOneWay", folder_name)
        data_path1 = os.path.join(data_folder, filename1)

        conn1 = sqlite3.connect(data_path1)
        self.c1 = conn1.cursor()

    def _getCarSpeedAimsun(self, connection_var):   
        """Get the car speed from the Aimsun database file"""	

        detail_speed_car_query = 'SELECT speed FROM MIVEHDETAILEDTRAJECTORY INNER JOIN MIVEHTRAJECTORY ON MIVEHDETAILEDTRAJECTORY.oid = MIVEHTRAJECTORY.oid WHERE MIVEHTRAJECTORY.sid = 154 OR MIVEHTRAJECTORY.sid = 534 OR MIVEHTRAJECTORY.sid = 536';
        detail_speed_car = connection_var.execute(detail_speed_car_query).fetchall()
        
        detail_speed_car_float = [float(item[0]) for item in detail_speed_car]

        return detail_speed_car_float

    def _getTruckSpeedAimsun(self, connection_var):   
        """Get the truck speed from the Aimsun database file"""

        detail_speed_truck_query = 'SELECT speed FROM MIVEHDETAILEDTRAJECTORY INNER JOIN MIVEHTRAJECTORY ON MIVEHDETAILEDTRAJECTORY.oid = MIVEHTRAJECTORY.oid WHERE MIVEHTRAJECTORY.sid = 159 ';
        detail_speed_truck = connection_var.execute(detail_speed_truck_query).fetchall()

        detail_speed_truck_float = [float(item[0]) for item in detail_speed_truck]

        return detail_speed_truck_float

    def _getIntensityAimsun(self, connection_var):
        """Get the intensity from the Aimsun database file"""

        flow_query = 'SELECT input_flow FROM MISECT WHERE oid=391 AND sid=0 AND ent!= 0'
        flow = connection_var.execute(flow_query).fetchall()

        flow_float = [float(item[0]) for item in flow]

        return flow_float

    def _getDensityAimsun(self, connection_var):
        """Get the density from the Aimsun database file"""

        density_query = 'SELECT density FROM MISECT WHERE oid=391 AND sid=0 AND ent!= 0'
        density = connection_var.execute(density_query).fetchall()

        density_float = [float(item[0]) for item in density]
        
        return density_float
    
    def _getLeaderAimsun(self, connection_var):
        """Get the leader from the Aimsun database file"""	

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


    def _getDRACAimsun(self, connection_var):
        """Get the DRAC from the Aimsun database file"""
        maxDRAC = []
        try:
            DRAC = self.leaderTable.groupby("followerID").max()["DRAC"]
        except:
            self._getLeaderAimsun(connection_var)
            self.leaderTable["DRAC"] = self.leaderTable["speedDifference"]**2/((3.6**2)*self.leaderTable["distance"])
            DRAC = self.leaderTable.groupby("followerID").max()["DRAC"]
        
        self.__dict__.pop("leaderTable",None) # remove leader table to ensure correct connection to database

        return list(DRAC)
    
    def _getTTCAimsun(self, connection_var):
        """Get the TTC from the Aimsun database file"""

        self._getLeaderAimsun(connection_var)
        self.leaderTable["TTC"] = 3.6*self.leaderTable["distance"]/self.leaderTable["speedDifference"]
        self.leaderTable = self.leaderTable.replace([inf, -inf], 0) # Fix issue with inf values -> 0 since it will not be counted 
        
        TTC = self.leaderTable[self.leaderTable["TTC"]>0].groupby("followerID").min()["TTC"]
        
        self.__dict__.pop("leaderTable",None) # remove leader table to ensure correct connection to database

        return list(TTC)
    
    def Aggregated_Aimsun_values(self, connection_var):
        """Get all Aimsun values (dictionary for lists)"""

        Aimsun_values = {}
        Aimsun_values["TTC"] = self._getTTCAimsun(connection_var)
        Aimsun_values["DRAC"] = self._getDRACAimsun(connection_var)        
        Aimsun_values["Density"] = self._getDensityAimsun(connection_var)
        Aimsun_values["Car_speed"] = self._getCarSpeedAimsun(connection_var)
        Aimsun_values["Truck_speed"] = self._getTruckSpeedAimsun(connection_var)
        return Aimsun_values
    
    def close_connection(self):
        """Close the connection to the Aimsun database file"""

        self.c1.close()

    def change_connection(self, new_filename1):
        """"Changes the current connection to another file in the folder: Aimsun\TwoLaneOneWay\Speed_calibration
        Input:
            new_filename1: name of the first file
        Returns:
            None -> (self.c1 and self.c2 is established)    
        """
        try:
            self.close_connection()
        except:
            print("No Connection had to be closed")
        self.getconnection(new_filename1)


        
