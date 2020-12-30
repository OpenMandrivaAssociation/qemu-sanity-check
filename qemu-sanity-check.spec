# _hardened_build breaks building the static 'init' binary.
# https://bugzilla.redhat.com/1204162
%undefine _hardened_build

%global debug_package %{nil}

Name:            qemu-sanity-check
Version:	1.1.6
Release:	1
Summary:         Simple qemu and Linux kernel sanity checker
Group:		Emulators
License:         GPLv2+

URL:             http://people.redhat.com/~rjones/qemu-sanity-check
Source0:         http://people.redhat.com/~rjones/qemu-sanity-check/files/%{name}-%{version}.tar.gz

# Non-upstream patch to disable test which fails on broken kernels
# which don't respond to panic=1 option properly.
Patch4:          0004-Disable-bad-userspace-test-Fedora-only.patch

Patch100: qemu-sanity-check-mga.patch

# Because the above patch touches configure.ac/Makefile.am:
BuildRequires:   autoconf, automake

# For building the initramfs.
BuildRequires:   cpio
BuildRequires:   glibc-static-devel

# BuildRequire these in order to let 'make check' run.  These are
# not required unless you want to run the tests.  Note don't run the
# tests on ARM since qemu isn't likely to work.
%ifarch %{ix86} x86_64
BuildRequires:   qemu-system-x86
%endif

BuildRequires:   kernel

%ifarch %{ix86} %{x86_64}
Requires:        qemu-system-x86
%endif
%ifarch armv7hl
Requires:        qemu-system-arm
%endif

Requires:        kernel-release

# Require the -nodeps subpackage.
Requires:        %{name}-nodeps = %{version}-%{release}


%description
Qemu-sanity-check is a short shell script that test-boots a Linux
kernel under qemu, making sure it boots up to userspace.  The idea is
to test the Linux kernel and/or qemu to make sure they are working.

Most users should install the %{name} package.

If you are testing qemu or the kernel in those packages and you want
to avoid a circular dependency on qemu or kernel, you should use
'BuildRequires: %{name}-nodeps' instead.


%package nodeps
Summary:         Simple qemu and Linux kernel sanity checker (no dependencies)
License:         GPLv2+


%description nodeps
This is the no-depedencies version of %{name}.  It is exactly the same
as %{name} except that this package does not depend on qemu or kernel.


%prep
%setup -q

%patch4 -p1

%patch100 -p0

# Rerun autotools because the patches touch configure.ac and Makefile.am.
autoreconf -i


%build
# NB: canonical_arch is a variable in the final script, so it
# has to be escaped here.
%configure --with-qemu-list="qemu-system-\$canonical_arch" || {
  cat config.log
  exit 1
}
%make_build


%check
# Temporarily disable x86 because kernel is broken there
# (https://bugzilla.redhat.com/show_bug.cgi?id=1302071)
%ifnarch %{ix86}
%ifarch %{ix86} %{x86_64}
make check || {
  cat test-suite.log
  exit 1
}
%endif
%endif

%install
make DESTDIR=$RPM_BUILD_ROOT install

%files
%doc COPYING


%files nodeps
%doc COPYING README
%{_bindir}/qemu-sanity-check
%{_libdir}/qemu-sanity-check
%{_mandir}/man1/qemu-sanity-check.1*
