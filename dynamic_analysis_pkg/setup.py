from setuptools import setup

setup(name='dynamic-analysis-pkg',
      version='0.2.1',
      description='Machinary to fetch simulation results to a Jupyter Notebook',
      author='BlueBrain NSE',
      author_email='bbp-ou-nse@groupes.epfl.ch',
      license='MIT',
      packages=['dynamic_analysis_pkg'],
      install_requires=[
        'pyunicore>=0.8.2',
        'tabulate>=0.8.7',
        'tqdm>=4.51.0',
      ],
      zip_safe=True)
