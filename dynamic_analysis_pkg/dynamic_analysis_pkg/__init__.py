
from os import makedirs
from os.path import join, exists, isdir, basename
from shutil import move
import pyunicore.client as unicore_client


class Results:

    DEFAULT_WD = '/home/jovyan/tmp/test_pull_unicore'

    HPC_CONSTANTS = {
        'NUVLA': {
            'URL': 'https://zam2125.zam.kfa-juelich.de:9112/NUVLA/rest/core',
            'CIRCUIT': '/mnt/circuits/O1/20181114',
        },
        'PIZ_DAINT': {
            'URL': 'https://brissago.cscs.ch:8080/DAINT-CSCS/rest/core',
            'CIRCUIT': '/store/hbp/ich002/antonel'
        }
    }

    hpc_base_url = None
    files_list = None
    local_dir = None
    blueconfig = None
    hpc_name = None


    def __init__(self, token, sim_id, hpc_name=None, base_working_directory=None):
        if not token:
            print('[ERROR] token was not provided')
            return

        if not sim_id:
            print('[ERROR] simulation id was not provided')
            return

        self.hpc_name = hpc_name if hpc_name else 'NUVLA'

        self.hpc_base_url = self.HPC_CONSTANTS[self.hpc_name]['URL']

        base_working_directory = base_working_directory if base_working_directory else self.DEFAULT_WD

        self.define_paths(base_working_directory, sim_id)
        self.fetch_results(token, sim_id)
        self.blueconfig = join(self.local_dir, 'BlueConfig')


    def define_paths(self, working_directory, sim_id):
        self.local_dir = join(working_directory, sim_id)
        if not exists(self.local_dir):
            makedirs(self.local_dir)


    def fetch_results(self, token, sim_id):
        self.retrieve_sim_info(token, sim_id)
        self.get_sim_results()


    def retrieve_sim_info(self, token, sim_id):
        jobs_base = join(self.hpc_base_url, 'jobs')
        job_url = join(jobs_base, sim_id)
        tr = unicore_client.Transport(token)
        job = unicore_client.Job(tr, job_url)
        print('Fetching results of: {}'.format(job.properties['name']))
        storage = job.working_dir
        self.files_list = storage.listdir()


    def get_sim_results(self):
        self.download_blueconfig()
        self.download_report()
        self.download_out_dat()


    def download_blueconfig(self, file_name='BlueConfig'):
        self.download_file_to_storage(file_name)


    def download_file_to_storage(self, file_name):
        # function to download the file and add it to kernel file system
        new_path = join(self.local_dir, file_name)
        x = self.files_list[file_name]

        if file_name == 'BlueConfig':
            # modify the paths
            file_content = x.raw().read()

            if self.hpc_name == 'NUVLA':
                writable_content = file_content.replace('/mooc', '/mnt')
                writable_content = writable_content.replace('/io', self.local_dir)

            if self.hpc_name == 'PIZ_DAINT':
                original_path = self.HPC_CONSTANTS[self.hpc_name]['CIRCUIT']
                writable_content = file_content.replace(original_path, '/mnt')
                writable_content = writable_content.replace('CurrentDir .', 'CurrentDir {}'.format(self.local_dir))
                writable_content = writable_content.replace('OutputRoot .', 'OutputRoot {}'.format(self.local_dir))

            with open(new_path, 'w') as fd:
                fd.write(writable_content)

        else:
            x.download(str(file_name)) # moves to home always
            move(file_name, new_path)

        print('- {} downloaded'.format(file_name))


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
