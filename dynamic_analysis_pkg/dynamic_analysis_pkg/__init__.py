
from os import makedirs
from os.path import join, exists, isdir, basename
from shutil import move
from datetime import datetime
from tabulate import tabulate
import pyunicore.client as unicore_client
import pandas as pd

UNICORE_ENDPOINT= 'https://bspsa.cineca.it/advanced/pizdaint/rest/core'


class Results:

    DEFAULT_CIRCUIT_DIR = '/home/data-bbp/20191017/'
    DEFAULT_WD_BASE = '/home/simulation-results';
    ORIGIN_CIRCUIT_PATH = '/store/hbp/ich002/antonel/O1/20191017/'
    ORIGIN_DIR_PATH = '/scratch/snx3000/unicore/FILESPACE/'
    job_base = join(UNICORE_ENDPOINT, 'jobs')
    files_list = None
    circuit_dir = None
    local_dir = None
    blueconfig = None

    def __init__(self, token, sim_id, base_working_directory=None, new_circuit_path=None):
        if base_working_directory == None:
            base_working_directory = self.DEFAULT_WD_BASE
        if new_circuit_path == None:
            new_circuit_path = self.DEFAULT_CIRCUIT_DIR

        self.define_paths(sim_id, base_working_directory, new_circuit_path)
        self.fetch_results(token, sim_id)
        self.blueconfig = join(self.local_dir, 'BlueConfig')

    def fetch_results(self, token, sim_id=None):
        if not sim_id:
            print('[Error] Simulation ID not provided')
            return
        self.retrieve_sim_info(token, sim_id)
        self.get_sim_results()

    def retrieve_sim_info(self, token, sim_id=None):
        tr = unicore_client.Transport(token)
        job_url = join(self.job_base, sim_id)
        job = unicore_client.Job(tr, job_url)
        print('Fetching results of [{}]. Please wait ...'.format(job.properties['name']))
        storage = job.working_dir
        self.files_list = storage.listdir()

    def get_sim_results(self):
        self.download_blueconfig()
        self.download_report()
        self.download_out_dat()
        print('Result were saved at: {}'.format(self.local_dir))

    def define_paths(self, sim_id, working_directory, new_circuit_path):
        self.local_dir = join(working_directory, sim_id)
        if not exists(self.local_dir):
            makedirs(self.local_dir)

        if not isdir(new_circuit_path):
            print('[ERROR] Circuit path does not exists')
        else:
            self.circuit_dir = new_circuit_path

        self.ORIGIN_DIR_PATH = join(self.ORIGIN_DIR_PATH, sim_id)

    def download_file_to_storage(self, file_name):
        # function to download the file and add it to kernel file system
        file_output_path = join(self.local_dir, file_name)
        if exists(file_output_path):
            print('- [{}] file already exists. Skipping download.'.format(file_name))
            return

        print('- Fetching [{}] ...'.format(file_name))
        x = self.files_list[file_name]

        if file_name == 'BlueConfig':
            file_content = x.raw().read()
            bc_str = file_content.decode('utf-8')
            writable_content = bc_str.replace(self.ORIGIN_CIRCUIT_PATH, self.circuit_dir)
            writable_content = writable_content.replace(self.ORIGIN_DIR_PATH, self.local_dir)

            with open(file_output_path, 'w') as fd:
                fd.write(writable_content)

        else:
            x.download(str(file_name)) # moves to home always
            move(file_name, file_output_path)

        print('- [{}] downloaded'.format(file_name))

    def download_blueconfig(self, file_name='BlueConfig'):
        self.download_file_to_storage(file_name)

    def download_report(self):
        reports = [x for x in self.files_list if '.bbp' in x]
        if not reports:
            print('No reports were found')
            return
        for report in reports:
            self.download_file_to_storage(report)

    def download_out_dat(self):
        self.download_file_to_storage('out.dat')


class FetchMultipleResults:

    values = []

    def __init__(self, token, sim_list_ids, base_working_directory=None):

        total_sims = len(sim_list_ids)
        for idx, sim in enumerate(sim_list_ids):
            print('({}/{})'.format(idx + 1, total_sims))
            self.values.append(Results(token, sim, base_working_directory))


class JobFinder:

    jobs = []
    sorted_jobs = None

    def __init__(self, token):
        tr = unicore_client.Transport(token)
        client = unicore_client.Client(tr, UNICORE_ENDPOINT)
        self.jobs = client.get_jobs()

    def show_list(self, amount_jobs_to_show=None):
        full_jobs_list = []
        if amount_jobs_to_show is None:
            amount_jobs_to_show = 1000

        for index, job in enumerate(self.jobs[:amount_jobs_to_show]):
            raw_time = job.properties['submissionTime']
            full_time = datetime.strptime(raw_time, '%Y-%m-%dT%H:%M:%S%z')
            date = full_time.strftime('%d-%m-%Y %H:%M')
            name = job.properties['name']
            job_id = basename(job.properties['_links']['self']['href'])
            full_jobs_list.append([index, name, date, job_id])
            print('Fetching jobs ({}/{})'.format(index + 1, amount_jobs_to_show or len(jobs) + 1), end = '\r')

        columns = ['index', 'name', 'date', 'job_id']
        self.sorted_results = pd.DataFrame(full_jobs_list, columns=columns).sort_values(by=['date'])

        pd.options.display.max_columns = None
        pd.options.display.width=None

        print('\n') # to stop the \r
        showing_columns = ['index', 'name', 'date']
        # insert index for user selection
        self.sorted_results['index'] = range(0, amount_jobs_to_show)
        print(tabulate(self.sorted_results[showing_columns], headers=showing_columns, showindex=False))


    def find_id_by_index(self):
        job_selection_index = input('Please select the index that you want to import:')
        try:
            selected_index = int(job_selection_index)
        except:
            print('ERROR: enter correct index')

        selection = self.sorted_results.iloc[int(selected_index)]
        job_id = selection['job_id']
        print('ID: {}'.format(job_id))
        return job_id
