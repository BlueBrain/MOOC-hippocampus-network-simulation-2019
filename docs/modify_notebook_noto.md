## Modify a notebook for developers

### 1) Open Jupyter Lab
- Open [EDX course](https://courseware.epfl.ch/courses/course-v1:EPFL+SimNeuro2+2019_2/courseware/ba6f8be8f0bb4956a94147f7a09e4cf4/f949d2c29dd94e1aa86bdc0d7a69c3fe/1?activate_block_id=block-v1%3AEPFL%2BSimNeuro2%2B2019_2%2Btype%40vertical%2Bblock%40e7654d4da7334108b7fa55e2338e41e5)
- Click on `Open Jupyter Lab` button on section **Open Jupyter Lab (prod)**
- After the Jupyter Lab is open you can check the content of the notebooks

### 2) Create a new branch to work on
Open a terminal in jupyter lab (File -> New -> Terminal)
```
cd ~/MOOC-hippocampus-network-simulation-2019
git fetch --all
git checkout -b YOUR_NEW_BRANCH_NAME origin/master
```

### 3) Modify notebook and save changes
- Modify the notebook

### 4) Commit changes
- Use the git extension on the left panel or the jupyter terminal to commit the changes
- Push the changes to `git push origin/YOUR_NEW_BRANCH_NAME`
