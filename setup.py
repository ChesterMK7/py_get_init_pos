from setuptools import find_packages, setup

package_name = 'py_get_init_pos'

setup(
    name=package_name,
    version='1.1.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Adam Kitchen',
    maintainer_email='kitchear@clarkson.edu',
    description='Converts NavSatFix GPS data into localized XY coordinates for Nav2, created for the' \
    ' Scout 2.0 Autonomous Navigation Project at Clarkson University.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
	    'gps_convert = py_get_init_pos.gps_convert:main',
        'orientation_calc = py_get_init_pos.orientation_experimental:main',
        ],
    },
)
