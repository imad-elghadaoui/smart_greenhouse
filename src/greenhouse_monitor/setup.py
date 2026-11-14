from setuptools import setup

package_name = 'greenhouse_monitor'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='imad-elghadaoui',
    maintainer_email='imad.elghadaoui@usmba.ac.ma',
    description='Data logging and alerting for the smart greenhouse.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'data_logger_node = greenhouse_monitor.data_logger_node:main',
            'alert_system_node = greenhouse_monitor.alert_system_node:main',
        ],
    },
)
