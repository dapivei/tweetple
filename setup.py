from setuptools import setup

setup(
    name='tweetple',
    version='0.13007',
    author='Daniela Pinto Veizaga',
    author_email='danielapintoveizaga@gmail.com',
    description='A python wrapper for users of the Academic Research product track',
    packages=['tweetple'],
    install_requires = [
       'certifi==2021.10.8',
       'charset-normalizer==2.0.7',
       'cramjam==2.5.0',
       'decorator==5.1.0',
       'fsspec==2021.11.0',
       'idna==3.3',
       'numpy==1.21.4',
       'pandas==1.3.4',
       'pyarrow==6.0.1',
       'python-dateutil==2.8.2',
       'pytz==2021.3',
       'requests==2.26.0',
       'setuptools==58.3.0',
       'six==1.16.0',
       'thrift==0.15.0',
       'tqdm==4.62.3',
       'urllib3==1.26.7',
       'validators==0.18.2',
       'wheel==0.37.0'
    ],
    url='https://github.com/dapivei/tweetple',
    zip_safe=False
)
