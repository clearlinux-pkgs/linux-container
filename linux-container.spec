#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a container
# This specialization allows us to optimize memory footprint and boot time.
#

Name:           linux-container
Version:        4.2.5
Release:        42
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside a container
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.2.5.tar.xz
Source1:        config
Source2:        cmdline

%define kversion %{version}-%{release}.container

BuildRequires:  bash >= 2.03
BuildRequires:  bc
# For bfd support in perf/trace
BuildRequires:  binutils-devel
BuildRequires:  elfutils
BuildRequires:  elfutils-devel
BuildRequires:  make >= 3.78
BuildRequires:  openssl
BuildRequires:  flex
BuildRequires:  bison

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

# linux-kvm patches
Patch1:  0001-msleep.patch
patch2:  0002-Skip-synchronize_rcu-on-single-CPU-systems.patch
patch3:  0003-sysrq-Skip-synchronize_rcu-if-there-is-no-old-op.patch
patch4:  0004-enable-no-blink-by-default.patch
patch5:  0005-wakeups.patch
patch6:  0006-probe.patch
patch7:  0007-cgroup.patch
patch8:  0008-smpboot.patch
patch9:  0009-perf.patch
patch10: 0010-tweak-the-scheduler-to-favor-CPU-0.patch
patch11: 0011-probe2.patch
patch12: 0012-No-wait-for-the-known-devices.patch
patch13: 0013-Turn-mmput-into-an-async-function.patch
Patch14: 0014-ptdamage.patch

# Security
Patch21: CVE-2015-6937.patch

# plkvm patches
Patch401: 401-plkvm.patch
Patch403: 403-rdrand.patch
Patch404: 404-reboot.patch
Patch405: 405-no-early-modprobe.patch
Patch406: 406-initcalldebug.patch
Patch407: 407-pci-guest-kernel-set-pci-net-class-bar-to-3.patch
Patch408: 408-restart-info-log.patch

# kdbus
Patch701: 701-kdbus.patch

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel
Group:          kernel

%description extra
Linux kernel extra file

%prep
%setup -q -n linux-4.2.5

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1

%patch21 -p1

%patch401 -p1
%patch403 -p1
%patch404 -p1
%patch405 -p1
%patch406 -p1
%patch407 -p1
%patch408 -p1

%patch701 -p1

cp %{SOURCE1} .

%build
BuildKernel() {
    MakeTarget=$1

    Arch=x86_64
    ExtraVer="-%{release}.container"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make -s mrproper
    cp config .config

    make -s ARCH=$Arch oldconfig > /dev/null
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch $MakeTarget %{?sparse_mflags} || exit 1
}

BuildKernel all

%install

InstallKernel() {
    KernelImage=$1
    KernelImageRaw=$2

    Arch=x86_64
    KernelVer=%{kversion}
    KernelDir=%{buildroot}/usr/lib/kernel

    mkdir   -p ${KernelDir}
    install -m 644 .config    ${KernelDir}/config-$KernelVer
    install -m 644 System.map ${KernelDir}/System.map-$KernelVer
    install -m 644 %{SOURCE2} ${KernelDir}/cmdline-$KernelVer
    cp  $KernelImage ${KernelDir}/vmlinuz-$KernelVer
    chmod 755 ${KernelDir}/vmlinuz-$KernelVer
    ln -sf vmlinuz-$KernelVer ${KernelDir}/vmlinuz.container

    cp $KernelImageRaw ${KernelDir}/vmlinux-$KernelVer
    chmod 755 ${KernelDir}/vmlinux-$KernelVer
    ln -sf vmlinux-$KernelVer ${KernelDir}/vmlinux.container

    rm -f %{buildroot}/usr/lib/modules/$KernelVer/build
    rm -f %{buildroot}/usr/lib/modules/$KernelVer/source
}

InstallKernel arch/x86/boot/bzImage vmlinux

rm -rf %{buildroot}/usr/lib/firmware

%files
%dir /usr/lib/kernel
/usr/lib/kernel/config-%{kversion}
/usr/lib/kernel/vmlinuz-%{kversion}
/usr/lib/kernel/vmlinuz.container
/usr/lib/kernel/vmlinux-%{kversion}
/usr/lib/kernel/vmlinux.container

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion}
/usr/lib/kernel/cmdline-%{kversion}
