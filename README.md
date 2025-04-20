# Project Overview 

This repository contains the code for data collection and data processing that supports the research in the following papers:

## Spaceport Facility Location Planning within the US National Airspace System

This paper introduces a Spaceport Facility Location Planning (SPFLP) model to help plan the locations of the next generation of US spaceports to accommodate the rising demands of rocket launches. The model: 

- Optimizes launch site selection across all U.S. counties by minimising a composite cost that includes transportation & construction expenses, launch Δv requirements, and the cost of rerouting commercial flights.
- Imposes realistic constraints on population overflight, feasible launch azimuths, and minimum separation between potential launch sites to preserve resilience.
- Quantifies National Airspace System (NAS) impacts so that air‑traffic delays, fuel burn, and inequitable congestion are explicitly captured in the objective function.
- Supports sensitivity studies — varying rocket launch path hazard‑zone width, cost weights, and daily air traffic volume — to show how different assumptions shift optimal site choices and flight‑rerouting costs.

## Natural‑Disaster‑Resilient Spaceport Network Planning

This paper builds upon the "Spaceport Facility Location Planning within the US National Airspace System" paper to offer a chance-constrained extention to the SPFLP model (CC-SPFLP). The CC-SPFLP model aims to choose new U.S. spaceport locations such that 1) aggregate launch demand is met and 2) the spaceport network can continue to operate with sufficient probability despite natural disasters occuring. 

The model begins with the deterministic facility location planning problem as a baseline then adds the chance-constrained extension by
- building probability distributions for natural disaster occurrences from county-level FEMA annual-frequency data
- introducing impact factors that incorporate effects of each hazard's frequency, duration, and severity 

# Codebase Overview

## `candidates`

Initial program that determines the range of launch azimuths for coastal counties that you can feasibly launch a rocket from without putting the population in harm's way. Later replaced with `ECA`.

## `ECA`

Expected Casualty Analysis. Finds the valid launch azimuths at each U.S. county from which you can feasibly launch a rocket from. The program uses a raster image of the US population data, overlays the hazard zone from a rocket's particular launch angle, and determines if the angle is valid based on whether the hazard zone 
1. flies over a small enough population
2. does not fly into Mexico or Canada

The program has tunable parameters for sensitivity analysis including 
1. Population limit that the rocket launch angle's hazard zone can fly over 
2. The spread angle of the hazard zone from the initial launch angle to tune its size 

## `flightclub`
Program to analyze past rocket launch data that is found from flightclub.io. Determines historically frequent launch angles and where past launches placed their hazard zones. 

## `haochen`
CSV data and python program provided from research team contributor Haochen Wu.

## `jackson`
CSV data and matlab program provided from research team contributor Jackson Miller.

## `Lat_Long`
Plots lattitude and longitude of launch trajectories from data pulled out of flightclub.io simulations.

## `Resiliency`
Pulls the annual frequencies of 8 natural disasters from FEMA county-level natural disaster data. Plots frequency maps to show where on the US the natural disasters occur most often. 

## `US_border`
Data for where the continental US border lies. 


# Citing this work
If you use this repository, please cite both papers:

- Wu, H., Sun, K. R., Miller, J. A., Jia-Richards, O., & Li, M. Z. (2024). Spaceport Facility Location Planning within the US National Airspace System. arXiv. https://doi.org/10.48550/arXiv.2402.11389= {2024}

- Wu, H., Lin, Y. S., Sun, K. R., Koduru, T., Cinar, G., Johnson, A. W., Jia-Richards, O., & Li, M. Z. (2024). Natural disaster-resilient spaceport network planning. AIAA Scitech 2024 Forum. https://doi.org/10.2514/6.2024-4930