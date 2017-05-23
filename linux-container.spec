#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a container
# This specialization allows us to optimize memory footprint and boot time.
#

Name:           linux-container
Version:        4.9.4
Release:        55
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside a container
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.9.4.tar.xz
Source1:        config

%define kversion %{version}-%{release}.container

BuildRequires:  bash >= 2.03
BuildRequires:  bc
BuildRequires:  binutils-dev
BuildRequires:  elfutils-dev
BuildRequires:  make >= 3.78
BuildRequires:  openssl-dev
BuildRequires:  flex
BuildRequires:  bison


# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

# Serie    00XX: mainline, CVE, bugfixes patches
Patch0001: cve-2016-8632.patch

# Serie    01XX: Clear Linux patches
#Patch0101: 0101-msleep-warning.patch
Patch0102: 0102-cpuidle-skip-synchronize_rcu-on-single-CPU-systems.patch
Patch0103: 0103-sysrq-skip-synchronize_rcu-if-there-is-no-old-op.patch
Patch0104: 0104-fbcon-enable-no-blink-by-default.patch
Patch0105: 0105-vmstats-wakeups.patch
Patch0106: 0106-pci-probe.patch
Patch0107: 0107-cgroup.patch
Patch0108: 0108-smpboot-reuse-timer-calibration.patch
Patch0109: 0109-perf.patch
Patch0110: 0110-pci-probe-identify-known-devices.patch
Patch0111: 0111-init-no-wait-for-the-known-devices.patch
Patch0112: 0112-ksm-wakeups.patch
Patch0113: 0113-init-do_mounts-recreate-dev-root.patch
Patch0114: 0114-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch

# Serie    02XX: Clear Containers patches
Patch0201: 0201-crypto-allow-testmgr-to-be-skipped.patch
Patch0202: 0202-silence-Power-down-msg.patch
Patch0203: 0203-fs-9p-fix-create-unlink-getattr-idiom.patch
Patch0204: 0204-rdrand.patch
Patch0205: 0205-reboot.patch
Patch0206: 0206-no-early-modprobe.patch
Patch0207: 0207-pci-guest-kernel-set-pci-net-class-bar-to-4.patch
Patch0208: 0208-Show-restart-information-using-info-log.patch

# Serie    XYYY: Extra features modules

%description
The Linux kernel.

%prep
%setup -q -n linux-4.9.4

#     00XX  mainline, CVE, bugfixes patches
%patch0001 -p1

#     01XX  Clear Linux KVM patches
#%patch0101 -p1
%patch0102 -p1
%patch0103 -p1
%patch0104 -p1
%patch0105 -p1
%patch0106 -p1
%patch0107 -p1
%patch0108 -p1
%patch0109 -p1
%patch0110 -p1
%patch0111 -p1
%patch0112 -p1
%patch0113 -p1
%patch0114 -p1

#     02XX  Clear Containers patches
%patch0201 -p1
%patch0202 -p1
%patch0203 -p1
%patch0204 -p1
%patch0205 -p1
%patch0206 -p1
%patch0207 -p1
%patch0208 -p1

# Serie    XYYY: Extra features modules

cp %{SOURCE1} .

%build
BuildKernel() {

    Arch=x86_64
    ExtraVer="-%{release}.container"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make -s mrproper
    cp config .config

    make -s ARCH=$Arch oldconfig > /dev/null
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch %{?sparse_mflags}
}

BuildKernel

%install

InstallKernel() {
    KernelImageRaw=$1

    Arch=x86_64
    KernelVer=%{kversion}
    KernelDir=%{buildroot}/usr/share/clear-containers

    mkdir   -p ${KernelDir}

    cp $KernelImageRaw ${KernelDir}/vmlinux-$KernelVer
    chmod 755 ${KernelDir}/vmlinux-$KernelVer
    ln -sf vmlinux-$KernelVer ${KernelDir}/vmlinux.container

    rm -f %{buildroot}/usr/lib/modules/$KernelVer/build
    rm -f %{buildroot}/usr/lib/modules/$KernelVer/source
}

InstallKernel vmlinux

rm -rf %{buildroot}/usr/lib/firmware

%files
%dir /usr/share/clear-containers
/usr/share/clear-containers/vmlinux-%{kversion}
/usr/share/clear-containers/vmlinux.container
