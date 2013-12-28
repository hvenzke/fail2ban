#
# spec file for package fail2ban
#
# Copyright (c) 2013 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Name:           fail2ban
Requires:       cron
Requires:       iptables
Requires:       logrotate
Requires:       lsof
Requires:       python >= 2.5
%if 0%{?suse_version} >= 1140 && 0%{?sles_version} == 0
Requires:       python-pyinotify
%endif
%if 0%{?suse_version} >= 1220
Requires:       python-gamin
%endif
BuildRequires:  python-devel
PreReq:         %fillup_prereq
Version:        0.8.8
Release:        2.8.1
Url:            http://www.fail2ban.org/
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
Summary:        Bans IP addresses that make too many authentication failures
License:        GPL-2.0+
Group:          Productivity/Networking/Security
Source0:        https://github.com/downloads/fail2ban/fail2ban/%{name}_%{version}.orig.tar.gz
Source1:        %{name}.init
Source2:        %{name}.sysconfig
# PATCH-FIX-UPSTREAM fail2ban-CVE-2013-2178.patch CVE-2013-2178 bnc#824710
Patch0:         fail2ban-CVE-2013-2178.patch

%description
Fail2ban scans log files like /var/log/messages and bans IP addresses
that makes too many password failures. It updates firewall rules to
reject the IP address, can send e-mails, or set host.deny entries.
These rules can be defined by the user. Fail2Ban can read multiple log
files such as sshd or Apache web server ones.

%prep
%setup
%patch0 -p1

