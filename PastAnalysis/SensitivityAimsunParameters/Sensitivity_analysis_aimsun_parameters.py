import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import openpyxl

# Import Aimsun and HighD data. Files should be made according to lines below.
from Pipeline.Aimsun_parameters import *

class SensitivityAnalysis:
    def __init__(self):
        self.mean_car_speed = []
        self.mean_truck_speed = []
        self.mean_densities = []
        self.mean_TTC = []
        self.mean_DRAC = []

    def parameters_analysis(self,Aimsun_car_speeds, 
                            Aimsun_truck_speeds, 
                            Aimsun_densities, 
                            Aimsun_TTCs, 
                            Aimsun_DRACs):
        self.mean_car_speed = np.mean(Aimsun_car_speeds)

        self.mean_truck_speed = np.mean(Aimsun_truck_speeds)

        self.mean_densities = np.mean(Aimsun_densities)

        # TTC values
        new_aimsun_TTCs = []
        for i in Aimsun_TTCs:
            if(i < 1000 and i >= 0):
                new_aimsun_TTCs.append(i)
        self.mean_TTC = np.mean(new_aimsun_TTCs)

        self.mean_DRAC = np.mean(Aimsun_DRACs)

    def save_to_excel(self):
        path = 'Sensitivity.xlsx'

        # dataframe with Name and Age columns
        df = pd.DataFrame({'mean_car_speed': [self.mean_car_speed], 'mean_truck_speed': [self.mean_truck_speed], 'density': [self.mean_densities], 'TTC': [self.mean_TTC], 'DRAC': [self.mean_DRAC]})

        # read  file content
        reader = pd.read_excel(path)

        # create writer object
        # used engine='openpyxl' because append operation is not supported by xlsxwriter
        writer = pd.ExcelWriter(path, engine='openpyxl', mode='a', if_sheet_exists="overlay")

        # append new dataframe to the excel sheet
        df.to_excel(writer, index=False, header=False, startrow=len(reader) + 1)

        # close file
        writer.close()

    def plot_figures(self):
        df = pd.read_excel('D:/Github/5ARIP10-TeamProject/SensitivityAimsunParameters/Sensitivity.xlsx')

        fig, axs = plt.subplots(5)
        axs[0].plot(df["mean_car_speed"].loc[1:])
        axs[1].plot(df["mean_truck_speed"].loc[1:])
        axs[2].plot(df["density"].loc[1:])
        axs[3].plot(df["TTC"].loc[1:])
        axs[4].plot(df["DRAC"].loc[1:])

        plt.show()
        
    def analysis(self):
        df = pd.read_excel('D:/Github/5ARIP10-TeamProject/SensitivityAimsunParameters/Sensitivity.xlsx')
        
        # baseline values are retrieved
        baseline = df.loc[1]

        # compute the error for each of the trials w.r.t the baseline value
        mean_car_speed_error = []
        mean_truck_speed_error = []
        mean_density_error = []
        mean_TTC_error = []
        mean_DRAC_error = []

        for i in range(len(df["mean_car_speed"].loc[2:])):
            mean_car_speed_error.append(abs(df["mean_car_speed"].loc[i+2] - baseline[0]))
            mean_truck_speed_error.append(abs(df["mean_truck_speed"].loc[i+2] - baseline[1]))
            mean_density_error.append(abs(df["density"].loc[i+2]- baseline[2]))
            mean_TTC_error.append(abs(df["TTC"].loc[i+2] - baseline[3]))
            mean_DRAC_error.append(abs(df["DRAC"].loc[i+2] - baseline[4]))

        # Retrieve data for each parameter
        # mean_car_speed = df["mean_car_speed"].loc[2:].to_numpy()
        # mean_truck_speed = df["mean_truck_speed"].loc[2:].to_numpy()
        # density = df["density"].loc[2:].to_numpy()
        # TTC = df["TTC"].loc[2:].to_numpy()
        # DRAC = df["DRAC"].loc[2:].to_numpy()
        
        # # Create a 2D array of the data
        # data = np.array([mean_car_speed, mean_truck_speed, density, TTC, DRAC])

        # # Compute the correlation coefficient matrix
        # correlation_matrix = np.corrcoef(data)

        # print(correlation_matrix)

        # print(mean_car_speed_error)
        # print(mean_truck_speed_error)
        # print(mean_density_error)
        # print(mean_TTC_error)
        # print(mean_DRAC_error)

        # plotting
        # fig, axs = plt.subplots(5)
        # axs[0].plot(mean_car_speed_error)
        # axs[1].plot(mean_truck_speed_error)
        # axs[2].plot(mean_density_error)
        # axs[3].plot(mean_TTC_error)
        # axs[4].plot(mean_DRAC_error)\
        values_rows = []

        for i in range(len(mean_car_speed_error)):
            values_rows.append([mean_car_speed_error[i], mean_truck_speed_error[i], mean_density_error[i], mean_TTC_error[i], mean_DRAC_error[i]])

        # Create a 2D array of the data
        data = np.array(values_rows)

        # Compute the correlation coefficient matrix
        correlation_matrix = np.corrcoef(data)

        print(correlation_matrix)

        path = 'D:/Github/5ARIP10-TeamProject/SensitivityAimsunParameters/PearsonsCoeff.xlsx'

        # dataframe with Name and Age columns
        df = pd.DataFrame(correlation_matrix)

        # read  file content
        reader = pd.read_excel(path)

        # create writer object
        # used engine='openpyxl' because append operation is not supported by xlsxwriter
        writer = pd.ExcelWriter(path, engine='openpyxl', mode='a', if_sheet_exists="replace")

        # append new dataframe to the excel sheet
        df.to_excel(writer, index=False, header=False, startrow=len(reader) + 1)

        # close file
        writer.close()

        plt.show()


if __name__ == "__main__":
    # Initialize data extraction
    # Aimsun = AimsunData()
    # Aimsun_car_speeds = Aimsun.getCarSpeed()
    # Aimsun_truck_speeds = Aimsun.getTruckSpeed()
    # Aimsun_intensities = Aimsun.getIntensity()
    # Aimsun_densities = Aimsun.getDensity()
    # Aimsun_TTCs = Aimsun.getTTC()
    # Aimsun_DRACs = Aimsun.getDRAC()
    sensitivity = SensitivityAnalysis()
    # The functions below can be called to add data to the excel file after running a simulation
    # sensitivity.parameters_analysis(Aimsun_car_speeds, 
    #                  Aimsun_truck_speeds, 
    #                  Aimsun_densities, 
    #                  Aimsun_TTCs, 
    #                  Aimsun_DRACs)
    # save_to_excel()
    # sensitivity.plot_figures()
    sensitivity.analysis()
