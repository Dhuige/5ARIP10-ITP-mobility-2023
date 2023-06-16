#include "behavioralModelParticular.h"
#include "simVehicleParticular.h"
#include "AKIProxie.h"
#include "ANGConProxie.h"
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <algorithm>
using namespace std;
#define Tolerancia 0.01
#define DBL_MAX 1.7976931348623158e+308 

behavioralModelParticular::behavioralModelParticular(): A2BehavioralModel()
{

   	const unsigned short *randomSeedString = AKIConvertFromAsciiString( "GKReplication::randomSeedAtt" );
   	seed = ANGConnGetAttributeValueInt( ANGConnGetAttribute( randomSeedString ), ANGConnGetReplicationId() );// Set seed for creation

   	const unsigned short *param0= AKIConvertFromAsciiString( "GKExperiment::p_distance" );
   	p_distance = ANGConnGetAttributeValueDouble( ANGConnGetAttribute( param0 ),ANGConnGetExperimentId());  // Unknown as of now

}
 


behavioralModelParticular::~behavioralModelParticular(){}



A2SimVehicle * behavioralModelParticular::arrivalNewVehicle( void *handlerVehicle, unsigned short idHandler, bool isFictitiousVeh, unsigned int vehTypeId ){
	
	// Create new sim vehicle (fictious)
	simVehicleParticular * res = new simVehicleParticular(handlerVehicle, idHandler, isFictitiousVeh, vehTypeId);

   	if (!isFictitiousVeh) {
	
		res->setnewAttribute(2); // Makes it a real car

   	}

  return res;

}



void behavioralModelParticular::removedVehicle( void *handlerVehicle, unsigned short idHandler, A2SimVehicle * a2simVeh ){
	
	// Allows for cars to be removed from the simulation given a certain condition

}



bool behavioralModelParticular::evaluateCarFollowing(A2SimVehicle *vehicle, double &newpos, double &newspeed)
{
	// has to be update
	int idveh = vehicle->getId(); 
	newspeed = vehicle->getAimsunCarFollowingSpeed(); // leader speed
	double increment = 0;

	if (newspeed >= vehicle->getSpeed(vehicle->isUpdated())){
		
		increment = newspeed*getSimStep();
	
	}

	else{

		increment = 0.5*(newspeed + vehicle->getSpeed(vehicle->isUpdated()))*getSimStep();
	
	}

	newpos = vehicle->getPosition(vehicle->isUpdated()) + increment; // Set new position of the car 
	
	return true;
}



double carFollowingSpeed(A2SimVehicle* vehicle)
{ // Computation of velocity

	float target_gap = 2; // [m] (2 is standard) Prefered target gap
	float target_speed = DTASection::getMaxSpeedInKmH() / 3.6; // [m/s] Returns max speed of the road (Hard Code?)
	float thw = 3; // [s] Time headway // This is a variable but
	float a = vehicle->getAccelration(); // [m/s^2] Returns acceleration (Test if this is current or max)
	float b = 2.5; // [m/s] Comfortable deceleration rate
	float d = 4; // [-] Order size
	
	double XPrevious, speedVehicle, XPreviousLeader, SpeedPreviousLeader; // Required for gap not sure if this is a global var.

	v_leader = vehicle->getAimsunCarFollowingSpeed();
	speed = vehicle->getSpeed(vehicle->isUpdated());
	s = vehicle->getGap(Shift, vehicleLeader, ShiftLeader, XPrevious, speedVehicle, XPreviousLeader, SpeedPreviousLeader, time); // Get current gap between leader

	// Compute differences
	speed_r = speed / (target_speed / 3.6);
	delta_v = v_leader - speed;

	// Desired spacing s*(v,delta_v)
	desired_spacing = target_gap + speed * thw + speed * delta_v /(2 * sqrt(a * b))

	// Returns acceleration
	accel = a*(1-pow(speed_r, d)-pow((desired_spacing/s), 2))

	// New speed computation
	v_new = speed + accel * getSimStep() 
}