%build
export CFLAGS="$RPM_OPT_FLAGS"
python setup.py build
gzip man/*.1

%install
python setup.py install \
        --root=$RPM_BUILD_ROOT \
        --prefix=%{_prefix}
install -d -m755 $RPM_BUILD_ROOT/%{_mandir}/man1
for i in fail2ban-client fail2ban-regex fail2ban-server; do
        install -m644 man/${i}.1.gz $RPM_BUILD_ROOT/%{_mandir}/man1
done
install -d -m755 $RPM_BUILD_ROOT/%{_initrddir}
install -d -m755 $RPM_BUILD_ROOT/%{_sbindir}
install -m755 %{SOURCE1} $RPM_BUILD_ROOT/%{_initrddir}/%{name}
ln -sf %{_initrddir}/%{name} ${RPM_BUILD_ROOT}%{_sbindir}/rc%{name}
install -d -m755 $RPM_BUILD_ROOT/var/adm/fillup-templates
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT/var/adm/fillup-templates/sysconfig.%{name}

%post
%{fillup_only}

%preun
%stop_on_removal %{name}

%postun
%restart_on_update %{name}
%insserv_cleanup

%files
%defattr(-, root, root)
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/action.d
%dir %{_sysconfdir}/%{name}/filter.d
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/action.d/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/filter.d/*.conf
%{_initrddir}/%{name}
%{_bindir}/%{name}*
%{_sbindir}/rc%{name}
%{_datadir}/%{name}
%dir %ghost /var/run/%{name}
/var/adm/fillup-templates/sysconfig.%{name}
%doc %{_mandir}/man1/*
%doc COPYING ChangeLog README TODO files/cacti

%changelog
* Fri Jun 14 2013 jweberhofer@weberhofer.at
- Fixes: Yaroslav Halchenko
  * [6ccd5781] filter.d/apache-{auth,nohome,noscript,overflows} - anchor
    failregex at the beginning (and where applicable at the end).
    Addresses a possible DoS.
    Closes gh#fail2ban/fail2ban#248, CVE-2013-2178, bnc#824710
* Thu Dec  6 2012 jweberhofer@weberhofer.at
  One of the important changes is escaping of the <matches> content -- so if you
  crafted some custom action which uses it -- you must upgrade, or you
  would be at a significant security risk.
- Fixes:
  Alan Jenkins
  * [8c38907] Removed 'POSSIBLE BREAK-IN ATTEMPT' from sshd filter to avoid
    banning due to misconfigured DNS. Close gh-64
  Yaroslav Halchenko
  * [83109bc] IMPORTANT: escape the content of <matches> (if used in
    custom action files) since its value could contain arbitrary
    symbols.  Thanks for discovery go to the NBS System security
    team
  * [0935566,5becaf8] Various python 2.4 and 2.5 compatibility fixes. Close gh-83
  * [b159eab] do not enable pyinotify backend if pyinotify < 0.8.3
  * [37a2e59] store IP as a base, non-unicode str to avoid spurious messages
    in the console. Close gh-91
- New features:
  David Engeset
  * [2d672d1,6288ec2] 'unbanip' command for the client + avoidance of touching
    the log file to take 'banip' or 'unbanip' in effect. Close gh-81, gh-86
- Enhancements:
  * [2d66f31] replaced uninformative "Invalid command" message with warning log
    exception why command actually failed
  * [958a1b0] improved failregex to "support" auth.backend = "htdigest"
  * [9e7a3b7] until we make it proper module -- adjusted sys.path only if
    system-wide run
  * [f52ba99] downgraded "already banned" from WARN to INFO level. Closes gh-79
  * [f105379] added hints into the log on some failure return codes (e.g. 0x7f00
    for this gh-87)
  * Various others: travis-ci integration, script to run tests
    against all available Python versions, etc
* Mon Dec  3 2012 jweberhofer@weberhofer.at
- Fixed initscript as discussed in bnc#790557
* Wed Oct  3 2012 meissner@suse.com
- use Source URL pointing to github
* Tue Oct  2 2012 jweberhofer@weberhofer.at
- Do not longer replace main config-files
- Use variables for directories in spec file
* Tue Oct  2 2012 jweberhofer@weberhofer.at
- Added dependencies to python-pyinotifyi, python-gamin and iptables
* Tue Oct  2 2012 jweberhofer@weberhofer.at
- Upgraded to version 0.8.7.1
- Yaroslav Halchenko
  * [e9762f3] Removed sneaked in comment on sys.path.insert
    Tom Hendrikx & Jeremy Olexa
  * [0eaa4c2,444e4ac] Fix Gentoo init script: $opts variable is deprecated.
    See http://forums.gentoo.org/viewtopic-t-899018.html
- Chris Reffett
  * [a018a26] Fixed addBannedIP to add enough failures to trigger a ban,
    rather than just one failure.
- Yaroslav Halchenko
  * [4c76fb3] allow trailing white-spaces in lighttpd-auth.conf
  * [25f1e8d] allow trailing whitespace in few missing it regexes for sshd.conf
  * [ed16ecc] enforce "ip" field returned as str, not unicode so that log
    message stays non-unicode. Close gh-32
  * [b257be4] added %%m-%%d-%%Y pattern + do not add %%Y for Feb 29 fix if
    already present in the pattern
  * [47e956b] replace "|" with "_" in ipmasq-ZZZzzz|fail2ban.rul to be
    friend to developers stuck with Windows (Closes gh-66)
  * [80b191c] anchor grep regexp in actioncheck to not match partial names
    of the jails (Closes: #672228) (Thanks SzÃ©pe Viktor for the report)
- New features:
- FranÃ§ois Boulogne
  * [a7cb20e..] add lighttpd-auth filter/jail
- Lee Clemens & Yaroslav Halchenko
  * [e442503] pyinotify backend (default if backend='auto' and pyinotify
    is available)
  * [d73a71f,3989d24] usedns parameter for the jails to allow disabling
    use of DNS
- Tom Hendrikx
  * [f94a121..] 'recidive' filter/jail to monitor fail2ban.conf to ban
    repeated offenders. Close gh-19
- Xavier Devlamynck
  * [7d465f9..] Add asterisk support
- Zbigniew Jedrzejewski-Szmek
  * [de502cf..] allow running fail2ban as non-root user (disabled by
    default) via xt_recent. See doc/run-rootless.txt
- Enhancements
- Lee Clemens
  * [47c03a2] files/nagios - spelling/grammar fixes
  * [b083038] updated Free Software Foundation's address
  * [9092a63] changed TLDs to invalid domains, in accordance with RFC 2606
  * [642d9af,3282f86] reformated printing of jail's name to be consistent
    with init's info messages
  * [3282f86] uniform use of capitalized Jail in the messages
- Leonardo Chiquitto
  * [4502adf] Fix comments in dshield.conf and mynetwatchman.conf
    to reflect code
  * [a7d47e8] Update Free Software Foundation's address
- Petr Voralek
  * [4007751] catch failed ssh logins due to being listed in DenyUsers.
    Close gh-47 (Closes: #669063)
- Yaroslav Halchenko
  * [MANY]    extended and robustified unittests: test different backends
  * [d9248a6] refactored Filter's to avoid duplicate functionality
  * [7821174] direct users to issues on github
  * [d2ffee0..] re-factored fail2ban-regex -- more condensed output by
    default with -v to control verbosity
  * [b4099da] adjusted header for config/*.conf to mention .local and way
    to comment (Thanks Stefano Forli for the note)
  * [6ad55f6] added failregex for wu-ftpd to match against syslog instead
    of DoS-prone auth.log's rhost (Closes: #514239)
  * [2082fee] match possibly present "pam_unix(sshd:auth):" portion for
    sshd filter (Closes: #648020)
- Yehuda Katz & Yaroslav Halchenko
  * [322f53e,bd40cc7] ./DEVELOP -- documentation for developers
* Tue Jul 31 2012 asemen@suse.de
- Adding to fail2ban.init remove of pid and sock files on stop
  in case not removed before (prevents start fail)
* Sun Jun  3 2012 jweberhofer@weberhofer.at
- Update to version 0.8.6. containing various fixes and enhancements
* Fri Nov 18 2011 lchiquitto@suse.com
- Update to version 0.8.5: many bug fixes, enhancements and, as
  a bonus, drop two patches that are now upstream
- Update FSF address to silent rpmlint warnings
- Drop stale socket files on startup (bnc#537239, bnc#730044)
* Sun Sep 18 2011 jengelh@medozas.de
- Apply packaging guidelines (remove redundant/obsolete
  tags/sections from specfile, etc.)
* Thu Sep  1 2011 coolo@suse.com
- Use /var/run/fail2ban instead of /tmp for temp files in
  actions: see bugs.debian.org/544232, bnc#690853,
  CVE-2009-5023
* Thu Jan  6 2011 lchiquitto@suse.com
- Use $FAIL2BAN_OPTIONS when starting (bnc#662495)
- Clean up sysconfig file
* Tue Jul 27 2010 cristian.rodriguez@opensuse.org
- Use O_CLOEXEC on fds (patch from Fedora)
* Wed May  5 2010 lchiquitto@suse.com
- Create /var/run/fail2ban during startup to support systems that
  mount /var/run as tmpfs
- Build package as noarch
- Spec file cleanup: fix a couple of rpmlint warnings
- Init script: look for fail2ban-server when checking if the
  daemon is running
* Thu Nov 26 2009 lchiquitto@suse.com
- Update to version 0.8.4. Important changes:
  * New "Ban IP" command
  * New filters: lighttpd-fastcgi php-url-fopen cyrus-imap sieve
  * Fixed the 'unexpected communication error' problem
  * Remove socket file on startup if fail2ban crashed (bnc#537239)
* Wed Feb  4 2009 kssingvo@suse.de
- Initial version: 0.8.3
