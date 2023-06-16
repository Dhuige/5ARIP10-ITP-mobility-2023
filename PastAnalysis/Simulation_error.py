from numpy import histogram, log, sum, abs, multiply
from numpy.random import uniform
from HighD_parameters import *
from Aimsun_parameters import *

class SPSA(HighDData, AimsunData):
    """Class for the SPSA algorithm"""
    def __init__(self, filename1, filename2):
        super().__init__()
        
        try:
            self.c1
        except AttributeError:
            self.getconnection(filename1, filename2)
        
    def KL_divergence(self, p, q, POI, bins:int=20, epsilon:float=1e-10):
        """ Compute KL divergence of two distributions 
        p and q are two distributions
        parameters:
            p: distribution (Aimsun)
            q: distribution (HighD)
        Returns:
            PQ: PQ matrix (difference of distribution) KL divergence
            PQ_sum: KL divergence
        """
        if POI == 'TTC':
            lb = 0
            ub = 199
        elif POI == 'DRAC':
            lb = 0
            ub = 0.17
        else:
            lb = min([min(p),min(q)])
            ub = max([max(p),max(q)])

        [n1, _] = histogram(p, bins=bins, range=[lb, ub])
        [n2, _] = histogram(q, bins=bins, range=[lb, ub])
        
        # Normalize the histograms
        n1 = n1/len(p)
        n2 = n2/len(q)

        # Replace zeros with small number to avoid nan and inf values
        n1[n1==0] = epsilon
        n2[n2==0] = epsilon

        # Compute KL divergence
        PQ = n1*log(n1/n2)
        
        return sum(PQ)
    
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
        self._delta = delta

        # Add weights to have different scales for different parameters

        params1 = params.copy()
        params2 = params.copy()

        params1 = params1 + delta
        params2 = params2 - delta

        print("manual input of gradient parameters", params1, "\n", params2)

        return params1, params2
    
    def update_params(self, param, ck = 100, alpha:float=2):
        """Computation of loss function and return of optimal parameters
        
        parameters:
            param: original parameters
            delta: random perturbation
            highD: HighD data
            aimsun1: Aimsun data with parameters param + delta
            aimsun2: Aimsun data with parameters param - delta
            alpha: step size
        Returns:
            param: updated parameters
        """

        POIs = ['TTC', 'DRAC', 'Truck_speed', 'Car_speed', 'Density']   # Parameters of interest (POIs)
        Loss_weights = [1, 1, 1, 1, 1]                                  # Relative weight for each POI, in same order as above

        HighD_dict = self.Aggregated_HighD_values()
        Aimsun_dict_1 = self.Aggregated_Aimsun_values(self.c1)          # Has to be made available when changed in Aimsun_parameters.py
        Aimsun_dict_2 = self.Aggregated_Aimsun_values(self.c2)          # Has to be made available when changed in Aimsun_parameters.py

        loss1 = 0
        loss2 = 0

        for i, POI in enumerate(POIs):
            loss1 += Loss_weights[i]*self.KL_divergence(Aimsun_dict_1[POI], HighD_dict[POI], POI)
            loss2 += Loss_weights[i]*self.KL_divergence(Aimsun_dict_2[POI], HighD_dict[POI], POI)
        
        grad = ((loss1 - loss2)/(2*ck*abs(self._delta).T))

        param -= alpha*grad
        print("updated parameters", param)

        if loss1 < loss2:
            loss = loss1
        else:
            loss = loss2
        print(f"With Loss: {loss}")

        return param, loss