# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1

%global service novajoin

Name:           python-%{service}
Version:        XXX
Release:        XXX
Summary:        Nova integration to enroll IPA clients

License:        ASL 2.0
URL:            https://launchpad.net/novajoin
Source0:        https://tarballs.openstack.org/%{service}/%{service}-%{version}.tar.gz
Source1:        novajoin.logrotate

BuildArch:      noarch

%description
A nova vendordata plugin for the OpenStack nova metadata
service to manage host instantiation in an IPA server.

%package -n     python%{pyver}-%{service}
Summary:        Nova integration to enroll IPA clients
%{?python_provide:%python_provide python%{pyver}-%{service}}

Requires:       python%{pyver}-webob
Requires:       python%{pyver}-six
Requires:       python%{pyver}-keystoneclient >= 1:3.8.0
Requires:       python%{pyver}-keystoneauth1 >= 3.4.0
Requires:       python%{pyver}-oslo-config >= 6.1.0
Requires:       python%{pyver}-oslo-concurrency >= 3.25.0
Requires:       python%{pyver}-oslo-messaging >= 5.29.0
Requires:       python%{pyver}-oslo-policy >= 1.30.0
Requires:       python%{pyver}-oslo-serialization >= 2.18.0
Requires:       python%{pyver}-oslo-service >= 1.24.0
Requires:       python%{pyver}-oslo-utils >= 3.33.0
Requires:       python%{pyver}-neutronclient >= 6.7.0
Requires:       python%{pyver}-novaclient >= 1:9.1.0
Requires:       python%{pyver}-cinderclient >= 3.3.0
Requires:       python%{pyver}-glanceclient >= 1:2.8.0
Requires:       python%{pyver}-keystonemiddleware >= 4.17.0

Requires:       ipa-admintools

# Handle python2 exception
%if %{pyver} == 2
Requires:       python-paste
Requires:       python-routes
Requires:       python-cachetools >= 2.0.0
%else
Requires:       python%{pyver}-paste
Requires:       python%{pyver}-routes
Requires:       python%{pyver}-cachetools >= 2.0.0
%endif

%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

BuildRequires:  python%{pyver}-webob
BuildRequires:  python%{pyver}-routes
BuildRequires:  python%{pyver}-six
BuildRequires:  python%{pyver}-keystoneclient
BuildRequires:  python%{pyver}-keystoneauth1
BuildRequires:  python%{pyver}-oslo-concurrency
BuildRequires:  python%{pyver}-oslo-messaging
BuildRequires:  python%{pyver}-oslo-policy
BuildRequires:  python%{pyver}-oslo-serialization
BuildRequires:  python%{pyver}-oslo-service
BuildRequires:  python%{pyver}-oslo-utils
BuildRequires:  python%{pyver}-neutronclient
BuildRequires:  python%{pyver}-novaclient
BuildRequires:  python%{pyver}-cinderclient
BuildRequires:  python%{pyver}-glanceclient
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  git
BuildRequires:  systemd
BuildRequires:  python%{pyver}-hacking
BuildRequires:  python%{pyver}-fixtures
BuildRequires:  python%{pyver}-mock
BuildRequires:  python%{pyver}-subunit
BuildRequires:  python%{pyver}-testtools
BuildRequires:  python%{pyver}-testrepository
BuildRequires:  python%{pyver}-testresources
BuildRequires:  python%{pyver}-testscenarios
BuildRequires:  python%{pyver}-stestr
BuildRequires:  openstack-macros

# Handle python2 exception
%if %{pyver} == 2
BuildRequires:  python-paste
BuildRequires:  python-anyjson
BuildRequires:  python-sphinx_rtd_theme
%else
BuildRequires:  python%{pyver}-paste
BuildRequires:  python%{pyver}-anyjson
BuildRequires:  python%{pyver}-sphinx_rtd_theme
%endif

%description -n python%{pyver}-%{service}
A nova vendordata plugin for the OpenStack nova metadata
service to manage host instantiation in an IPA server.

%package -n python%{pyver}-%{service}-tests-unit
Summary:        Unit tests for novajoin
%{?python_provide:%python_provide python%{pyver}-%{service}-tests-unit}
Requires:       python%{pyver}-%{service} = %{version}-%{release}

Requires:       python%{pyver}-fixtures
Requires:       python%{pyver}-mock
Requires:       python%{pyver}-subunit
Requires:       python%{pyver}-testtools
Requires:       python%{pyver}-testrepository
Requires:       python%{pyver}-testresources
Requires:       python%{pyver}-testscenarios
Requires:       python%{pyver}-os-testr
# Handle python2 exception
%if %{pyver} == 2
Requires:       python-anyjson
%else
Requires:       python%{pyver}-anyjson
%endif


%description -n python%{pyver}-%{service}-tests-unit
Unit test files for the novajoin service.

