# pylint: disable=missing-function-docstring
'''Machinary to fetch simulation results to a Jupyter Notebook'''
from pathlib import Path
import requests
from tqdm.notebook import tqdm


BLUE_CONFIG = 'BlueConfig'
SIMULATION_CONFIG = 'simulation_config.json'


class Results:
    '''
    Based on a simulation id, fetch the results using Unicore API
    '''
    DEFAULT_CIRCUIT_DIR = Path('/home/data-bbp/20191017/')
    DEFAULT_WD_BASE = Path('/home/simulation-results')
    ORIGIN_CIRCUIT_PATH = Path('/gpfs/bbp.cscs.ch/project/proj133/circuit/mooc-circuit/')
    HPC_DIR_BASE = Path('/gpfs/bbp.cscs.ch/project/proj133/scratch/unicore/')

    VMM_BASE_URL = 'https://bbp-mooc-sim-neuro.epfl.ch/vmm/rest/core'
    VMM_JOBS_URL = f'{VMM_BASE_URL}/jobs?tags=simulation,mooc_bb5'
    VMM_FILE_LIST_URL = f'{VMM_BASE_URL}/storages/{{JOB_ID}}-uspace/files'


    def __init__(self, token, sim_id, base_working_directory=None, new_circuit_path=None):

        if base_working_directory is None:
            base_working_directory = self.DEFAULT_WD_BASE
        if new_circuit_path is None:
            new_circuit_path = self.DEFAULT_CIRCUIT_DIR

        self.files_list = None
        self.files_endpoint = None
        self.headers = { 'Authorization': token }

        self.circuit_dir = Path(new_circuit_path)
        if not self.circuit_dir.is_dir():
            raise ValueError('[ERROR] Circuit path does not exists')

        self.local_dir = Path(base_working_directory) / sim_id
        self.local_dir.mkdir(parents=True, exist_ok=True)

        self.hpc_dir_path = self.HPC_DIR_BASE / sim_id

        self.fetch_results(token, sim_id)
        self.blueconfig = self.local_dir / BLUE_CONFIG
        self.simulation_config = self.local_dir / SIMULATION_CONFIG

    def get_id_from_url(self, url):
        return url.split('/').pop()

    def fetch_results(self, token, sim_id):
        print(f'Fetching results for {sim_id}')
        self.retrieve_sim_info(sim_id)
        self.get_sim_results()

    def retrieve_sim_info(self, sim_id):
        self.files_endpoint = self.VMM_FILE_LIST_URL.replace('{JOB_ID}', self.get_id_from_url(sim_id))
        response = requests.get(self.files_endpoint, headers=self.headers)
        if not response.ok:
            if response.status_code == 401:
                raise ValueError('[ERROR] Token has expired. Get a new one in EDX')
            else:
                raise ValueError(response)
        children = response.json()['children']
        self.files_list = [f.replace('/', '') for f in children]

    def get_sim_results(self):
        self.download_file_to_storage(BLUE_CONFIG)
        self.download_file_to_storage(SIMULATION_CONFIG)
        self.download_report()
        self.download_file_to_storage('out.dat')
        print(f'Result were saved at: {self.local_dir}')

    def download_file_to_storage(self, file_name):
        ''' function to download the file and add it to kernel file system '''
        file_output_path = self.local_dir / file_name
        if file_output_path.exists():
            print(f'- [{file_name}] file already exists. Skipping download.')
            return

        print(f'- Fetching file [{file_name}] ...')
        file_url = f'{self.files_endpoint}/{file_name}'
        file_resp = requests.get(file_url, headers=self.headers)

        if file_name in [BLUE_CONFIG, SIMULATION_CONFIG]:
            writable_content = file_resp.text.replace(str(self.ORIGIN_CIRCUIT_PATH), str(self.circuit_dir))
            writable_content = writable_content.replace(str(self.hpc_dir_path), str(self.local_dir))

            with open(file_output_path, 'w') as fd:
                fd.write(writable_content)

        else:
            file_resp = requests.get(file_url, headers=self.headers)
            with open(file_output_path, 'wb') as f:
                f.write(file_resp.content)

    def download_report(self):
        reports = [x for x in self.files_list if x.endswith('.h5')]
        if not reports:
            print('No reports were found')
        for report in reports:
            self.download_file_to_storage(report)


class FetchMultipleResults:
    '''
    Fetch results based on a list of job_ids
    '''
    def __init__(self, token, sim_list_ids, base_working_directory=None):
        self.values = []
        for sim in tqdm(sim_list_ids):
            self.values.append(Results(token, sim, base_working_directory))
