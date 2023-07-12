%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

%global with_doc 1

%global service novajoin

Name:           python-%{service}
Version:        XXX
Release:        XXX
Summary:        Nova integration to enroll IPA clients

License:        Apache-2.0
URL:            https://launchpad.net/novajoin
Source0:        https://tarballs.openstack.org/%{service}/%{service}-%{version}.tar.gz
Source1:        novajoin.logrotate
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{service}/%{service}-%{version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
BuildRequires:  openstack-macros
%endif

%description
A nova vendordata plugin for the OpenStack nova metadata
service to manage host instantiation in an IPA server.

%package -n     python3-%{service}
Summary:        Nova integration to enroll IPA clients

Requires:       ipa-admintools

%{?systemd_ordering}

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  git-core
BuildRequires:  systemd
BuildRequires:  openstack-macros

%description -n python3-%{service}
A nova vendordata plugin for the OpenStack nova metadata
service to manage host instantiation in an IPA server.

%package -n python3-%{service}-tests-unit
Summary:        Unit tests for novajoin
Requires:       python3-%{service} = %{version}-%{release}

Requires:       python3-fixtures
Requires:       python3-mock
Requires:       python3-subunit
Requires:       python3-testtools
Requires:       python3-testrepository
Requires:       python3-testresources
Requires:       python3-testscenarios
Requires:       python3-os-testr
Requires:       python3-anyjson


%description -n python3-%{service}-tests-unit
Unit test files for the novajoin service.

%if 0%{?with_doc}
%package -n python3-%{service}-doc
Summary:        %{name} documentation

%description -n python3-%{service}-doc
%{common_desc}

It contains the documentation for Novajoin.
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{service}-%{upstream_version} -S git


sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build

%pyproject_wheel

# Generate config file
PYTHONPATH=. oslo-config-generator --config-file=files/novajoin-config-generator.conf

%if 0%{?with_doc}
# generate html docs
%tox -e docs
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}
%endif

%install
%pyproject_install

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
%tox -e %{default_toxenv}

%pre -n python3-%{service}
getent group novajoin >/dev/null || groupadd -r novajoin
getent passwd novajoin >/dev/null || \
useradd -r -g novajoin -d %{_sharedstatedir}/novajoin -s /sbin/nologin \
-c "OpenStack novajoin Daemons" novajoin
exit 0

%files -n python3-%{service}
%license LICENSE
%doc README.rst
%{python3_sitelib}/%{service}
%{python3_sitelib}/%{service}-*.dist-info
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
%exclude %{python3_sitelib}/%{service}/test.*
%exclude %{python3_sitelib}/%{service}/tests

%files -n python3-%{service}-tests-unit
%license LICENSE
%{python3_sitelib}/%{service}/test.*
%{python3_sitelib}/%{service}/tests


%post -n python3-%{service}
%systemd_post novajoin-server.service novajoin-notify.service

%preun -n python3-%{service}
%systemd_preun novajoin-server.service novajoin-notify.service

%postun -n python3-%{service}
%systemd_postun_with_restart novajoin-server.service novajoin-notify.service

%if 0%{?with_doc}
%files -n python3-%{service}-doc
%doc doc/build/html
%license LICENSE
%endif

%changelog
