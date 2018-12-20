
import pprint
from os import makedirs
from os.path import join, exists, isdir, basename
import pyunicore.client as unicore_client

base = 'https://zam2125.zam.kfa-juelich.de:9112/NUVLA/rest/core'
job_base = join(base, 'jobs')
files_list = None
circuit_dir = None
local_dir = None


def define_paths(working_directory='/home/jovyan/tmp/test_pull_unicore',
                 circuit_config='/mnt/circuits/O1/20181114'):
  global local_dir
  global circuit_dir

  local_dir = working_directory
  if not exists(local_dir):
    print('Creating working directory: {}'.format(working_directory))
    makedirs(local_dir)

  if not isdir(circuit_config):
    circuit_directory = basename(circuit_config)
  else:
    circuit_directory = circuit_config
  circuit_dir = circuit_directory


def download_file_to_storage(file_name):
  # function to download the file and add it to kernel file system
  x = files_list[file_name]
  file_content = x.raw().read()

  new_path = join(local_dir, file_name)

  if file_name == 'BlueConfig':
      writable_content = file_content.replace('/mooc', '/mnt')
      writable_content = writable_content.replace('/io', local_dir)
  else:
      writable_content = file_content

  with open(new_path, 'w') as fd:
      fd.write(writable_content)

  print('- {} downloaded'.format(file_name))


def retrieve_sim_info(token, sim_url=None):
  tr = unicore_client.Transport(token)
  job_url = sim_url
  job = unicore_client.Job(tr, job_url)
  print('Fetching results from: {}'.format(job.properties['name']))
  storage = job.working_dir
  # print('Files:')
  global files_list
  files_list = storage.listdir()
  # pprint.pprint(files_list)


def download_blueconfig(file_name='BlueConfig'):
  # pull the BlueConfig with Unicore
  download_file_to_storage(file_name)


def download_report():
  # find report
  report = next((x for x in files_list if '_report_' in x), None)
  # pull report
  download_file_to_storage(report)


def download_out_dat():
  # pull the out.dat
  download_file_to_storage('out.dat')


def get_sim_results():
  download_blueconfig()
  download_report()
  download_out_dat()


def fetch_results(token, sim_url=None):
  if not sim_url:
    print('[Error] Provide Simulation URL')
    return
  retrieve_sim_info(token, sim_url)
  get_sim_results()
  return Results()


class Results:
  def __init__(self):
    self.blueconfig = join(local_dir, 'BlueConfig')
