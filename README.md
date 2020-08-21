# Collaborative Mutil-agent planning of autonomous taxis: A Case Study in New York Manhattan island


 Hello, everyone, welcome to the "New York autonomous taxi intelligent planning" projects.
 
 # Data source
 
 
 The data used in this research were collected from taxi data-sets in Manhattan island, New York from November 1st-7st, 2019 on Yellow Cab's website https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page.
 
 # Simulation basic background
 

To obtain the performance of our planning framework, a Monte Carlo simulation is introduced in this work. In the simulation phase, 3000 autonomous taxis are randomly generated in the network on 00:00 am per day, and each day will be treated as an episode with 144 steps in the simulator.

The data mainly contains trip's location (origin and destination), generating time and fees etc. The study area is divided into 67 locations and comprised of 164 edges  according to the real-world road network of Manhattan. Note that trip requests falling outside the spatial boundary will be disregarded, and recorded origins, destinations, taxis' positions will be converted to the locations in $L$. Shortest paths and travel times among all locations are pre-calculated and stored in a look-up table. 
 
 
