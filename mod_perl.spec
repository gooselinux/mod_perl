%define contentdir /var/www

Name:           mod_perl
Version:        2.0.4
Release:        10%{?dist}
Summary:        An embedded Perl interpreter for the Apache HTTP Server

Group:          System Environment/Daemons
License:        ASL 2.0
URL:            http://perl.apache.org/
Source0:        http://perl.apache.org/dist/mod_perl-%{version}.tar.gz
Source1:        perl.conf
Source2:        filter-requires.sh
Source3:        filter-provides.sh
Patch0:         mod_perl-2.0.4-multilib.patch
Patch1:         mod_perl-2.0.4-inline.patch
Patch2:         mod_perl-2.0.4-CVE-2009-0796.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  perl-devel, perl(ExtUtils::Embed)
BuildRequires:  httpd-devel >= 2.2.0, httpd, gdbm-devel
BuildRequires:  apr-devel >= 1.2.0, apr-util-devel
Requires:  perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:       httpd-mmn = %(cat %{_includedir}/httpd/.mmn || echo missing)

%define __perl_requires %{SOURCE2}
%define __perl_provides %{SOURCE3}

%description
Mod_perl incorporates a Perl interpreter into the Apache web server,
so that the Apache web server can directly execute Perl code.
Mod_perl links the Perl runtime library into the Apache web server and
provides an object-oriented Perl interface for Apache's C language
API.  The end result is a quicker CGI script turnaround process, since
no external Perl interpreter has to be started.

Install mod_perl if you're installing the Apache web server and you'd
like for it to directly incorporate a Perl interpreter.


%package devel
Summary:        Files needed for building XS modules that use mod_perl
Group:          Development/Libraries
Requires:       mod_perl = %{version}-%{release}, httpd-devel

%description devel 
The mod_perl-devel package contains the files needed for building XS
modules that use mod_perl.


%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1 -b .inline
%patch2 -p1

%build
CFLAGS="$RPM_OPT_FLAGS -fpic" %{__perl} Makefile.PL </dev/null \
	PREFIX=$RPM_BUILD_ROOT/usr \
	INSTALLDIRS=vendor \
	MP_APXS=%{_sbindir}/apxs \
	MP_APR_CONFIG=%{_bindir}/apr-1-config
make -C src/modules/perl %{?_smp_mflags} OPTIMIZE="$RPM_OPT_FLAGS -fpic"
make

%install
rm -rf $RPM_BUILD_ROOT
install -d -m 755 $RPM_BUILD_ROOT%{_libdir}/httpd/modules
make install \
    MODPERL_AP_LIBEXECDIR=$RPM_BUILD_ROOT%{_libdir}/httpd/modules \
    MODPERL_AP_INCLUDEDIR=$RPM_BUILD_ROOT%{_includedir}/httpd

# Remove the temporary files.
find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name perllocal.pod -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name '*.bs' -a -size 0 -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type d -depth -exec rmdir {} 2>/dev/null ';'

