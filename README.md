# MOOC-hippocampus-network-simulation-2019

### Create notebook in Collab

- Open https://collab.humanbrainproject.eu/#/collab/33645/nav/233818
- In Navigation (left side) click on ADD -> search for `sp6mooc` -> click Add to Navigation
- Example notebook https://collab.humanbrainproject.eu/#/collab/33645/nav/233822

### Put notebook in Github

1) Change:
    ```
    job_url = 'https://zam2125...'
    dynamic_analysis_pkg.fetch_results(oauth.get_token(), job_url)
    ```
    by
    ```
    dynamic_analysis_pkg.fetch_results(oauth.get_token(), SIMULATION_URL)
    ```

2) Download the notebook from the Collab (File -> Download)
3) Upload it to the Github repo

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