bool behavioralModelParticular::evaluateLaneChanging(A2SimVehicle *vehicle,int threadId)
{	// Do not touch	
	//Define Lane Changing Direction
	int LaneChangingDirection = vehicle->getNbLaneChanges2ReachNextValidLane();
	if (LaneChangingDirection != 0){
		if (abs(LaneChangingDirection)>1){
			LaneChangingDirection = LaneChangingDirection / abs(LaneChangingDirection);
		}
		bool RightLanePossible = vehicle->isLaneChangingPossible(1);
		bool LeftLanePossible = vehicle->isLaneChangingPossible(-1);
		if (LaneChangingDirection == -1 && !LeftLanePossible){
			LaneChangingDirection = 0;
		}
		else if (LaneChangingDirection == 1 && !RightLanePossible){
			LaneChangingDirection = 0;
		}
	}

	if (LaneChangingDirection != 0){

		double XPosTargetlane = vehicle->getPositionInTargetlane(vehicle->getPosition(0), LaneChangingDirection);

		//Define whether a lane changing attempt is made or not
		bool Intentacambio = true;
		if (Intentacambio){
			//Lane Changing attempt
			A2SimVehicle* pVehDw = nullptr;
			A2SimVehicle *pVehUp = nullptr;
			double ShiftUp = 0, ShiftDw = 0;
			vehicle->getUpDown(LaneChangingDirection, XPosTargetlane, pVehUp, ShiftUp, pVehDw, ShiftDw);
			bool GapAcceptable = vehicle->isGapAcceptable(LaneChangingDirection, XPosTargetlane, pVehUp, ShiftUp, pVehDw, ShiftDw);
			if (GapAcceptable){
				vehicle->assignAcceptedGap(LaneChangingDirection, XPosTargetlane, (const   simVehicleParticular*)pVehUp, ShiftUp, (const simVehicleParticular*)pVehDw, ShiftDw, threadId);
				return true;
			}
		}

		//Target New Gap
		if (abs(vehicle->getNbLaneChanges2ReachNextValidLane())>0){
			A2SimVehicle * pVehDwReal = nullptr;
			A2SimVehicle * pVehUpReal = nullptr;
			double ShiftUpReal = 0, ShiftDwReal = 0;
			vehicle->getRealUpDown(LaneChangingDirection, XPosTargetlane, pVehUpReal, ShiftUpReal, pVehDwReal, ShiftDwReal);
			vehicle->targetNewGap(LaneChangingDirection, XPosTargetlane, pVehUpReal, ShiftUpReal, pVehDwReal, ShiftDwReal, threadId);
			if (pVehUpReal || pVehDwReal){
				vehicle->assignNewTargetGap(XPosTargetlane, (const simVehicleParticular*)pVehUpReal, ShiftUpReal, (const simVehicleParticular*)pVehDwReal, ShiftDwReal, threadId);
			}
		}
	}
	return true;
}

int behavioralModelParticular::evaluateHasTime2CrossYellowState(A2SimVehicle *vehicle, double distance2StopLine)
{ // Not of importance thus keep!
	int valueTime2Cross = 0;
	double BrakingDistance = - 0.5*vehicle->getSpeed(vehicle->isUpdated())*vehicle->getSpeed(vehicle->isUpdated()) / vehicle->getDeceleration();
	if (BrakingDistance > distance2StopLine){
		valueTime2Cross = 1;
	}
	return valueTime2Cross;
}

int behavioralModelParticular::evaluateLaneSelectionDiscretionary(A2SimVehicle *vehicle, bool LeftLanePossible, bool RightLanePossible)
{ 	// getDecelerationComponentGippsModelSpeed should be rewritten for IDM otherwise this is fine.
	// This function is found in ... (cant find it yet likely an Aimsun function)
	double Shift = 0;
	A2SimVehicle * leader = vehicle->getLeader(Shift);
	double Vel_leader = DBL_MAX;
	if (leader){
		Vel_leader = vehicle->getDecelerationComponentGippsModelSpeed(leader, Shift, false, false, 1);
		if (LeftLanePossible || RightLanePossible){
			if (LeftLanePossible){
				A2SimVehicle * pVehDwReal = nullptr;
				A2SimVehicle * pVehUpReal = nullptr;
				double ShiftUpReal = 0, ShiftDwReal = 0;
				int LaneChangingDirection = -1;
				double XPosTargetlane = vehicle->getPositionInTargetlane(vehicle->getPosition(0), LaneChangingDirection);
				vehicle->getRealUpDown(LaneChangingDirection, XPosTargetlane, pVehUpReal, ShiftUpReal, pVehDwReal, ShiftDwReal);
				double Vel_dw = DBL_MAX;
				if (pVehDwReal){
					Vel_dw = vehicle->getDecelerationComponentGippsModelSpeed(pVehDwReal, ShiftDwReal, false, false, 1);
				}
				if (Vel_dw > Vel_leader){
					return -1;
				}
			}
			if (RightLanePossible){
				A2SimVehicle * pVehDwReal = nullptr;
				A2SimVehicle * pVehUpReal = nullptr;
				double ShiftUpReal = 0, ShiftDwReal = 0;
				int LaneChangingDirection = 1;
				double XPosTargetlane = vehicle->getPositionInTargetlane(vehicle->getPosition(0), LaneChangingDirection);
				vehicle->getRealUpDown(LaneChangingDirection, XPosTargetlane, pVehUpReal, ShiftUpReal, pVehDwReal, ShiftDwReal);
				double Vel_dw = DBL_MAX;
				if (pVehDwReal){
					Vel_dw = vehicle->getDecelerationComponentGippsModelSpeed(pVehDwReal, ShiftDwReal, false, false, 1);
				}
				if (Vel_dw > Vel_leader){
					return 1;
				}
			}
		}
	}
	return 0;
}