# Fix permissions to avoid strip failures on non-root builds.
chmod -R u+w $RPM_BUILD_ROOT/*

# Install the config file
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d
install -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/conf.d/

# Move set of modules to -devel
devmods="ModPerl::Code ModPerl::BuildMM ModPerl::CScan \
          ModPerl::TestRun ModPerl::Config ModPerl::WrapXS \
          ModPerl::BuildOptions ModPerl::Manifest \
          ModPerl::MapUtil ModPerl::StructureMap \
          ModPerl::TypeMap ModPerl::FunctionMap \
          ModPerl::ParseSource ModPerl::MM \
          Apache2::Build Apache2::ParseSource Apache2::BuildConfig \
          Apache Bundle::ApacheTest"
for m in $devmods; do
   test -f $RPM_BUILD_ROOT%{_mandir}/man3/${m}.3pm &&
     echo "%{_mandir}/man3/${m}.3pm*"
   fn=${m//::/\/}
   test -f $RPM_BUILD_ROOT%{perl_vendorarch}/${fn}.pm &&
        echo %{perl_vendorarch}/${fn}.pm
   test -d $RPM_BUILD_ROOT%{perl_vendorarch}/${fn} && 
        echo %{perl_vendorarch}/${fn}
   test -d $RPM_BUILD_ROOT%{perl_vendorarch}/auto/${fn} && 
        echo %{perl_vendorarch}/auto/${fn}
done | tee devel.files | sed 's/^/%%exclude /' > exclude.files

# Completely remove Apache::Test - can be packaged separately
#rm -rf $RPM_BUILD_ROOT%{_mandir}/man3/Apache::Test*
#rm -rf $RPM_BUILD_ROOT%{perl_vendorarch}/Apache


%clean
rm -rf $RPM_BUILD_ROOT

%files -f exclude.files
%defattr(-,root,root,-)
%doc Changes LICENSE README* STATUS SVN-MOVE docs/
%config(noreplace) %{_sysconfdir}/httpd/conf.d/*.conf
%{_bindir}/*
%{_libdir}/httpd/modules/mod_perl.so
%{perl_vendorarch}/auto/*
%{perl_vendorarch}/Apache2/
%{perl_vendorarch}/Bundle/
%{perl_vendorarch}/APR/
%{perl_vendorarch}/ModPerl/
%{perl_vendorarch}/*.pm
%{_mandir}/man3/*.3*

%files devel -f devel.files
%defattr(-,root,root,-)
%{_includedir}/httpd/*

%changelog
* Tue Dec  8 2009 Joe Orton <jorton@redhat.com> - 2.0.4-10
- add security fix for CVE-2009-0796 (#544455)

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.4-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Oct 17 2008 Joe Orton <jorton@redhat.com> 2.0.4-7
- fix inline abuse (#459351)

* Wed Aug  6 2008 Joe Orton <jorton@redhat.com> 2.0.4-5
- rebuild to fix patch fuzz (#427758)

* Mon Jul 14 2008 Joe Orton <jorton@redhat.com> 2.0.4-4
- rebuild for new BDB

* Tue May 13 2008 Joe Orton <jorton@redhat.com> 2.0.4-3
- trim changelog; rebuild

* Fri Apr 18 2008 Joe Orton <jorton@redhat.com> 2.0.4-2
- update to 2.0.4

* Wed Feb 27 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.0.3-21
- Rebuild for perl 5.10 (again)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.0.3-20
- Autorebuild for GCC 4.3

* Wed Jan 30 2008 Joe Orton <jorton@redhat.com> 2.0.3-19
- further fixes for perl 5.10 (upstream r480903, r615751)

* Wed Jan 30 2008 Joe Orton <jorton@redhat.com> 2.0.3-18
- fix build with perl 5.10 (upstream r480890)

* Tue Jan 29 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.3-17
- fix perl BR

* Mon Jan 28 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.3-16
- rebuild for new perl

* Thu Dec  6 2007 Joe Orton <jorton@redhat.com> 2.0.3-15
- rebuild for new OpenLDAP

* Wed Sep  5 2007 Joe Orton <jorton@redhat.com> 2.0.3-14
- filter perl(HTTP::Request::Common) Provide from -devel (#247250)

* Sun Sep  2 2007 Joe Orton <jorton@redhat.com> 2.0.3-13
- rebuild for fixed 32-bit APR

* Thu Aug 23 2007 Joe Orton <jorton@redhat.com> 2.0.3-12
- rebuild for expat soname bump

* Tue Aug 21 2007 Joe Orton <jorton@redhat.com> 2.0.3-11
- rebuild for libdb soname bump

* Mon Aug 20 2007 Joe Orton <jorton@redhat.com> 2.0.3-10
- fix License

* Fri Apr 20 2007 Joe Orton <jorton@redhat.com> 2.0.3-8
- filter provide of perl(warnings) (#228429)

* Wed Feb 28 2007 Joe Orton <jorton@redhat.com> 2.0.3-7
- also restore Apache::Test to devel
- add BR for perl-devel

* Tue Feb 27 2007 Joe Orton <jorton@redhat.com> 2.0.3-6
- filter more Apache::Test requirements

* Mon Feb 26 2007 Joe Orton <jorton@redhat.com> 2.0.3-5
- repackage set of trimmed modules, but only in -devel

* Wed Jan 31 2007 Joe Orton <jorton@redhat.com> 2.0.3-4
- restore ModPerl::MM

* Tue Dec  5 2006 Joe Orton <jorton@redhat.com> 2.0.3-3
- trim modules even more aggressively (#197841)

* Mon Dec  4 2006 Joe Orton <jorton@redhat.com> 2.0.3-2
- update to 2.0.3
- remove droplet in buildroot from multilib patch
- drop build-related ModPerl:: modules and Apache::Test (#197841)
- spec file cleanups

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - sh: line 0: fg: no job control
- rebuild

* Thu Jun 15 2006 Joe Orton <jorton@redhat.com> 2.0.2-6
- fix multilib conflicts in -devel (#192733)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.0.2-5.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.0.2-3.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Dec  2 2005 Joe Orton <jorton@redhat.com> 2.0.2-3
- rebuild for httpd 2.2

* Wed Oct 26 2005 Joe Orton <jorton@redhat.com> 2.0.2-2
- update to 2.0.2

* Thu Oct 20 2005 Joe Orton <jorton@redhat.com> 2.0.1-2
- rebuild

* Fri Jun 17 2005 Warren Togami <wtogami@redhat.com> 2.0.1-1
- 2.0.1

* Fri May 20 2005 Warren Togami <wtogami@redhat.com> 2.0.0-3
- dep changes (#114651 jpo and ville)

* Fri May 20 2005 Joe Orton <jorton@redhat.com> 2.0.0-1
- update to 2.0.0 final

* Mon Apr 18 2005 Ville Skyttä <ville.skytta at iki.fi> - 2.0.0-0.rc5.3
- Fix sample configuration.
- Explicitly disable the test suite. (#112563)

* Mon Apr 18 2005 Joe Orton <jorton@redhat.com> 2.0.0-0.rc5.2
- fix filter-requires for new Apache2:: modules

* Sat Apr 16 2005 Warren Togami <wtogami@redhat.com> - 2.0.0-0.rc5.1
- 2.0.0-RC5

* Sun Apr 03 2005 Jose Pedro Oliveira <jpo@di.uminho.pt> - 2.0.0-0.rc4.1
- Update to 2.0.0-RC4.
- Specfile cleanup. (#153236)
