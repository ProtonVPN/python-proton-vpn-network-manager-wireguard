#!/usr/binn/env python
from setuptools import setup, find_namespace_packages

setup(
    name="proton-vpn-network-manager-wireguard",
    version="0.0.2",
    description="Proton Technologies VPN connector for linux",
    author="Proton Technologies",
    author_email="contact@protonmail.com",
    url="https://github.com/ProtonVPN/pyhon-protonvpn-network-manager-wireguard",
    packages=find_namespace_packages(include=['proton.vpn.backend.linux.networkmanager.protocol.wireguard']),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=["proton-core", "proton-vpn-network-manager", "pygobject"],
    extras_require={
        "development": ["pytest", "pytest-cov", "pygobject-stubs"]
    },
    entry_points={
        "proton_loader_nm_protocol": [
            "wireguard = proton.vpn.backend.linux.networkmanager.protocol.wireguard:Wireguard",
        ]
    },
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
