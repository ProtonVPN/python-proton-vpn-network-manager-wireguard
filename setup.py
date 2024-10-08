#!/usr/binn/env python
from setuptools import setup, find_namespace_packages

setup(
    name="proton-vpn-network-manager-wireguard",
    version="0.4.7",
    description="Proton VPN Wireguard NM connector for linux",
    author="Proton AG",
    author_email="opensource@proton.me",
    url="https://github.com/ProtonVPN/pyhon-protonvpn-network-manager-wireguard",
    packages=find_namespace_packages(include=['proton.vpn.backend.linux.networkmanager.protocol.*']),
    include_package_data=True,
    install_requires=[
        "proton-vpn-api-core", "proton-vpn-logger", "proton-vpn-network-manager",
        "proton-vpn-killswitch-network-manager-wireguard"
    ],
    extras_require={
        "development": ["wheel", "pytest", "pytest-cov", "pytest-asyncio", "flake8", "pylint", "pygobject-stubs"]
    },
    python_requires=">=3.8",
    license="GPLv3",
    platforms="OS Independent",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python",
        "Topic :: Security",
    ]
)
