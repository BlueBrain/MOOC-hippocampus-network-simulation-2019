
from os import makedirs
from os.path import join, exists, isdir, basename
import pyunicore.client as unicore_client


class Results:

    UNICORE_ENDPOINT = 'https://bspsa.cineca.it/advanced/pizdaint/rest/core'
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
        file_content = x.raw().read()

        if file_name == 'BlueConfig':
            bc_str = file_content.decode('utf-8')
            writable_content = bc_str.replace(self.ORIGIN_CIRCUIT_PATH, self.circuit_dir)
            writable_content = writable_content.replace(self.ORIGIN_DIR_PATH, self.local_dir)
            writable_content = writable_content.encode('utf-8')
        else:
            writable_content = file_content

        with open(file_output_path, 'wb') as fd:
            fd.write(writable_content)

        print('- [{}] downloaded'.format(file_name))

    def download_blueconfig(self, file_name='BlueConfig'):
        self.download_file_to_storage(file_name)

    def download_report(self):
        # find report
        report = next((x for x in self.files_list if '_report_' in x), None)
        if not report:
            print('No reports were found')
            return
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
