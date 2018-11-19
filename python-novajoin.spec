%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1

%global service novajoin

Name:           python-%{service}
Version:        1.0.21
Release:        1%{?dist}
Summary:        Nova integration to enroll IPA clients

License:        ASL 2.0
URL:            https://launchpad.net/novajoin
Source0:        https://tarballs.openstack.org/%{service}/%{service}-%{version}.tar.gz
Source1:        novajoin.logrotate

BuildArch:      noarch

Requires:       python-webob
Requires:       python-paste
Requires:       python-routes
Requires:       python2-six
Requires:       python2-keystoneclient >= 1:3.8.0
Requires:       python2-keystoneauth1 >= 3.3.0
Requires:       python2-oslo-concurrency >= 3.25.0
Requires:       python2-oslo-messaging >= 5.29.0
Requires:       python2-oslo-policy >= 1.30.0
Requires:       python2-oslo-serialization >= 2.18.0
Requires:       python2-oslo-service >= 1.24.0
Requires:       python2-oslo-utils >= 3.33.0
Requires:       python2-neutronclient >= 6.3.0
Requires:       python2-novaclient >= 1:9.1.0
Requires:       python2-cinderclient >= 3.3.0
Requires:       python2-glanceclient >= 1:2.8.0
Requires:       python2-keystonemiddleware >= 4.17.0
Requires:       python-cachetools >= 2.0.0

Requires:       ipa-admintools
%{?systemd_requires}

BuildRequires:  python-webob
BuildRequires:  python-paste
BuildRequires:  python2-routes
BuildRequires:  python2-six
BuildRequires:  python2-keystoneclient
BuildRequires:  python2-keystoneauth1
BuildRequires:  python2-oslo-concurrency
BuildRequires:  python2-oslo-messaging
BuildRequires:  python2-oslo-policy
BuildRequires:  python2-oslo-serialization
BuildRequires:  python2-oslo-service
BuildRequires:  python2-oslo-utils
BuildRequires:  python2-neutronclient
BuildRequires:  python2-novaclient
BuildRequires:  python2-cinderclient
BuildRequires:  python2-glanceclient
BuildRequires:  python2-devel
BuildRequires:  python2-pbr
BuildRequires:  python2-setuptools
BuildRequires:  git
BuildRequires:  systemd
BuildRequires:  python2-hacking
BuildRequires:  python-anyjson
BuildRequires:  python2-fixtures
BuildRequires:  python2-mock
BuildRequires:  python2-subunit
BuildRequires:  python2-testtools
BuildRequires:  python2-testrepository
BuildRequires:  python2-testresources
BuildRequires:  python2-testscenarios
BuildRequires:  python2-stestr
BuildRequires:  openstack-macros

%description
A nova vendordata plugin for the OpenStack nova metadata
service to manage host instantiation in an IPA server.

%package -n python-%{service}-tests-unit
Summary:        Unit tests for novajoin
Requires:       python-%{service} = %{version}-%{release}

Requires:       python-anyjson
Requires:       python2-fixtures
Requires:       python2-mock
Requires:       python2-subunit
Requires:       python2-testtools
Requires:       python2-testrepository
Requires:       python2-testresources
Requires:       python2-testscenarios
Requires:       python2-os-testr

%description -n python-%{service}-tests-unit
Unit test files for the novajoin service.

%if 0%{?with_doc}
%package -n %{name}-doc
Summary:        %{name} documentation

BuildRequires:  python2-oslo-sphinx
BuildRequires:  python2-sphinx
BuildRequires:  python-sphinx_rtd_theme

%description -n %{name}-doc
%{common_desc}

It contains the documentation for Novajoin.
%endif

%prep
%autosetup -n %{service}-%{upstream_version} -S git

%py_req_cleanup

%build

%py2_build

# Generate config file
PYTHONPATH=. oslo-config-generator --config-file=files/novajoin-config-generator.conf

%if 0%{?with_doc}
# generate html docs
sphinx-build doc/source html
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}
%endif

%install
%py2_install

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
stestr run

%pre
getent group novajoin >/dev/null || groupadd -r novajoin
getent passwd novajoin >/dev/null || \
useradd -r -g novajoin -d %{_sharedstatedir}/novajoin -s /sbin/nologin \
-c "OpenStack novajoin Daemons" novajoin
exit 0

%files -n python-%{service}
%license LICENSE
%doc README.rst
%{python2_sitelib}/%{service}
%{python2_sitelib}/%{service}-*.egg-info
%config(noreplace) %attr(-, root, novajoin) %{_sysconfdir}/novajoin/cloud-config-novajoin.json
%config(noreplace) %attr(-, root, novajoin) %{_sysconfdir}/novajoin/join-api-paste.ini
%config(noreplace) %attr(-, root, novajoin) %{_sysconfdir}/novajoin/join.conf
%{_libexecdir}/novajoin-ipa-setup
%{_sbindir}/novajoin-install
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
%config(noreplace) %{_sysconfdir}/logrotate.d/novajoin
%exclude %{python2_sitelib}/%{service}/test.*
%exclude %{python2_sitelib}/%{service}/tests

%files -n python-%{service}-tests-unit
%license LICENSE
%{python2_sitelib}/%{service}/test.*
%{python2_sitelib}/%{service}/tests


%post
%systemd_post novajoin-server.service novajoin-notify.service

%preun
%systemd_preun novajoin-server.service novajoin-notify.service

%postun
%systemd_postun_with_restart novajoin-server.service novajoin-notify.service

%if 0%{?with_doc}
%files -n %{name}-doc
%doc html
%license LICENSE
%endif

%changelog
* Mon Nov 19 2018 RDO <dev@lists.rdoproject.org> 1.0.21-1
- Update to 1.0.21

* Fri Feb 23 2018 RDO <dev@lists.rdoproject.org> 1.0.18-1
- Update to 1.0.18

