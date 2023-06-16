from numpy import histogram, log, sum, abs, multiply
from numpy.random import uniform
from HighD_parameters import *
from Aimsun_parameters import *

class SPSA(HighDData, AimsunData):
    """Class for the SPSA algorithm"""
    def __init__(self, filename1, filename2, file_input:str = '1'):
        super().__init__(file_input=file_input)
        
        try:
            self.c1
        except AttributeError:
            self.getconnection(filename1, filename2)
        
    def KL_divergence(self, p, q, POI, bins:int=20, epsilon:float=1e-10)->float:
        """ Compute KL divergence of two distributions 
        p and q are two distributions values retrieved from Aimsun and HighD

        parameters:
            p: distribution (Aimsun)
            q: distribution (HighD)
            bins: number of bins for histogram
            epsilon: small number to avoid nan and inf values
        
        Returns:
            PQ: PQ matrix (difference of distribution) KL divergence
            PQ_sum: KL divergence
        """
        if POI == 'TTC':
            lb = 0
            ub = 199
        elif POI == 'DRAC':
            lb = 0
            ub = 1
        else:
            lb = min([min(p),min(q)])
            ub = max([max(p),max(q)])
            if POI == 'Truck_speed': # Unrealistic speed values removed
                ub = 95
        
        # Bin size adjustment for density and DRAC
        binsave = bins
        if POI == 'Density' or POI == "DRAC":
            bins = 10
        else:
            bins = binsave

        # Compute counts in the ranges
        [n1, _] = histogram(p, bins=bins, range=[lb, ub])
        [n2, _] = histogram(q, bins=bins, range=[lb, ub])

        # normalize the counts:
        n1 = n1/len(p)
        n2 = n2/len(q)

        # Replace zeros with small number to avoid nan and inf values
        n1[n1==0] = epsilon
        n2[n2==0] = epsilon

        # Compute KL divergence
        PQ = n1*log(n1/n2)
        
        return sum(PQ)
    
    def param_clip(self, param)->np.array:
        """Clip parameters to be within the range of the parameters
        
        parameters:
            param: parameters to be clipped
        
        Returns:
            clipped parameters"""
        
        min_val = np.array([50, 40, 2.6, 0.6, 3.5, 2.5,0,0, 0.5, 0.5, 450, 80, 0,0])
        max_val = np.array([200, 120, 3.4, 1.8, 4.5, 4.8, 1, 1, 1.5, 3, 550, 100, 5, 5])

        return np.clip(param, min_val, max_val)

    def get_new_params(self, params, amp):
        """
        Get parameters for the gradient approximation

        parameters:
            params: original parameters
            index: index of parameter to be changed
            amp: factor to adjust the amplitude of the perturbation

        Returns:
            params1: random perturbation added to original parameters
            params2: random perturbation subtracted from original parameters
        """

        # Generate random perturbation (w/ amplitude adjustment factor)
        delta = uniform(-1, 1, size=len(params))
        delta = multiply(delta, amp)

        # Add weights to have different scales for different parameters

        params1 = params.copy()
        params2 = params.copy()

        self.params1 = self.param_clip(params1 + delta)
        self.params2 = self.param_clip(params2 - delta)

        # Calculate the new delta (After clipping)
        new_delta = (self.params1 - self.params2)/2
        for i in range(len(new_delta)):
            if new_delta[i] == 0:
                new_delta[i] = 1000 # Set to a large number to avoid division by zero
        self._delta = new_delta
        

        print("[CarMaxdesiredSpeed, TruckMaxdesiredSpeed, CarMaxAcceleration, TruckMaxAccerlation,\n CarNormalDeceleration, TruckNormalDeceleration, CarSensitivityFactor, TruckSensistivityFactor,\n CarReactionTime, TruckReactionTime, CarVehicleDemand, TruckVehicleDemand,\n CarGap, TruckGap]\n")
        
        print(f"manual input of gradient parameters:\n ", self.params1, "\n", self.params2)

        return self.params1, self.params2
    
    def update_params(self, param:list, ck:float = 100, alpha:float=0.01, Validation:bool=False)->list:
        """Computation of loss function and return of optimal parameters
        
        parameters:
            param (list): original parameters
            ck (float): learning rate
            alpha (float): step size

        Returns:
            param (list): updated parameters
        """

        POIs = ['TTC', 'DRAC', 'Truck_speed', 'Car_speed', 'Density']   # Parameters of interest (POIs)
        Loss_weights = [1, 1, 1, 1, 1]                                  # Relative weight for each POI, in same order as above

        if Validation:
            direction = input("Which direction do you want to use: 1 or 2?")
            direction = eval(direction)
            assert direction == 1 or direction == 2, "Please enter 1 or 2"
        else:
            direction = 1

        HighD_dict = self.Aggregated_HighD_values(direction=direction)
        Aimsun_dict_1 = self.Aggregated_Aimsun_values(self.c1)          # Has to be made available when changed in Aimsun_parameters.py
        Aimsun_dict_2 = self.Aggregated_Aimsun_values(self.c2)          # Has to be made available when changed in Aimsun_parameters.py

        # Compute KL divergence for each POI
        loss1 = 0
        loss2 = 0
        l1 = []
        l2 = []
        for i, POI in enumerate(POIs):
            loss1 = Loss_weights[i]*self.KL_divergence(Aimsun_dict_1[POI], HighD_dict[POI], POI)
            l1.append(loss1)
            loss2 = Loss_weights[i]*self.KL_divergence(Aimsun_dict_2[POI], HighD_dict[POI], POI)
            l2.append(loss2)
        
        # Update parameters (Calibration)/ Return loss (Validation)
        if not Validation:
            grad = ((sum(l1) - sum(l2))/(2*ck*abs(self._delta).T))

            param -= alpha*grad
            print("updated parameters", param)

            if sum(l1) < sum(l2):
                loss = l1
                bparams = self.params1
            else:
                loss = l2
                bparams = self.params2
            print(f"With Loss: {loss}")

            return self.param_clip(param), bparams, loss
        else:
            print(l1)
            return l1