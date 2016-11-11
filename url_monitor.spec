%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           url_monitor
Version:        3.0.3
Release:        1%{?dist}
Group:          Applications/Systems
Summary:        This is an external script for zabbix for monitoring restful endpoints for data.

License:        ASLv2
URL:            https://github.com/rackerlabs/zabbix_url_monitor
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:  python-setuptools
Requires(pre):  shadow-utils
Requires:       python
Requires:       python-daemon
Requires:       python-setuptools
Requires:       python-requests
Requires:       python-requests-oauthlib
Requires:       python-argparse
Requires:       PyYAML
Requires:       facterpy

%define service_name %{name}d

%description
A zabbix plugin to perform URL endpoint monitoring for JSON and XML REST APIs, supporting multiple http auth mechinisms

%prep
%setup -q -n %{name}-%{version}

%build

%pre

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --root $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}
%post

%preun

%postun

%files
%doc README.md
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/url_monitor.yaml
%{python_sitelib}/%{name}
%{python_sitelib}/%{name}*.egg-info
%attr(0755,-,-) %{_bindir}/%{name}

%changelog
* Thu Nov 10 2016 Jonathan Kelley <jon.kelley@rackspace.com> - 3.0.2-1
- Update spec version

* Mon Oct 31 2016 Jonathan Kelley <jon.kelley@rackspace.com> - 3.0.1-1
- Update spec version
- Add facterpy to requirements (built against facterpy-0.1-1)

* Mon Oct 11 2016 Jonathan Kelley <jon.kelley@rackspace.com> - 3.0.0-1
- Update spec version

* Mon Oct 10 2016 Jonathan Kelley <jon.kelley@rackspace.com> - 2.2.0-1
- Update spec version

* Mon Oct 10 2016 Jonathan Kelley <jon.kelley@rackspace.com> - 2.1.0-1
- Update spec version

* Mon Oct 10 2016 Jonathan Kelley <jon.kelley@rackspace.com> - 2.0.1-1
- Update spec version

* Mon Jul 18 2016 Jonathan Kelley <jon.kelley@rackspace.com> - 1.0.0-1
- Spec now mock-build compatible by removing inline py code from spec.

* Fri Apr 29 2016 Jonathan Kelley <jon.kelley@rackspace.com> - 0.8.5-1
- First spec
