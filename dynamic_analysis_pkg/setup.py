from setuptools import setup

setup(name='dynamic-analysis-pkg',
      version='0.2.2',
      description='Machinary to fetch simulation results to a Jupyter Notebook',
      author='BlueBrain NSE',
      author_email='bbp-ou-nse@groupes.epfl.ch',
      license='MIT',
      packages=['dynamic_analysis_pkg'],
      install_requires=[
        'tqdm>=4.51.0',
      ],
      zip_safe=True)
