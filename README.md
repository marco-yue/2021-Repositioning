# Collaborative Mutil-agent planning of autonomous taxis: A Case Study in New York Manhattan island


 Hello, everyone, welcome to the "New York autonomous taxi intelligent planning" projects.
 
 Data source
 ==
 
 
 The data used in this research were collected from taxi data-sets in Manhattan island, New York from November 1st-7st, 2019 on Yellow Cab's website https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page.
 
 We process the trip-related dataset in [Data processing procedure](https://github.com/marco-yue/Autonomous-taxis-planning/blob/master/01Preparation.py), other data was avaiable on my [Google Drive](https://drive.google.com/drive/folders/1SGAjXBZg75YRwe7NC7xNWlBJHkkKTTxi?usp=sharing).
 
 If you want to recur our work, you need to download the whole data to replace the ‘Data.file’ under this directory.
 
 Simulation basic background
 ==
 

In the simulation phase, 

* 3000 autonomous taxis are randomly generated in the network on 00:00 am per day.

* each day will be treated as an episode with 144 steps in the simulator.

* the study area is divided into 67 locations and comprised of 164 edges.

Benchmark heuristics
==

There are two baseline heuristics compared with our approach:

* [Hotspot walk](https://github.com/marco-yue/Autonomous-taxis-planning/blob/master/03%20Hot_spot.py), essentially defines a stochastic policy for each agent, which indicates that the actions will be chosen according to the probability  computed by trips quantity at each step.

* [DiDi repositioning](https://github.com/marco-yue/Autonomous-taxis-planning/blob/master/04DiDi_repositioning.py), employs a centralized optimization framework to determine the repositioning tasks(next pick-up location) of each taxi. Each task will be assigned by solving the Mixed-integer linear programming (MILP) model.


 
 
