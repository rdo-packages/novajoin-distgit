%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global service novajoin

Name:           python-%{service}
Version:        1.0.10
Release:        1%{?dist}
Summary:        Nova integration to enroll IPA clients

License:        ASL 2.0
URL:            http://github.com/rcritten/novajoin.git
Source0:        https://github.com/rcritten/%{service}/archive/%{version}.tar.gz#/%{service}-%{version}.tar.gz
Source1:        novajoin-notify.service
Source2:        novajoin-server.service
Source3:        novajoin.logrotate

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-sphinx_rtd_theme
BuildRequires:  git
BuildRequires:  systemd
BuildRequires:  systemd-units

%description
A nova vendordata plugin for the OpenStack nova metadata
service to manage host instantiation in an IPA server.

# this is the package that creates the nova user
Requires:       openstack-nova-common
Requires:       openstack-utils
Requires:       ipa-admintools
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%package -n python-%{service}-tests-unit
Summary:        Unit tests for novajoin
Requires:       python-%{service} = %{version}-%{release}

%description -n python-%{service}-tests-unit
Unit test files for the novajoin service.

%prep
%autosetup -n %{service}-%{version}

rm -f *requirements.txt

%build
# Needed for pbr to find version when building docs
git init .

%py2_build

# generate html docs
sphinx-build doc/source html
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
%py2_install

# Setup directories
install -d -m 755 %{buildroot}%{_mandir}/man1
install -d -m 755 %{buildroot}%{_datadir}/%{service}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{service}
install -d -m 755 %{buildroot}%{_localstatedir}/log/novajoin

# Install systemd service files
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/novajoin-notify.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/novajoin-server.service

# install log rotation configuration
install -p -D -m 644 -p %{SOURCE3} \
  %{buildroot}%{_sysconfdir}/logrotate.d/novajoin

%files -n python-%{service}
%license LICENSE
%doc README.md
%{python2_sitelib}/%{service}
%{python2_sitelib}/%{service}-*.egg-info
%{_sysconfdir}/nova/join-api-paste.ini
%{_libexecdir}/novajoin-ipa-setup
%{_sbindir}/novajoin-install
%{_sbindir}/novajoin-notify
%{_sbindir}/novajoin-server
%{_usr}/share/novajoin/cloud-config.json
%{_usr}/share/novajoin/freeipa.json
%{_usr}/share/novajoin/join.conf.template
%{_mandir}/man1/novajoin-install.1.gz
%{_mandir}/man1/novajoin-notify.1.gz
%{_mandir}/man1/novajoin-server.1.gz
%{_unitdir}/*.service
%attr(0700,nova,nova) %dir %{_localstatedir}/log/novajoin
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

%changelog
* Tue Nov 29 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.10-1
- Update to 1.0.10

* Tue Nov 29 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.9-1
- Update to 1.0.9
- Move /etc/join/api-paste.ini to /etc/nova/join-api-paste.ini

* Thu Nov 17 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.8-1
- Update to 1.0.8

* Wed Nov  9 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.7-1
- Update to 1.0.7

* Fri Oct  7 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.6-2
- Drop /var/run/nova

* Thu Oct  6 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.6-1
- Update to upstream 1.0.6

* Tue Oct  4 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.5-1
- Update to upstream 1.0.5

* Thu Sep 22 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.4-1
- Update to upstream 1.0.4 which fixes syntax error in cache

* Tue Sep 20 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.3-9
- Add missing fi to systemd_preun macro

* Tue Sep 20 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.3-8
- Move kinit code around in installer

* Tue Sep 20 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.3-7
- Fixed a bunch of pylint issues
- Remove some cut-n-paste problems with the systemd reconfig

* Mon Sep 19 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.3-6
- Fix a few issues with new installer, update man page

* Mon Sep 19 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.3-5
- Break out the IPA installer into a separate script

* Mon Sep 19 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.3-4
- Don't configure keystone_authtoken

* Thu Sep 15 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.3-3
- Add systemd macros for requires, post, pre, etc.

* Thu Sep 15 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.3-2
- Change configuration layout of join.conf

* Wed Sep 14 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.3-1
- Update to upstream 1.0.3

* Tue Sep 13 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.2-5
- Add log rotate script

* Wed Sep  7 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.2-4
- Change project_name from services to service

* Wed Sep  7 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.2-3
- New upstream tarball: Don't overwrite join.conf, fix cache delete

* Tue Sep  6 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.2-2
- Fix typo in Requires for openstack-utils

* Tue Sep  6 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.2-1
- Update to upstream 1.0.2
- Ensure that /var/run/nova exists, don't own it

* Tue Aug 16 2016 Rob Crittenden <rcritten@redhat.com> - 1.0.1-1
- Initial version
