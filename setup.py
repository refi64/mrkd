from setuptools import setup, find_packages

with open('requirements.txt') as fp:
    requirements = fp.read().splitlines()

setup(
    name='mrkd',
    description='Write man pages using Markdown, and convert them to Roff or HTML',
    version='0.1.7',
    author='Ryan Gonzalez',
    author_email='rymg19@gmail.com',
    license='BSD',
    url='https://github.com/refi64/mrkd',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['mrkd=mrkd:main', ],
    },
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: BSD License',
    ],
)
