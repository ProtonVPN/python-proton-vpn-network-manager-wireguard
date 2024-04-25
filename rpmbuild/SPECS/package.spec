%define unmangled_name proton-vpn-network-manager-wireguard
%define version 0.0.7
%define release 1

Prefix: %{_prefix}

Name: python3-%{unmangled_name}
Version: %{version}
Release: %{release}%{?dist}
Summary: %{unmangled_name} library

Group: ProtonVPN
License: GPLv3
Vendor: Proton Technologies AG <opensource@proton.me>
URL: https://github.com/ProtonVPN/%{unmangled_name}
Source0: %{unmangled_name}-%{version}.tar.gz
BuildArch: noarch
BuildRoot: %{_tmppath}/%{unmangled_name}-%{version}-%{release}-buildroot

BuildRequires: python3-proton-vpn-network-manager
BuildRequires: python3-proton-vpn-killswitch-network-manager-wireguard
BuildRequires: python3-setuptools

Requires: python3-proton-vpn-network-manager
Requires: python3-proton-vpn-killswitch-network-manager-wireguard
Requires: python3-setuptools

%{?python_disable_dependency_generator}

%description
Package %{unmangled_name} library.


%prep
%setup -n %{unmangled_name}-%{version} -n %{unmangled_name}-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES


%files -f INSTALLED_FILES
%{python3_sitelib}/proton/
%{python3_sitelib}/proton_vpn_network_manager_wireguard-%{version}*.egg-info/
%defattr(-,root,root)

%changelog
* Thu Apr 25 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.0.7
- Show wireguard protocol as experimental in app settings

* Wed Apr 17 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.0.6
- Add wireguard kill switch dependency

* Thu Apr 4 2024 Alexandru Cheltuitor <alexandru.cheltuitor@proton.ch> 0.0.5
- Add UI friendly protocol name

* Fri Mar 1 2024 Alexandru Cheltuitor <alexandru.cheltuitor@proton.ch> 0.0.4
- Use WireGuard ports

* Mon Feb 26 2024 Alexandru Cheltuitor <alexandru.cheltuitor@proton.ch> 0.0.3
- Refactor code so that the package can be usable

* Wed Jun 1 2022 Proton Technologies AG <opensource@proton.me> 0.0.2
- First RPM release
