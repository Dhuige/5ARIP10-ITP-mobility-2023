# Calibration Of Traffic Micro-Simulation For Modelling The Effects Of Autonomous Vehicle Integration On Traffic Safety
_abstract:_ 
The testing of autonomous vehicles (AVs) is troublesome since testing in a real-world environment is unsafe. For this reason, agent-based traffic modelling software Aimsun Next is used to replicate a real-world traffic scenario from HighD trajectory data. Simultaneous Perturbation Stochastic Approximation (SPSA) and a loss function based on the Kullback-Leibler divergence test are used to calibrate a traffic micro-simulation. The application of SPSA yields car-follower parameters that lower the loss. However, the number of iterations taken to calibrate the system is found to be insufficient to conclude the convergence of the calibration. The penetration rate of AVs is tested in the calibrated simulation. For AV penetration rates until 50\%, AVs do not contribute much towards improving traffic safety. However, increasing the penetration rate further than 50\% increases safety.


## Application:
This software can be applied in combination with the HighD dataset to calibrate the Aimsun Next 22 simulation environment. The software can also be used to test the effects of AVs on traffic safety in a safe environment.

For further information about the software, please read the [documentation.md](documentation.md) file.

## Installation:
The software can be installed by cloning the repository. The software is written in Python 3.9 and uses the following packages:
```
 - os
 - numpy
 - sqlite
 - pandas
 - matplotlib
```
The software can be installed by running the following command in the terminal:
```
conda env create -f environment.yml
```

## Usage
The usage of the software is described in the [documentation.md](documentation.md) file.

## Credits:
Credits to our coach, Dr. A. Tejada Ruiz, for his guidance and support during the project. Credits to the HighD dataset for providing the data used in this project.

## License:
MIT License
