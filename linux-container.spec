#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a container
# This specialization allows us to optimize memory footprint and boot time.
#

Name:           linux-container
Version:        4.14.22
Release:        85
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside a container
Url:            http://www.kernel.org/
Group:          kernel
Source0:        http://www.kernel.org/pub/linux/kernel/v4.x/linux-4.14.22.tar.xz
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

# Serie    01XX: Clear Linux patches
Patch0102: 0102-cpuidle-skip-synchronize_rcu-on-single-CPU-systems.patch
Patch0103: 0103-sysrq-skip-synchronize_rcu-if-there-is-no-old-op.patch
Patch0104: 0104-fbcon-enable-no-blink-by-default.patch
Patch0105: 0105-vmstats-wakeups.patch
Patch0107: 0107-cgroup.patch
Patch0108: 0108-smpboot-reuse-timer-calibration.patch
Patch0109: 0109-perf.patch
Patch0110: 0110-pci-probe-identify-known-devices.patch
Patch0111: 0111-init-no-wait-for-the-known-devices.patch
Patch0112: 0112-ksm-wakeups.patch
Patch0113: 0113-init-do_mounts-recreate-dev-root.patch
Patch0114: 0114-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch

# Serie    02XX: Clear Containers patches
Patch0209: 0209-HACK-9P-always-use-cached-inode-to-fill-in-v9fs_vfs_.patch

# Serie    XYYY: Extra features modules

%description
The Linux kernel.

%prep
%setup -q -n linux-4.14.22

#     01XX  Clear Linux KVM patches
%patch0102 -p1
%patch0103 -p1
%patch0104 -p1
%patch0105 -p1
%patch0107 -p1
%patch0108 -p1
%patch0109 -p1
%patch0110 -p1
%patch0111 -p1
%patch0112 -p1
%patch0113 -p1
%patch0114 -p1

#     02XX  Clear Containers patches
%patch0209 -p1

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
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch %{?sparse_mflags} || exit 1
}

BuildKernel

%install

InstallKernel() {
    KernelImage=$1
    KernelImageRaw=$2

    Arch=x86_64
    KernelVer=%{kversion}
    KernelDir=%{buildroot}/usr/share/clear-containers

    mkdir   -p ${KernelDir}

    cp $KernelImage ${KernelDir}/vmlinuz-$KernelVer
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
%dir /usr/share/clear-containers
/usr/share/clear-containers/vmlinux-%{kversion}
/usr/share/clear-containers/vmlinux.container
/usr/share/clear-containers/vmlinuz-%{kversion}
/usr/share/clear-containers/vmlinuz.container
