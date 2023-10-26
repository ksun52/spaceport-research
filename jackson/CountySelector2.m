clear
clc


%%This File is intended to analyze flight data and place coordinates within
%%their nearest county. It was created by Jackson Miller in coordination
%%with the Aerospace Department at the University of Michigan

%% This area inputs an outline of the US, plots it, and cleans it

%Set rectangle boundaries around continental US
USLatMin = 24.585;
USLatMax = 49.3;
USLonMin = -125.1;
USLonMax = -65.47;

%Read in the datapoints from the original Contintental data and the cleaned
%data. The cleaned data was manually selected out of the us_continental
%data file in order to create a polygon usable for the "inpolygon" function
USData = readtable('us_continental.csv');
BetterUSDATA = readmatrix('Clean_US_Boundaries.xlsx');


%set and plot the original US data. When plotted as lines rather than
%scatter points there should be crisscrossing lines across the US
ylatgeo = table2array(USData(:,1));
xlongeo = table2array(USData(:,2));
figure(5)
geoplot(ylatgeo,xlongeo);


%Remove any values of data that are outside of the above designated square
%around the US(removes alaska)
index = table2array(USData(:,1)) < USLatMax & table2array(USData(:,1)) > USLatMin & table2array(USData(:,2)) < USLonMax & table2array(USData(:,2)) > USLonMin;
filteredOpensky = USData(index, :);

%Turns the opensky data into a table
latgeo = table2array(filteredOpensky(:,1));
longeo = table2array(filteredOpensky(:,2));

%plot the complex polygon of the continental US
figure(6)
geoplot(latgeo,longeo);

%plots the simple polygon of the continental US(the manually set data)
figure(7)
geoplot(BetterUSDATA(:,1),BetterUSDATA(:,2));





%% This area inputs and cleans the opensky data

%read in data
OpenskyData = readtable("Day1_5min.csv", 'PreserveVariableNames', true);
OpenskyDatax = readmatrix("Day1_5min.csv");
OpenskyData.Properties.VariableNames = ["x1", "lat", "lon", "x2", "time", "callsign"];


%Repeated: Set rectangle boundaries around continental US
USLatMin = 24.585;
USLatMax = 49.3;
USLonMin = -125.1;
USLonMax = -65.47;

%Determine original size of data and ouput it
Datalength = height(OpenskyData);
fprintf('Original Matrix Size Is: %d \n', height(OpenskyData.lat));

%remove rows that do not have latitude and longitude values recorded,
%output the new datasize
OpenskyData1 = OpenskyData(~(string(OpenskyData.lat) == "" | string(OpenskyData.lat)  == "lat"),:);
fprintf('Matrix Size After clearing "Lat" and "_" is: %d \n', height(OpenskyData1.lat))

%Change the commas in the datafile to periods so that matlab can accurately
%plot and do calculations
OpenskyData1.lat = num2cell(double(strrep(string(OpenskyData1.lat), ",", ".")));
OpenskyData1.lon = num2cell(double(strrep(string(OpenskyData1.lon), ",", ".")));

