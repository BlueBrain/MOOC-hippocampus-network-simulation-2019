# pylint: disable=missing-function-docstring
'''Machinary to fetch simulation results to a Jupyter Notebook'''
from pathlib import Path, PurePath
from shutil import move
from datetime import datetime
import logging
import os
import pandas as pd
from tabulate import tabulate
import pyunicore.client as unicore_client
from tqdm.notebook import tqdm

L = logging.getLogger('dynamic-analysis-pkg')
L.setLevel(logging.INFO)

UNICORE_ENDPOINT = 'https://bspsa.cineca.it/advanced/pizdaint/rest/core'


class AResults:
    '''
    Based on a simulation id, fetch the results using Unicore API
    '''
    DEFAULT_CIRCUIT_DIR = '/home/data-bbp/20191017/'
    DEFAULT_WD_BASE = '/home/simulation-results'
    ORIGIN_CIRCUIT_PATH = '/store/hbp/ich002/antonel/O1/20191017/'
    HPC_DIR_BASE = '/scratch/snx3000/unicore/FILESPACE/'
    JOB_BASE = os.path.join(UNICORE_ENDPOINT, 'jobs')

    def __init__(self, token, sim_id, base_working_directory=None, new_circuit_path=None):
        self.hpc_dir_path = None
        self.files_list = None
        self.circuit_dir = None
        self.local_dir = None

        if base_working_directory is None:
            base_working_directory = self.DEFAULT_WD_BASE
        if new_circuit_path is None:
            new_circuit_path = self.DEFAULT_CIRCUIT_DIR

        self.define_paths(sim_id, base_working_directory, new_circuit_path)
        self.fetch_results(token, sim_id)
        self.blueconfig = Path(self.local_dir) / 'BlueConfig'

    def fetch_results(self, token, sim_id=None):
        if not sim_id:
            raise ValueError('[Error] Simulation ID not provided')

        self.retrieve_sim_info(token, sim_id)
        self.get_sim_results()

    def retrieve_sim_info(self, token, sim_id=None):
        tr = unicore_client.Transport(token)
        job_url = os.path.join(self.JOB_BASE, sim_id)
        job = unicore_client.Job(tr, job_url)
        job_name = job.properties['name']
        L.info('Fetching results of [%s]. Please wait ...', job_name)
        storage = job.working_dir
        self.files_list = storage.listdir()

    def get_sim_results(self):
        self.download_file_to_storage('BlueConfig')
        self.download_report()
        self.download_file_to_storage('out.dat')
        L.info('Result were saved at: %s', self.local_dir)

    def define_paths(self, sim_id, working_directory, new_circuit_path):
        if not Path(new_circuit_path).is_dir():
            raise ValueError('[ERROR] Circuit path does not exists')
        else:
            self.circuit_dir = new_circuit_path

        self.local_dir = Path(working_directory) / Path(sim_id)
        self.local_dir.mkdir(parents=True, exist_ok=True)

        self.hpc_dir_path = Path(self.HPC_DIR_BASE) / Path(sim_id)

    def download_file_to_storage(self, file_name):
        ''' function to download the file and add it to kernel file system '''
        file_output_path = Path(self.local_dir) / Path(file_name)
        if file_output_path.exists():
            L.info('- [%s] file already exists. Skipping download.', file_name)
            return

        L.info('- Fetching [%s] ...', file_name)
        current_file = self.files_list[file_name]

        if file_name == 'BlueConfig':
            file_content = current_file.raw().read()
            bc_str = file_content.decode('utf-8')
            writable_content = bc_str.replace(self.ORIGIN_CIRCUIT_PATH, self.circuit_dir)
            writable_content = writable_content.replace(str(self.hpc_dir_path), str(self.local_dir))

            with open(file_output_path, 'w') as fd:
                fd.write(writable_content)

        else:
            current_file.download(file_name) # moves to home always
            move(file_name, file_output_path)

        L.info('- [%s] downloaded', file_name)

    def download_report(self):
        reports = [x for x in self.files_list if x.endswith('.bbp')]
        if not reports:
            L.info('No reports were found')
            return
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


class AJobFinder:
    '''
    List the jobs launched using Uncicore in the Service Account Piz-Daint
    '''
    def __init__(self, token):
        self.sorted_jobs = None
        self.sorted_results = None
        tr = unicore_client.Transport(token)
        client = unicore_client.Client(tr, UNICORE_ENDPOINT)
        self.jobs = client.get_jobs()

    def show_list(self, amount_jobs_to_show=1000):
        full_jobs_list = []
        fetched_index = 0
        for job in tqdm(self.jobs[:amount_jobs_to_show], desc='Fetching jobs'):
            raw_time = job.properties['submissionTime']
            full_time = datetime.strptime(raw_time, '%Y-%m-%dT%H:%M:%S%z')
            date = full_time.strftime('%d-%m-%Y %H:%M')
            name = job.properties['name']
            status = job.properties['status']
            job_id = PurePath(job.properties['_links']['self']['href']).name
            full_jobs_list.append([fetched_index, name, date, job_id, full_time, status])
            fetched_index += 1

        columns = ['index', 'name', 'date', 'job_id', 'timestamp', 'status']
        self.sorted_results = pd.DataFrame(full_jobs_list, columns=columns).sort_values(
            by=["timestamp"]
        )

        showing_columns = ['index', 'name', 'date', 'status']
        # insert index for user selection
        self.sorted_results['index'] = range(0, amount_jobs_to_show)
        print(tabulate(self.sorted_results[showing_columns],
                       headers=showing_columns,
                       showindex=False))

    def find_id_by_index(self):
        job_selection_index = input('Please select the index that you want to import:')
        try:
            selected_index = int(job_selection_index)
        except:
            raise ValueError('ERROR: enter correct index')

        selection = self.sorted_results.iloc[int(selected_index)]
        job_id = selection['job_id']
        L.info('ID: %s', job_id)
        return job_id
