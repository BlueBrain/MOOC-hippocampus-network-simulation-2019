# MOOC-hippocampus-network-simulation-2019

### Create notebook in Collab

- Open https://collab.humanbrainproject.eu/#/collab/33645/nav/233818
- In Navigation (left side) click on ADD -> search for `sp6mooc` -> click Add to Navigation
- Example notebook https://collab.humanbrainproject.eu/#/collab/33645/nav/252688
- Beware of adding a placeholder like `SIMULATION_URL` so it is replaced and we can fetch the simulation results. (For testing I would suggest to comment this out and use directly the full url of your job)

### Put notebook in Github

Just download the notebook from the Collab (File -> Download) and upload it to the repo.

### Modify configuration

Once notebook was uploaded in Github, we need to add this notebook in the configuration so it is picked up by the simulation-launcher-ui.

Just add a dictionary (`{}`) into the configuration array.

```
[ ...,
  {
​    "name": "...",
​    "uri": "...",
​    "txtToReplace": "SIMULATION_URL",
​    "appId": 410
  }
]
```

##### The fields are the following:
`name`: (string) Name of the navigation item that will be created in the Collab when the user select this notebook.
`uri`: (string) Full url of the notebook in Github (to obtain this just open the notebook in Github and click on Raw, then copy the url).
`txtToReplace`: (string) Placeholder that must be present on the notebook for being replaced by the user simulation url.
`appId`: (number) [keep 410] Application id, normal jupyter notebook 175, notebook with mount 410.
