from setuptools import setup

setup(name='dynamic_analysis_pkg',
      version='0.1.6',
      description='Machinary to run analysis based on simulation url',
      author='Stefano Antonel',
      author_email='stefano.antonel@epfl.ch',
      license='MIT',
      packages=['dynamic_analysis_pkg'],
      install_requires=[
        'pyunicore',
      ],
      zip_safe=True)
