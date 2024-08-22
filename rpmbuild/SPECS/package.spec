%define unmangled_name proton-vpn-network-manager-wireguard
%define version 0.4.5
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

BuildRequires: python3-proton-vpn-logger
BuildRequires: python3-proton-vpn-api-core >= 0.33.0
BuildRequires: python3-proton-vpn-network-manager
BuildRequires: python3-proton-vpn-killswitch-network-manager-wireguard
BuildRequires: python3-setuptools

Requires: python3-proton-vpn-logger
Requires: python3-proton-vpn-api-core >= 0.33.0
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
* Thu Aug 22 2024 Luke Titley <luke.titley@proton.ch> 0.4.5
- Dont request features for free users, even on updates

* Thu Aug 22 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.4.4
- Expose property to signal that feature updates can be applied to active WG connections

* Wed Aug 21 2024 Luke Titley <luke.titley@proton.ch> 0.4.3
- Dont request features for free users

* Wed Aug 15 2024 Luke Titley <luke.titley@proton.ch> 0.4.2
- Resume local agent connection after deserializing persisted connection

* Tue Aug 13 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.4.1
- Fix certificate expired error handling regression

* Fri Aug 09 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.4.0
- Request local agent connection features

* Thu Aug 8 2024 Luke Titley <luke.titley@proton.ch> 0.3.1
- Notify subscribers if the maximum number of open vpn sessions is reached.

* Thu Aug 08 2024 Luke Titley <luke.titley@proton.ch> 0.3.0
- Handle certificate expiration midway through a session

* Wed Aug 07 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.2.0
- Notify when agent connection goes down

* Fri Jul 26 2024 Alexandru Cheltuitor <alexandru.cheltuitor@proton.ch> 0.1.0
- Notify subscribers whenever we have and expired certificate so it can be refreshed.

* Wed Jul 24 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.0.13
- Handle local agent server pushing status messages

* Thu Jul 18 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.0.12
- Handle expired certificate error raised when getting certificate in PEM format

* Wed Jul 17 2024 Luke Titley <luke.titley@proton.ch> 0.0.11
- Switch over to newer local agent api

* Fri Jul 12 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.0.10
- Reestablish local agent connection when client is started up with an active connection

* Wed Jul 10 2024 Josep Llaneras <josep.llaneras@proton.ch> 0.0.9
- Add proton-vpn-api-core dependency.

* Tue Jul 9 2024 Luke Titley <luke.titley@proton.ch> 0.0.8
- Added implementation of local agent connections.

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