bool behavioralModelParticular::isVehicleGivingWay(A2SimVehicle *vehicleGiveWay, A2SimVehicle *vehiclePrio, yieldInfo *givewayInfo, int &Yield)
{ // Do not touch this	
	if (givewayInfo->isVehiclePrioWithinVisibility && (givewayInfo->isVehicleGiveWayComingNext
		|| (!givewayInfo->isVehiclePrioRealAndReachingConflict && vehiclePrio->getSpeed(0)>0)
		|| givewayInfo->isVehiclePrioLeaderOfVehicleGiveWay)){
		//Vehicle is passing before Ceda arrives
		//or
		//Vehicle is fictitious or not coming to this conflict (and not stopped)
		Yield = -1;
	}
	else{
		bool prioritaryComesNext = (givewayInfo->isVehiclePrioComingNext
			|| givewayInfo->isVehiclePrioAfectedByStop
			|| givewayInfo->isVehiclePrioAfectedByYellowBox
			|| (givewayInfo->isVehiclePrioAfectedByGiveWay && !givewayInfo->isVehiclePrioPrioritaryBasedOnWaitingTime)
			|| ((vehiclePrio->getSpeed(0) == 0) && (givewayInfo->passingTimeVehicleGiveWay <= 0.0)));

		if (givewayInfo->isVehiclePrioWithinVisibility && givewayInfo->isVehiclePrioRealAndReachingConflict && !prioritaryComesNext){
			Yield = 1;
		}
		else{
			//Vehicle not visibile will not be considered!
			//Vehicle not prioritary but stopped
			//Ceda is Passing before Prioritary arrives
			Yield = 0;
		}
	}
	return true;
}

double behavioralModelParticular::computeCarFollowingAccelerationComponentSpeed(A2SimVehicle *vehicle,double CurrentSpeed,double TargetSpeed, double deltaRT)
{ // we can change this / but we also don't have too. It is the computation of acceleration, i.e. if we need to break or accelerate and what value this should be.
	// Calcula l'acceleracio tenint en compte les pendents
	double X = CurrentSpeed / TargetSpeed;
	double speedaccelerationcomponent = min(TargetSpeed, CurrentSpeed + 2.5 * vehicle->getAcceleration() * deltaRT * (1.0 - X)* sqrt(0.025 + X));
	if (speedaccelerationcomponent<CurrentSpeed){
		speedaccelerationcomponent = max(speedaccelerationcomponent, max(0., CurrentSpeed + (0.5 * vehicle->getDeceleration() * deltaRT)));
	}
	return speedaccelerationcomponent;
}

double behavioralModelParticular::computeCarFollowingDecelerationComponentSpeed (A2SimVehicle *vehicle,double Shift,A2SimVehicle *vehicleLeader,double ShiftLeader,bool controlDecelMax, bool aside,int time)
{ // Do not touch this
	double XPrevious, speedVehicle, XPreviousLeader, SpeedPreviousLeader;
	double gap = vehicle->getGap(Shift, vehicleLeader, ShiftLeader, XPrevious, speedVehicle, XPreviousLeader, SpeedPreviousLeader, time);
	double RT = vehicle->getReactionTime();
	double DecelEstimada = 0;
	if (SpeedPreviousLeader>Tolerancia){
		DecelEstimada = vehicle->getEstimationOfLeadersDeceleration(vehicleLeader, SpeedPreviousLeader);
	}
	double SpeedDecelerationComponent = computeCarFollowingDecelerationComponentSpeedCore(vehicle, speedVehicle, vehicleLeader, SpeedPreviousLeader, gap, DecelEstimada);
	if (aside){
		//SpeedAnterior imposed by Car-Following on side lane > Tolerancia to avoid RT at stop
		double GapMin = computeMinimumGap(vehicle, vehicleLeader);
		GapMin = gap - GapMin;
		if (GapMin<0){
			double Distance2Obstacle = DBL_MAX;
			if (vehicle->getObstacleType() != eNone){
				Distance2Obstacle = vehicle->getDistance2Obstacle() / abs(vehicle->getNbLaneChanges2ReachNextValidLane());
				Distance2Obstacle = max(0., Distance2Obstacle - max(SpeedPreviousLeader*RT, vehicleLeader->getLength()));
			}
			double minimumValue = Distance2Obstacle;
			double AdaptationDistance = max(vehicle->getFreeFlowSpeed()*RT, vehicle->getLength());
			if (vehicle->getObstacleType() == eOnRamp){
				minimumValue = min(minimumValue, 3 * AdaptationDistance);
			}
			else{
				minimumValue = min(minimumValue, AdaptationDistance);
			}
			double maximumValue = max(SpeedPreviousLeader, Tolerancia);
			double expParam = 0.5*(1. - speedVehicle / maximumValue*(1 - (GapMin) / minimumValue));

			double expValue = (float)exp(expParam); // function exp in 32/64 bits returns the same value used in this way
			SpeedDecelerationComponent = speedVehicle*expValue;
		}
	}
	if (controlDecelMax){
		double VelMin = 0;
		if (aside){
			VelMin = max(0., speedVehicle + vehicle->getDeceleration()*RT);
		}
		else{
			VelMin = max(0., speedVehicle + vehicle->getDecelerationMax()*RT);
		}
		if (SpeedDecelerationComponent<VelMin){
			SpeedDecelerationComponent = VelMin;
		}
	}
	return SpeedDecelerationComponent;
}

