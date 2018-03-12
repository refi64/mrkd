from setuptools import setup


with open('requirements.txt') as fp:
    requirements = fp.read().splitlines()


setup(
    name='mrkd',
    description='Write man pages using Markdown, and convert them to Roff or HTML',
    version='0.1.1',
    author='Ryan Gonzalez',
    author_email='rymg19@gmail.com',
    license='BSD',
    url='https://github.com/kirbyfan64/mrkd',
    py_modules=['mrkd'],
    entry_points={
        'console_scripts': [
            'mrkd=mrkd:main',
        ],
    },
    package_data={
        '': ['template.html'],
    },
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: BSD License',
    ],
)
