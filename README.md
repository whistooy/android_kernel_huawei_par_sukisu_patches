# Huawei nova 3 (PAR) kernel patches

Source patches and GitHub Actions builds for the Huawei nova 3 (`PAR`) on the
Mashopy Kirin 970 Linux 4.9.148 kernel base, with Nova 3 EMUI 9.1 /
HarmonyOS source imports. The target is AlphaDroid Android 13 with the current
PAR EMUI 9.1 vendor/firmware. Initial device checks passed for boot, WPA2 Wi-Fi, root and authorization persistence;
automatic reboot and broader hardware validation remain outstanding.

This repository is a fork of
[yukino1111/android_kernel_huawei_par_sukisu_patches](https://github.com/yukino1111/android_kernel_huawei_par_sukisu_patches).
This branch independently rebases its original EMUI 9.0 feature builder
([`4444781`](https://github.com/yukino1111/android_kernel_huawei_par_sukisu_patches/commit/4444781)) onto Mashopy `5208809c3fb8faa74ba07abff32015ff69d3b7f3`. It
keeps the original pinned KernelSU and SuSFS 2.3.0 dependencies; Antigravity
9.1 and KernelSU-Next trees are references only. KPM is disabled. See
[the source comparison and migration report](docs/UPSTREAM-REBASE.md).

## Disclaimer

This is a personal project shared as-is. Flashing a custom kernel can cause
data loss, boot failure, or a bricked device. You accept all risk and
responsibility for flashing and recovery. No warranty, porting, or
device-recovery support is provided.

## Compatibility

- Device: Huawei nova 3 (`PAR`).
- Target firmware base: the existing PAR EMUI 9.1 vendor/firmware.
- Android target: Android 13.
- Kernel: Linux 4.9.148.
- Status: initial device validation passed; automatic reboot still powers off.

Other devices and other major firmware bases are unsupported.

## Downloads

Build this fork using the local instructions below or its GitHub Actions workflow.
GitHub Actions artifacts are build candidates and are not releases until they
have been tested on the device.

## GitHub Actions

The `Build pinned feature PAR kernel` workflow lets you select:

- SELinux Enforcing or runtime-switchable SELinux;
- KernelSU, SuSFS, Re-Kernel, DroidSpaces support, NTSync, and Baseband Guard;
- Re-Kernel's separate network wake monitor;
- the network extensions available in this Linux 4.9 tree.

All upstream inputs are fetched at the exact revisions recorded in
[`SOURCE_STATE`](SOURCE_STATE). The resolved revisions used by each build are
also recorded in the artifact's `build-info.txt`.

## Important notes

- The new upstream already provides EROFS, Binder security contexts and the
  Wi-Fi EAPOL marker correction. No replacement Wi-Fi firmware is embedded.
- The old VDEC protected-SMR patch is not applied: its target function is absent
  in this upstream. Video decoding still needs device testing.
- Re-Kernel Binder and signal support works independently of its network wake
  monitor. The network wake monitor is known to cause problems on PAR; keep it
  disabled.
- Keep DroidSpaces's optional `/system/bin/droidspaces` convenience symlink
  disabled.
- Baseband Guard is configured not to block the kernel or recovery partitions.
- KPM is excluded from release builds.

## Local builds

Use the selectable-feature builder for this branch:

```bash
BUILD_BACKEND=host JOBS=4 scripts/build_par_kernel_dev_ci.sh \
  selinux-switchable /absolute/path/to/empty-build-directory
```

Docker is the default backend. `SOURCE_CACHE_DIR` may point to local Git clones
(named `kernel`, `toolchain`, and dependency names); only pinned committed files
are checked out. `PREPARE_ONLY=1` stops after source preparation.
`CONFIG_ONLY=1` on `build_par_kernel_dev.sh` validates configuration without
compiling. The earlier `ci-build.sh` / `apply.sh` SukiSU-only route is historical
and is not covered by this migration validation.

## Repository layout

| Location | Purpose |
| --- | --- |
| `SOURCE_STATE` | Exact upstream/dependency revisions and selected input hashes |
| `patches/kernel/series` | Ordered base-kernel patches for the selected Mashopy revision |
| `patches/dev/kernel/` | Feature integration and Linux 4.9 compatibility; applied conditionally by the builder |
| `patches/dev/kernelsu/series` | KernelSU compatibility, authorization guard and fscrypt credential fix |
| `patches/dev/baseband-guard/` | PAR-specific Baseband Guard policy |
| `configs/` | Enforcing and runtime-switchable configurations |
| `scripts/build_par_kernel_dev_ci.sh` | Pinned checkout, patch preparation and build orchestration |
| `scripts/build_par_kernel_dev.sh` | Feature configuration, assertions and compilation |
| `scripts/package-kernel.sh` | PAR image header, command line and partition-size checks |
| `tests/test_par_fstab.py` | Host test of the prepared kernel’s actual fstab transformation code |
| `docs/UPSTREAM-REBASE.md` | Migration decisions, source replay and device-validation limits |
| `docs/ALLOWLIST-HISTORY.md` | KernelSU keyring/SELinux history and the authorization persistence fix |

The patched full kernel tree and dependency clones are generated build inputs,
not files to copy into this patch repository. Images belong in release/build
artifacts with their manifests; firmware packages and device backups remain local.

## Installation

Back up the current kernel and keep a known-good rollback image. Flash the
downloaded image to the `kernel` partition:

```bash
fastboot flash kernel /path/to/selected-kernel.img
fastboot reboot
```

Automatic reboot from Android currently powers the test device off. Manual
power-on was used for persistence checks; do not assume unattended reboot works.

## License

Original repository material uses GPL-2.0-only. Upstream-derived patches keep
their original terms, including the separate SuSFS GPL-3.0-or-later scope; see
[`ATTRIBUTION.md`](ATTRIBUTION.md) and [`LICENSES.md`](LICENSES.md).

## Acknowledgements

- [yukino1111/android_kernel_huawei_par_sukisu_patches](https://github.com/yukino1111/android_kernel_huawei_par_sukisu_patches) — original PAR patch repository, feature integration and build workflow forming the basis of this fork.
- [Mashopy/android_kernel_huawei_kirin970](https://github.com/Mashopy/android_kernel_huawei_kirin970)
- [LineageOS/android_kernel_huawei_kirin970](https://github.com/LineageOS/android_kernel_huawei_kirin970)
- [SukiSU Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra)
- [KernelSU](https://github.com/tiann/KernelSU)
- [SuSFS](https://gitlab.com/simonpunk/susfs4ksu)
- [Re-Kernel](https://github.com/Sakion-Team/Re-Kernel)
- [DroidSpaces](https://github.com/ravindu644/Droidspaces-OSS)
- [WildKernels kernel patches](https://github.com/WildKernels/kernel_patches)
- [Baseband Guard](https://github.com/vc-teahouse/Baseband-guard)
- [KernelSU_on_Huawei](https://github.com/xixiaobei-bei/KernelSU_on_Huawei)
- [Huawei GSI and KernelSU tutorial](https://github.com/Coconutat/Huawei-GSI-And-Modify-Or-Support-KernelSU-Tutorial)