double behavioralModelParticular::computeCarFollowingDecelerationComponentSpeedCore(A2SimVehicle *vehicle, double speedVehicle, A2SimVehicle *vehicleLeader, double speedLeader, double gap, double leaderDecelerationEstimated)
{ // Maybe change but not sure if we need too?
	double bn = vehicle->getDeceleration();
	double RT = vehicle->getReactionTime();
	double bnTau = bn*RT;
	double SpeedDecelerationComponent = bnTau;
	double factorSqrt = 0;
	if (speedLeader<Tolerancia){
		factorSqrt = (bnTau* bnTau) - vehicle->getDeceleration() * (2.0 * gap - (speedVehicle * RT));
	}
	else if (speedLeader<DBL_MAX){
		factorSqrt = (bnTau * bnTau) - vehicle->getDeceleration() * (2.0 * gap - (speedVehicle * RT) - ((speedLeader * speedLeader) / leaderDecelerationEstimated));
	}
	else{
		SpeedDecelerationComponent = DBL_MAX;
	}
	if (factorSqrt>0){
		SpeedDecelerationComponent = bnTau + (double)sqrt(factorSqrt);//the double results in always having the same value in 32/64 bit
	}
	return SpeedDecelerationComponent;
}

double behavioralModelParticular::computeMinimumGap(A2SimVehicle *vehicleUp,A2SimVehicle *vehicleDown,bool VehicleIspVehDw, int time)
{ // Do not touch this
	double DecelFactorUp = 1;
	
	double tau = vehicleUp->getReactionTime();

	double Xup, Vup, Xdw, Vdw;
	double gap = vehicleUp->getGap(0, vehicleDown, 0, Xup, Vup, Xdw, Vdw, time);

	double GapMin = 0;
	if (Vdw<0.01){
		GapMin = max(0., 0.5*Vup*tau + max(0., -Vup*Vup / (2 * vehicleUp->getDeceleration()) + DecelFactorUp*(1. - 0.5*DecelFactorUp)*vehicleUp->getDeceleration()*tau*tau + (1 - DecelFactorUp)*Vup*tau));
		if (DecelFactorUp>-Vup / (vehicleUp->getDeceleration())*tau){
			GapMin = max(0., 0.5*Vup*tau);
		}
	}
	else{
		double DecelEstimada = vehicleUp->getEstimationOfLeadersDeceleration(vehicleDown, Vdw);
		GapMin = max(0., (Vdw*Vdw) / (2 * DecelEstimada) + 0.5*Vup*tau + max(0., -Vup*Vup / (2 * vehicleUp->getDeceleration()) + DecelFactorUp*(1. - 0.5*DecelFactorUp)*vehicleUp->getDeceleration()*tau*tau + (1 - DecelFactorUp)*Vup*tau));
		if (DecelFactorUp>-Vup / (vehicleUp->getDeceleration())*tau){
			GapMin = max(0., (Vdw*Vdw) / (2 * DecelEstimada) + 0.5*Vup*tau);
		}
	}
	return GapMin;
}

bool behavioralModelParticular::avoidCollision(A2SimVehicle *vehicle,A2SimVehicle *vehiclePre,double ShiftPre)
{ // Do not touch this
	return false;
}

