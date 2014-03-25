%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%{!?__initrddir: %define __initrddir /etc/rc.d/init.d}


Name:           plight
Version:        0.0.2
Release:        3%{?dist}
Group:          Applications/Systems
Summary:        Load balancer agnostic node state control service

License:        ASLv2
URL:            https://github.com/rackerlabs/plight
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:  python-setuptools
Requires(pre):  shadow-utils
Requires:       python
Requires:       python-daemon
Requires:       python-setuptools

%define service_name %{name}d

%if 0%{?rhel} == 5 || 0%{?rhel} == 6
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
%endif

%description
Plight is a lightweight daemon that can be used for load balancer
health checks to determine if a node should be used or not.

%prep
%setup -q -n %{name}-%{version}


%build

%pre
/usr/bin/getent group plight >/dev/null || /usr/sbin/groupadd -r plight
/usr/bin/getent passwd plight >/dev/null || \
    /usr/sbin/useradd -r -g plight -d /var/run/plight -s /sbin/nologin \
    -c "System account for plight daemon" plight
exit 0

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --root $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/run/%{name}
%if 0%{?rhel} == 5 || 0%{?rhel} == 6
    mv %{buildroot}%{__initrddir}/%{service_name}.init %{buildroot}%{__initrddir}/%{service_name}
    #TODO: Delete unit file when we have one
%else
    #TODO: Rename unit file
    rm -f %{buildroot}%{__initrddir}/%{service_name}.init
%endif

%if 0%{?rhel} == 5 || 0%{?rhel} == 6
# Manage the init scripts if el5/6
%post
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add %{service_name}

%preun
if [ $1 -eq 0 ] ; then
    /sbin/service %{service_name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{service_name}
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service %{service_name} condrestart >/dev/null 2>&1 || :
fi
%endif

%files
%doc README.md
%{python_sitelib}/%{name}
%{python_sitelib}/%{name}*.egg-info
%config(noreplace) %attr(0644,plight,plight) %{_sysconfdir}/%{name}.conf
%attr(0755,-,-) %{_bindir}/%{name}
%dir %attr(0755,plight,plight) %{_localstatedir}/log/%{name}/
%dir %attr(0755,plight,plight) %{_localstatedir}/run/%{name}/
%if 0%{?rhel} == 5 || 0%{?rhel} == 6
  %attr(0755,-,-) %{_initrddir}/%{service_name}
%endif

%changelog
* Tue Mar 25 2014 Greg Swift <greg.swift@rackspce.com> - 0.0.2-3
- bump of release for copr build system for el5

* Tue Feb 05 2014 Alex Schultz <alex.schultz@rackspce.com> - 0.0.2-2
- python-setuptools is required to run the plight command

* Wed Jan 29 2014 Alex Schultz <alex.schultz@rackspce.com> - 0.0.2-1
- CentOS/RHEL 5 support
- Removed cherrypy, replaced with python-daemon

* Wed Jan 22 2014 Greg Swift <gregswift@gmail.com> - 0.0.1-1
- Initial spec
