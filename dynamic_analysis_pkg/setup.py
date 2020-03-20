from setuptools import setup

setup(name='dynamic-analysis-pkg',
      version='0.1.7',
      description='Machinary to fetch simulation results to a Jupyter Notebook',
      author='BlueBrain NSE',
      author_email='bbp-ou-nse@groupes.epfl.ch',
      license='MIT',
      packages=['dynamic_analysis_pkg'],
      install_requires=[
        'pyunicore>=0.5.7',
        'tabulate>=0.8.6',
        'tqdm>=4.36.1',
      ],
      zip_safe=True)
