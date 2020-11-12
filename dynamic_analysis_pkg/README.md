## Package to pull simulation results to Notebook


### Import package
```
import dynamic_analysis_pkg
from collab_oidc_client.oidc.client import BBPOIDCClient
```

### Get HBP token
```
USER = 'YOUR_HBP_USERNAME'
oidc = BBPOIDCClient.implicit_auth(user=USER)
```

### Find job based on a list
```
finder = dynamic_analysis_pkg.JobFinder(oidc.credentials.access_token)
finder.show_list(25)
```

### Pick the job by index
`job_id = finder.find_id_by_index()`

### OR select a job by id
`job_id = 'YOUR_JOB_ID'`



### Pull the files
`sim_result = dynamic_analysis_pkg.Results(oidc.credentials.access_token, job_id)`

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
