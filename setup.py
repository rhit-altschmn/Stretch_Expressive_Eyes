from setuptools import find_packages, setup

package_name = 'expressive_eyes'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*')),
        ('share/' + package_name + '/rviz', glob('rviz/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sharelab2',
    maintainer_email='altschmn@rose-hulman.edu',
    description='expressive eyes for stretch robot',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        	'eye_listener=new_expressive_eyes.eye_listener_node:main',
        	'keyboard_input=new_expressive_eyes.keyboard_driver:main'
        ],
    },
)
