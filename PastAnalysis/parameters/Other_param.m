clear all
clc
%%
data = readtable('01_tracksMeta.csv');
data(data.drivingDirection == 2, :) = [];
%%
idx = strfind(data.class, 'Car');
idx = find(not(cellfun('isempty', idx)));
idx1 = strfind(data.class, 'Truck');
idx1 = find(not(cellfun('isempty', idx1)));
Num_cars = length(idx)
Num_trucks = length(idx1)
%% 
truck = data(cellfun(@isempty, strfind(data.class, 'Car')), :);
truck_length = table2array(truck(:,2));
truck_width = table2array(truck(:,3));


car = data(cellfun(@isempty, strfind(data.class, 'Truck')), :);
car_length = table2array(car(:,2));
car_width = table2array(car(:,3));

truck_length_mean = mean(truck_length)
truck_length_std  = std(truck_length)
truck_length_min  = min(truck_length)
truck_length_max  = max(truck_length)

truck_width_mean = mean(truck_width)
truck_width_std  = std(truck_width)
truck_width_min  = min(truck_width)
truck_width_max  = max(truck_width)

car_length_mean = mean(car_length)
car_length_std  = std(car_length)
car_length_min  = min(car_length)
car_length_max  = max(car_length)

car_width_mean = mean(car_width)
car_width_std  = std(car_width)
car_width_min  = min(car_width)
car_width_max  = max(car_width)

%% For myself not correct values
truck_speed = table2array(truck(:,12));
truck_speed_mean = mean(truck_speed)*3.6
truck_speed_max = max(table2array(truck(:,11)))*3.6


car_speed = table2array(car(:,12));
car_speed_mean = mean(car_speed)*3.6
car_speed_max = max(table2array(car(:,11)))*3.6


