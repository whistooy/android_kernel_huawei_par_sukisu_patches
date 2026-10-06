# Source attribution

This repository is a port and patch archive. Importing or rebasing upstream
code does not transfer authorship to the repository maintainer.

This fork is based on
[yukino1111/android_kernel_huawei_par_sukisu_patches](https://github.com/yukino1111/android_kernel_huawei_par_sukisu_patches),
using its complete EMUI 9.0 selectable-feature builder at commit
[`4444781`](https://github.com/yukino1111/android_kernel_huawei_par_sukisu_patches/commit/4444781) as the migration baseline.
The original PAR integration and build work remain attributed to yukino1111;
this fork adds the independent EMUI 9.1 migration and follow-up fixes described below.

## Required upstream work

| Area | Upstream author or project | Use in this repository |
| --- | --- | --- |
| Linux 4.9.148 Kirin 970 base | Huawei, Mashopy and Linux contributors | Nova 3 imports at the exact revision in `SOURCE_STATE` |
| Original Linux 4.9.97 baseline | LineageOS and Huawei kernel contributors | Original project functional patches rebased from `4444781` |
| SukiSU Ultra 4.1.3 | ShirkNeko and SukiSU Ultra contributors | Root implementation at pinned commit `b1d534bc41941b2c818d7a1a1dac341e4aabfc2d` |
| SuSFS 2.2.0 | simonpunk and SuSFS contributors | Filesystem-hiding implementation at pinned commit `ee7dc7a03b7c836952cce55c5f3834de62a465d1` |
| Huawei Linux 4.9 SuSFS/KPM backport | Coconut (`Coconutat`) | Starting point for the legacy-kernel and Huawei compatibility portions of `patches/kernel/0001-par-android13-sukisu-susfs2.patch`; the released config still disables KPM |
| Binder sender security-context support | Todd Kjos / Android kernel contributors | Already present in the selected upstream; the original project backport is omitted |
| Huawei KernelSU references | xixiaobei-bei and Coconut (`Coconutat`) | Reference implementations used during the Huawei port |
| KernelSU upstream source | tiann and KernelSU contributors | Pinned official `main` revision used by the selectable feature workflow |
| SuSFS development source | simonpunk and SuSFS contributors | Pinned `gki-android12-5.10-dev` source and KernelSU integration patch |
| Re-Kernel | Sakion-Team and Re-Kernel contributors | Binder and signal wake/report integration |
| DroidSpaces | ravindu644 and DroidSpaces contributors | Linux 4.9 container requirements and qtaguid fix |
| NTSync | Elizabeth Figura, CodeWeavers, and WildKernels contributors | NTSync driver plus compatibility patch source |
| Baseband Guard | vc-teahouse/Baseband-guard contributors | Optional anti-format protection with boot/recovery blocking disabled |

The Binder work is based on Android common kernel commit
`3d5885175b90e5059a0ff3dcbe3ba93de9c8ff6f` (original upstream commit
`ec74136ded792deed80780d5fb8b557af1327d36`).

These upstream portions were used by the original Android 13/SukiSU/SuSFS
combination and are therefore retained with their original attribution and
licenses. Files under `research/kpm-failed/` are retained only as failed
experiment records: they are excluded from `scripts/apply.sh`, the formal
patch series, release images, and the list of implemented features.

The formal aggregate patch retains compatibility code inherited from
Coconut's combined SuSFS/KPM backport. Retaining that source is not a claim
that KPM is enabled or working: `CONFIG_KPM` is disabled in the published
release configuration.

## PAR-specific work

The original integration and device fixes were maintained by
yukino1111:

- adaptation of the pinned SukiSU and SuSFS revisions to this exact Huawei
  Kirin 970 Linux 4.9.97 tree and reproducible configuration;
- Huawei policydb, legacy-kernel API, build, GPT/AVB, and Android 13 integration
  needed by the published PAR image;
- the UID authorization guard added to SukiSU `sucompat`;
- the Kirin 970 VDEC protected-SMR fix in
  `0002-kirin970-vdec-keep-protected-smr-in-secure-world.patch`.

This local maintenance does not claim authorship of SukiSU, SuSFS, Linux,
Huawei, LineageOS, or the referenced Android Binder implementation.

The files under `patches/dev/` contain only the additional PAR/Linux 4.9
adaptation applied after those pinned upstream sources are fetched. In
particular, the KernelSU compatibility work retains the pinned official main
revision as its source base while reusing legacy API and Huawei SELinux techniques
from KernelSU-Next and `KernelSU_on_Huawei` where Linux 4.9 lacks newer APIs.

## Independent 9.1 migration

The migration reuses the original feature dependency pins. Re-Kernel Binder
integration is derived from Sakion-Team's pinned `Integrate/patches.sh`, rewritten
as a deterministic patch for Huawei's foreground queue. NTSync uses the new
base's native overflow helpers. The GSI fstab adaptation is independently
rewritten and host-tested; CFC Python 3 support and the DTC `yylloc` declaration
fix address build-tool compatibility. Initial boot, Wi-Fi and root checks passed on PAR; these do not validate every
optional feature. See the migration report for the remaining checks.

The old VDEC patch remains historical source in this repository but is excluded
from the new series. See `docs/UPSTREAM-REBASE.md` for omitted backports and the
limits of the source-provenance comparison.
