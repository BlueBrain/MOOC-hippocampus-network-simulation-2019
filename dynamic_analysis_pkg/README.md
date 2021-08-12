## Package to pull simulation results to Notebook


### Import package
```
import dynamic_analysis_pkg
```

### Get token
This should be provided by EDX to use for this exercise
`token = 'YOUR_EDX_TOKEN'`

### Select a job by id
`job_id = 'YOUR_JOB_ID'`

### Pull the files
`sim_result = dynamic_analysis_pkg.Results(token, job_id)`

### Get the paths to:
```
sim_result.blueconfig
sim_result.circuit_dir
sim_result.local_dir
sim_result.simulation_config
```


## Use the results
```
from bluepysnap import Simulation
sim = Simulation(sim_result.simulation_config)
spikes = sim.spikes
hippocampus_spikes = spikes["hippocampus_neurons"]
hippocampus_spikes.nodes.get(group=hippocampus_spikes.node_ids).head()
```
