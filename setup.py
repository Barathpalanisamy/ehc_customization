from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ehc_customization/__init__.py
from ehc_customization import __version__ as version

setup(
	name="ehc_customization",
	version=version,
	description="EHC",
	author="8848digital",
	author_email="developer@8848digital.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
