from setuptools import setup

setup(name='dynamic_analysis_pkg',
      version='0.1.7',
      description='Machinary to fetch simulation results to a Jupyter Notebook',
      author='Stefano Antonel',
      author_email='stefano.antonel@epfl.ch',
      license='MIT',
      packages=['dynamic_analysis_pkg'],
      install_requires=[
        'pyunicore',
        'tabulate',
      ],
      zip_safe=True)
