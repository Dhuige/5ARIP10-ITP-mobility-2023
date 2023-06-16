# This script changes the factor for a traffic demand.

import os
# Variables used to configure this script
trafficDemandId = 413
assertiveAVTypeID = 534
cautiousAVTypeID = 536
aVODMatrixID = 531
replicationID = 530
scenarioID = 408

# new factor
newFactorAVPenetrationRange = [i for i in range(10, 110, 10)]
newFactorCarPenetrationRange = [i for i in range(90, -10, -10)]

# get strings for each of the files
data_dir = "Directory for files"

assertive_file_names = []
cautious_file_names = []
num_of_files = 10
for file in range(num_of_files):
    file_name_a = data_dir + "Assertive/Penetration_"
    assertive_file_names.append(file_name_a)

    file_name_c = data_dir + "Cautious/Penetration_"
    cautious_file_names.append(file_name_c)

assertive_data_dict = []
for i, filename in enumerate(assertive_file_names, start=1):
    DB_data = filename + str(i*10) + "_asser.sqlite"
    assertive_data_dict.append(DB_data)

cautious_data_dict = []
for i, filename in enumerate(cautious_file_names, start=1):
    DB_data = filename + str(i*10) + "_caut.sqlite"
    cautious_data_dict.append(DB_data)


def getVehicleObject(model, AVTypeID):
	"""
	Return the vehicle object based on its ID

	Parameters:
		model: object for the Aimsun model
		AVTypeID(int): the identifier of the AV
	
	Returns:
		The vehicle object corresponding to the ID
	
	Throws an error:
		The vehicle ID does not exist
	"""
	AVConfig = model.getCatalog().find( int(AVTypeID) )
	if AVConfig != None:
		if AVConfig.isA( "GKVehicle" ):
			print ("AV type found!")
		else:
			print ("AV type not found")
	return AVConfig

# 
def setVehicleObject(model, vehicleObject):
	"""
	Set a vehicle object type in the OD matrix

	Parameters:
		model: object for the Aimsun model
		vehicleObject(int): the object of the modified vehicle ID
	
	Throws an error:
		The vehicle Object does not exist 
	"""
	container = model.getCatalog().find( int(aVODMatrixID) )
	if container != None:
		if container.isA( "GKODMatrix" ):
			container.setVehicle(vehicleObject)
			print("The vehicle type has been changed to: ", container.getVehicle().getName())
		else:
			print ("Object is not a traffic demand")


def apply_replication(model, replicationID):
	"""
	Run a Replication in Aimsun based on the replication ID

	Parameters:
		model: object for the Aimsun model
		replicationID(int): the replication ID
	
	Throws an error:
		The replication ID does not exist
	"""
	replication = model.getCatalog().find( replicationID )
	GKSystem.getSystem().executeAction( "execute", replication, [], "" )


def change_database_name(model, filename):
	"""
	Change the output trajectory file directory in Aimsun Next

	Parameters:
		model: object for the Aimsun model
		filename(str): the directory of the output trajectory file 
	
	Throws an error:
		The directory in filename does not exist
	"""
# 
	dynamicScenarioConfig = model.getCatalog().find( int(scenarioID) )
	if dynamicScenarioConfig != None:
		if dynamicScenarioConfig.isA( "GKScenario" ):
			db = dynamicScenarioConfig.getDB(False)
			
			db.setDatabaseName(filename)

			# sets the new database directory
			dynamicScenarioConfig.setDB(db)
			print ("Database changed found!")
		else:
			print ("Scenario not found")

# modify traffic demand
def changeFactorDemand( model, trafficDemand, vehicleType, carPenetrationRange, AVPenetrationRange, replicationID, filename):
	"""
	Change the factor demand for each traffic demand item.

	Parameters:
		model: object for the Aimsun model
		trafficDemand(str): object for the traffic demand
		vehicleType(str): the AV vehicle type 
		carPenetrationRange(int[]): the range of values for the Car penetration 
		AVPenetrationRange(int[]): the range of values for the AV penetration 
		replicationID(int): the replication ID 
		filename(str): the directory of the output trajectory file 
	
	"""
	# change the vehicle type after getting the AV object
	vehicleObject = getVehicleObject(model, vehicleType)
	setVehicleObject(model, vehicleObject)

	analysedVehicles = []
	# extracts all vehicles other than the truck
	for vehicles in trafficDemand.getUsedVehicles():
		if(vehicles.getName() != 'Truck'):
			analysedVehicles.append(vehicles)

	for index in range(len(carPenetrationRange)):
		change_database_name(model, filename[index])
		carRate = carPenetrationRange[index]
		AVRate = AVPenetrationRange[index]

		# modify car schedule
		carDemandItem = trafficDemand.getSchedule(analysedVehicles[0])
		carDemandItem[0].setFactor( str(carRate) )
		trafficDemand.removeFromSchedule(carDemandItem[0])
		trafficDemand.addToSchedule(carDemandItem[0])	

		# modify AV schedule
		AVDemandItem = trafficDemand.getSchedule(analysedVehicles[1])
		AVDemandItem[0].setFactor( str(AVRate)  )
		trafficDemand.removeFromSchedule(AVDemandItem[0])
		trafficDemand.addToSchedule(AVDemandItem[0])
		apply_replication(model, replicationID)
		
def changeFactor( model, entry, vehicleType, carPenetrationRate, AVPenetrationRate, replicationID, filename):
	#Get GKTrafficDemand object by Id.
	container = model.getCatalog().find( int(entry) )
	if container != None:
		if container.isA( "GKTrafficDemand" ):
			changeFactorDemand( model, container, vehicleType, carPenetrationRate, AVPenetrationRate, replicationID, filename)
			print ("Traffic demand modified")
		else:
			print ("Object is not a traffic demand")
	else:
		print ("No traffc demand to modify")

changeFactor( model, trafficDemandId, assertiveAVTypeID, newFactorCarPenetrationRange,newFactorAVPenetrationRange, replicationID, assertive_data_dict)
changeFactor( model, trafficDemandId, cautiousAVTypeID, newFactorCarPenetrationRange,newFactorAVPenetrationRange, replicationID, cautious_data_dict)

# Be sure that you reset the UNDO buffer after a modification that cannot be undone
model.getCommander().addCommand( None )