# Collaborative Mutil-agent planning of autonomous taxis: A Case Study in New York Manhattan island


 Hello, everyone, welcome to the "New York autonomous taxi intelligent planning" projects.
 
 
 The data used in this research were collected from taxi data-sets in Manhattan island, New York from November 1st-7st, 2019 on Yellow Cab's website $\footnote{https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page}$. The data mainly contains trip's location (origin and destination), generating time and fees etc. The study area is divided into 67 locations(operating zones) and comprised of 164 edges according to the real-world road network of Manhattan. Shortest paths and travel times between all locations are pre-calculated and stored in a look-up table.Moreover, there are some hyper-parameters used in this phase: the action searching threshold $\delta=10min$, the matching parameter $\widehat{\theta}$ is set to $0.94$ by logistic regression from real-world data.

To obtain the performance of our planning framework and comparisons with other policies, a Monte Carlo simulation is introduced in this paper. In the simulation phase, 3000 autonomous taxis are randomly generated in the network on 00:00 am per day, and there are two baseline heuristics compared with our system:
 
 
