from setuptools import setup, find_packages

setup(
    name='database-utility',
    version='1.0.0',
    description='Enterprise-grade Python CLI tool for database backup and restore',
    author='Garvit Agrawal',
    author_email='garvitagrawal321@gmail.com',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'PyYAML>=6.0',
        'python-dotenv>=0.19.0',
        'PyMySQL>=1.0.0',
        'psycopg2-binary>=2.9.0',
        'pymongo>=4.0.0',
    ],
    extras_require={
        'cloud': [
            'boto3>=1.26.0',
            'google-cloud-storage>=2.0.0',
            'azure-storage-blob>=12.0.0',
        ],
        'scheduling': [
            'APScheduler>=3.10.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-mock>=3.10.0',
            'pytest-cov>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'db-backup=src.cli:cli',
        ],
    },
    python_requires='>=3.8',
)