%remove any datapoints that are outside the designated rectangle around the
%US (If this had not been done when pulling from OpenSky
index = double(string(OpenskyData1.lat)) < USLatMax & double(string(OpenskyData1.lat)) > USLatMin & double(string(OpenskyData1.lon)) < USLonMax & double(string(OpenskyData1.lon)) > USLonMin;
filteredOpensky = OpenskyData1(index, :);

%Outut the new datasize
fprintf('Matrix Size After clearing latitudes and longitudes outside rectangle of US: %d \n', height(filteredOpensky))

%repeated: Change the commas in the datafile to periods
filteredOpensky.lat = num2cell(double(strrep(string(filteredOpensky.lat), ",", ".")));
filteredOpensky.lon = num2cell(double(strrep(string(filteredOpensky.lon), ",", ".")));

%ensure that the latitude and longitudes 
FilteredLat = double(string(filteredOpensky.lat));
FilteredLon = double(string(filteredOpensky.lon));



%% This area inputs and cleans the county Data

%%Read in Files to get data
%This contains data including a central lattitude and longitude data point
%for each  of the US counties. It would be possible to do the same thing
%for states as well. 

%read in County Data(
CountyData = readtable("us-county-boundaries.csv", 'PreserveVariableNames', true);

% Extract columns for county Name
countynames = table2array(CountyData(:,8));
LengthofCountyData = height(countynames);

%pull out the latitude and longitude coordinates of each county
for i = 1:LengthofCountyData
    long = double(extractAfter(string(CountyData{i,1}), ", "));
    lat = double(extractBefore(string(CountyData{i,1}), ", "));
    countylatitudes(i) = lat;
    countylongitudes(i) = long;
end
countylongitudes = countylongitudes';
countylatitudes = countylatitudes';


%% 

flightlatitudes = FilteredLat;
flightlongitudes = FilteredLon;
lengthofFlightData = height(FilteredLat);

%% This area of code seperates counties that are above the Us and Above the ocean

%create vectors before seperating other information
LatsAboveUS = [];
LonsAboveUS = [];
LatsAboveOcean = [];
LonsAboveOcean = [];

%Place 
for i = 1:lengthofFlightData
    x = inpolygon(flightlongitudes(i),flightlatitudes(i),BetterUSDATA(:,2), BetterUSDATA(:,1));
    if x == 1
        LatsAboveUS = [LatsAboveUS, flightlatitudes(i)];
        LonsAboveUS = [LonsAboveUS, flightlongitudes(i)];
    else 
        LatsAboveOcean = [LatsAboveOcean, flightlatitudes(i)];
        LonsAboveOcean = [LonsAboveOcean, flightlongitudes(i)];
    end
end

%output how many are above ocean and above US
fprintf('Number of counties flown over in US: %d \n', length(LatsAboveUS));
fprintf('Number of counties outside US: %d \n', length(LatsAboveOcean));



%% This code begins to find the desired list of counties flown over

%set the AboveUs as the new FlightLats
flightlatitudes = LatsAboveUS;
flightlongitudes = LonsAboveUS;

%create the vector for county indeces
closestCountyInd = [];

%Find the location in the vector of counties where each flight point is and
%add it to the clostestCountyIND vector
for i = 1:length(flightlatitudes)
    lat = double(string(flightlatitudes(i)));
    lon = double(string(flightlongitudes(i)));
    countydists = sqrt( (lat - countylatitudes).^2 + (lon - countylongitudes).^2);
    [minDist, closestIndex] = min(countydists);
    closestCountyInd = [closestCountyInd, closestIndex];

end

%ClosestCountyIND is a vector whose length is the number of counites
%selected, and at each place is one of the counties selected 

%Get the latitude and longitude coordinates for each county flown over
for i = 1:length(closestCountyInd)
    CountiesFlownOver(i) = countynames(closestCountyInd(i));
end 




%%%%%Still needs to be done
    %How long is the time taken actually
    %How Many flights are over a county



%simplify the counties and the county locations
SimplifiedIndex = unique(closestCountyInd);
LatitudesOfCountiesFlownOver = countylatitudes(SimplifiedIndex);
LongitudesOfCountiesFlownOver = countylongitudes(SimplifiedIndex);
[GC,GR] = groupcounts(closestCountyInd');
% GR is the list of county indexes, GC is how many times each respective county was
% selected 

%create a table that holds the county names and how many times they were
%flown over

countynames2 = cell2table(countynames(GR));
FlownOverXTimes = array2table(GC);

Counties = [countynames2,FlownOverXTimes, array2table(LatitudesOfCountiesFlownOver),array2table(LongitudesOfCountiesFlownOver)];
Counties.Properties.VariableNames = ["County Name", "Flown Over X Times", "Center Latitidude", "Center Longitude"];



%%This section Finishes plotting relevant graphs

%Plotting All County Locations and All Flight Points
figure(1)
geoscatter(countylatitudes,countylongitudes, '.');
geolimits([-15 70],[-180 60])
geobasemap streets
title('Scatter Plot of all US Counties')

hold off

%Plotting the lat and long locations of each flight location
figure(2)
geoscatter(flightlatitudes,flightlongitudes, '.');
geobasemap streets
title('Flight Data')

figure(3)
geoscatter(flightlatitudes,flightlongitudes);
title('Flight Data')
hold on

%plotting the counties selected as being flown over
figure(4)
geoscatter(LatitudesOfCountiesFlownOver,LongitudesOfCountiesFlownOver, 'blue');
geobasemap streets
title('Counties Flown Over');


uniquecountynames = unique(countynames);