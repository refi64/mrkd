from setuptools import setup, find_packages

with open('README.md') as fp:
    readme = fp.read()

setup(
    name='mrkd',
    version='0.2.0',
    description='Write man pages using Markdown, and convert them to Roff or HTML',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Ryan Gonzalez',
    author_email='rymg19@gmail.com',
    license='BSD',
    url='https://github.com/refi64/mrkd',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['mrkd=mrkd:main'],
    },
    include_package_data=True,
    install_requires=['Jinja2', 'mistune', 'pygments'],
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: BSD License',
    ],
)