%if 0%{?with_doc}
%package -n python%{pyver}-%{service}-doc
Summary:        %{name} documentation
%{?python_provide:%python_provide python%{pyver}-%{service}-doc}

BuildRequires:  python%{pyver}-oslo-sphinx
BuildRequires:  python%{pyver}-sphinx

# Handle python2 exception
%if %{pyver} == 2
BuildRequires:  python-sphinx_rtd_theme
%else
BuildRequires:  python%{pyver}-sphinx_rtd_theme
%endif

%description -n python%{pyver}-%{service}-doc
%{common_desc}

It contains the documentation for Novajoin.
%endif

%prep
%autosetup -n %{service}-%{upstream_version} -S git

%py_req_cleanup

%build

%{pyver_build}

# Generate config file
PYTHONPATH=. oslo-config-generator-%{pyver} --config-file=files/novajoin-config-generator.conf

%if 0%{?with_doc}
# generate html docs
sphinx-build-%{pyver} doc/source html
# remove the sphinx-build-%{pyver} leftovers
rm -rf html/.{doctrees,buildinfo}
%endif

%install
%{pyver_install}

# Setup directories
install -d -m 755 %{buildroot}%{_mandir}/man1
install -d -m 755 %{buildroot}%{_datadir}/%{service}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{service}
install -d -m 755 %{buildroot}%{_localstatedir}/log/novajoin

# Install generated config file
install -p -D -m 640 files/join.conf %{buildroot}%{_sysconfdir}/novajoin/join.conf

# install log rotation configuration
install -p -D -m 644 -p %{SOURCE1} \
  %{buildroot}%{_sysconfdir}/logrotate.d/novajoin

# Install the upstream-provided systemd unit files
install -p -D -m 644 %{buildroot}%{_datarootdir}/novajoin/novajoin-notify.service \
  %{buildroot}%{_unitdir}/novajoin-notify.service
install -p -D -m 644 %{buildroot}%{_datarootdir}/novajoin/novajoin-server.service \
  %{buildroot}%{_unitdir}/novajoin-server.service
rm -f %{buildroot}%{_datarootdir}/novajoin/novajoin-notify.service
rm -f %{buildroot}%{_datarootdir}/novajoin/novajoin-server.service

%check
PYTHON=%{pyver_bin} stestr-%{pyver} run

%pre -n python%{pyver}-%{service}
getent group novajoin >/dev/null || groupadd -r novajoin
getent passwd novajoin >/dev/null || \
useradd -r -g novajoin -d %{_sharedstatedir}/novajoin -s /sbin/nologin \
-c "OpenStack novajoin Daemons" novajoin
exit 0

%files -n python%{pyver}-%{service}
%license LICENSE
%doc README.rst
%{pyver_sitelib}/%{service}
%{pyver_sitelib}/%{service}-*.egg-info
%config(noreplace) %attr(-, root, novajoin) %{_sysconfdir}/novajoin/cloud-config-novajoin.json
%config(noreplace) %attr(-, root, novajoin) %{_sysconfdir}/novajoin/join-api-paste.ini
%config(noreplace) %attr(-, root, novajoin) %{_sysconfdir}/novajoin/join.conf
%{_libexecdir}/novajoin-ipa-setup
%{_bindir}/novajoin-ipa-setup
%{_bindir}/novajoin-install
%{_bindir}/novajoin-notify
%{_bindir}/novajoin-server
%dir %{_datarootdir}/novajoin
%{_datarootdir}/novajoin/freeipa.json
%{_mandir}/man1/novajoin-install.1.gz
%{_mandir}/man1/novajoin-notify.1.gz
%{_mandir}/man1/novajoin-server.1.gz
%{_unitdir}/novajoin-server.service
%{_unitdir}/novajoin-notify.service
%attr(0755,novajoin,novajoin) %dir %{_localstatedir}/log/novajoin
%attr(0755,novajoin,novajoin) %dir %{_sharedstatedir}/novajoin
%config(noreplace) %{_sysconfdir}/logrotate.d/novajoin
%exclude %{pyver_sitelib}/%{service}/test.*
%exclude %{pyver_sitelib}/%{service}/tests

%files -n python%{pyver}-%{service}-tests-unit
%license LICENSE
%{pyver_sitelib}/%{service}/test.*
%{pyver_sitelib}/%{service}/tests


%post -n python%{pyver}-%{service}
%systemd_post novajoin-server.service novajoin-notify.service

%preun -n python%{pyver}-%{service}
%systemd_preun novajoin-server.service novajoin-notify.service

%postun -n python%{pyver}-%{service}
%systemd_postun_with_restart novajoin-server.service novajoin-notify.service

%if 0%{?with_doc}
%files -n python%{pyver}-%{service}-doc
%doc html
%license LICENSE
%endif

%changelog
