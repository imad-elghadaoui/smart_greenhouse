from setuptools import setup

package_name = 'greenhouse_control'

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
    maintainer='imadelghadaoui',
    maintainer_email='imadelghadaoui@gmail.com',
    description='Greenhouse control package for managing ventilation and irrigation.',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ventilation_node = greenhouse_control.ventilation_node:main',
            'irrigation_node = greenhouse_control.irrigation_node:main',
        ],
    },
)
