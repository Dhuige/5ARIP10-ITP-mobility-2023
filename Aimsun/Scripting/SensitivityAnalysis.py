import random

# Variables used to configure this script
# apply a replication
replication = model.getCatalog().find( 530 )

# Experiment to modify
experimentId = 409

# Experiment name
experimentName = "Micro SRC Experiment 409"

# VehicleType to modify
carTypetId = 154
truckTypetId = 159

# set random variable within the range
maxDesiredSpeedMeanCar = random.uniform(50.0, 200.0)
maxDesiredSpeedMeanTruck = random.uniform(40.0, 120.0)

normalDecelerationMeanCar = random.uniform(3.5, 4.5)
normalDecelerationMeanTruck = random.uniform(2.5, 4.8)

maxAccelerationMeanCar  = random.uniform(2.6, 3.4)
maxAccelerationMeanTruck  = random.uniform(0.6, 1.8)

reactionTimeCar = [random.uniform(0.5, 1.5), 1.2, 1.6, 1.0]
reactionTimeTruck = [random.uniform(0.5, 3.0), 1.3, 1.7, 1.0]

sensitivityFactorMeanCar  = random.uniform(0.0, 1.0)
sensitivityFactorMeanTruck  = random.uniform(0.0, 1.0)

print("The values for the parameters are [", 
      maxDesiredSpeedMeanCar, 
	  maxDesiredSpeedMeanTruck,
	  normalDecelerationMeanCar,
	  normalDecelerationMeanTruck,
	  maxAccelerationMeanCar,
	  maxAccelerationMeanTruck,
	  reactionTimeCar,
	  reactionTimeTruck,
	  sensitivityFactorMeanCar,
	  sensitivityFactorMeanTruck, "]")

def apply_replication():
	"""
	Run a Replication in Aimsun based on the replication ID
	
	Throws an error:
		The replication ID does not exist
	"""
	GKSystem.getSystem().executeAction( "execute", replication, [], "" )


# Modify the following parameters:
# - Max desired speed
# - Max Acceleration 
# - Normal Deceleration 
# - Reaction Time 
# - Vehicle demand 
# - Gap
# - Sensitivity Factor

# Do the sensitivity analysis on the car type
experiment = model.getCatalog().findByName(QString(experimentName))
vehType = model.getCatalog().find( carTypetId )
if vehType != None and vehType.isA( "GKVehicle" ):
	# Save maxDesiredSpeed parameter
	max_vehicle_speed = vehType.getDataValueByID( GKVehicle.maxDesiredSpeed )[0]
	# Save new random value in the model and apply replication
	vehType.getDataValueByID( GKVehicle.maxSpeedMean, QVariant( maxDesiredSpeedMeanCar[0] ))
	apply_replication()
	# Set back the previous value
	vehType.setDataValueByID( GKVehicle.maxSpeedMean, QVariant( max_vehicle_speed ))

	# Save maxAcceleration parameter
	maxAcceleration = vehType.getDataValueByID( GKVehicle.maxAcceleration )[0]
	# Save new random value in the model and apply replication
	vehType.getDataValueByID( GKVehicle.maxAcceleration, QVariant( maxAccelerationMeanCar[0] ))
	apply_replication()
	# Set back the previous value
	vehType.setDataValueByID( GKVehicle.maxAcceleration, QVariant( maxAcceleration ))

	# Save maxAcceleration parameter
	normalDecelMean = vehType.getDataValueByID( GKVehicle.normalDecelMean )[0]
	# Save new random value in the model and apply replication
	vehType.getDataValueByID( GKVehicle.normalDecelMean, QVariant( normalDecelerationMeanCar[0] ))
	apply_replication()
	# Set back the previous value
	vehType.setDataValueByID( GKVehicle.normalDecelMean, QVariant( normalDecelMean ))

	# [reaction_time, reaction_stop, reaction_light, reaction_prob]
	car_react = GKVehicleReactionTimes(reactionTimeCar[0], reactionTimeCar[1],
										reactionTimeCar[2], reactionTimeCar[3])
	vehType.setVariableReactionTimes([car_react])
	experiment.setVariableReactionTimesMicro(vehType, [car_react])

	# Traffic Demand: TODO: implement using code from PenetrationRate.py file

	# Gap: TODO: search in the official Aimsun Scripting documentation where to extract it from.

	# Sensitivity factor
	# Save maxAcceleration parameter
	speedAcceptanceMean = vehType.getDataValueByID( GKVehicle.speedAcceptanceMean )[0]
	# Save new random value in the model and apply replication
	vehType.getDataValueByID( GKVehicle.speedAcceptanceMean, QVariant( sensitivityFactorMeanCar[0] ))
	apply_replication()
	# Set back the previous value
	vehType.setDataValueByID( GKVehicle.speedAcceptanceMean, QVariant( speedAcceptanceMean ))

vehType = model.getCatalog().find( truckTypetId )
# repeat in the same way for the truck type
if vehType != None and vehType.isA( "GKVehicle" ):
	# Save maxDesiredSpeed parameter
	max_vehicle_speed = vehType.getDataValueByID( GKVehicle.maxDesiredSpeed )[0]
	# Save new random value in the model and apply replication
	vehType.getDataValueByID( GKVehicle.maxSpeedMean, QVariant( maxDesiredSpeedMeanTruck[0] ))
	apply_replication()
	# Set back the previous value
	vehType.setDataValueByID( GKVehicle.maxSpeedMean, QVariant( max_vehicle_speed ))

	# Save maxAcceleration parameter
	maxAcceleration = vehType.getDataValueByID( GKVehicle.maxAcceleration )[0]
	# Save new random value in the model and apply replication
	vehType.getDataValueByID( GKVehicle.maxAcceleration, QVariant( maxAccelerationMeanTruck[0] ))
	apply_replication()
	# Set back the previous value
	vehType.setDataValueByID( GKVehicle.maxAcceleration, QVariant( maxAcceleration ))

	# Save maxAcceleration parameter
	normalDecelMean = vehType.getDataValueByID( GKVehicle.normalDecelMean )[0]
	# Save new random value in the model and apply replication
	vehType.getDataValueByID( GKVehicle.normalDecelMean, QVariant( normalDecelerationMeanTruck[0] ))
	apply_replication()
	# Set back the previous value
	vehType.setDataValueByID( GKVehicle.normalDecelMean, QVariant( normalDecelMean ))

	# [reaction_time, reaction_stop, reaction_light, reaction_prob]
	truck_react = GKVehicleReactionTimes(reactionTimeTruck[0], reactionTimeTruck[1],
										reactionTimeTruck[2], reactionTimeTruck[3])
	vehType.setVariableReactionTimes([truck_react])
	experiment.setVariableReactionTimesMicro(vehType, [truck_react])

	# Traffic Demand: TODO: implement using code from PenetrationRate.py file

	# Gap: TODO: search in the official Aimsun Scripting documentation where to extract it from.

	# Sensitivity factor
	# Save maxAcceleration parameter
	speedAcceptanceMean = vehType.getDataValueByID( GKVehicle.speedAcceptanceMean )[0]
	# Save new random value in the model and apply replication
	vehType.getDataValueByID( GKVehicle.speedAcceptanceMean, QVariant( sensitivityFactorMeanTruck[0] ))
	apply_replication()
	# Set back the previous value
	vehType.setDataValueByID( GKVehicle.speedAcceptanceMean, QVariant( speedAcceptanceMean ))

# Be sure that you reset the UNDO buffer after a modification that cannot be undone
model.getCommander().addCommand( None )