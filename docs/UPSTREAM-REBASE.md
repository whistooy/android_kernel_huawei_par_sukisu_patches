# Independent Nova 3 upstream migration

This migration starts from project commit `4444781` (the last complete selectable-feature builder before the EMUI9.1 migration), based on LineageOS `b8f2dd993aa2f67ceefd98b5475fec29c6032f6b`, Linux4.9.97. The intervening Antigravity EMUI9.1 branch is reference material only. KernelSU, SuSFS and other dependency pins remain those from the original9.0 feature builder. KernelSU-Next is not substituted.

## Selected upstream and cross-checks

Selected: [Mashopy/android_kernel_huawei_kirin970](https://github.com/Mashopy/android_kernel_huawei_kirin970/tree/huawei/kirin970_p_9.0), commit `5208809c3fb8faa74ba07abff32015ff69d3b7f3`, Linux4.9.148. The branch has separate per-directory Nova3 EMUI9.1 and HarmonyOS2 import commits. This documents the maintainer's provenance claim; the original Huawei archives have not been independently hash-verified.

| Reference | Revision | Role and findings |
|---|---|---|
| LineageOS original | b8f2dd993aa2f67ceefd98b5475fec29c6032f6b | Original4.9.97 functionality baseline; lacks EROFS and unconditional EAPOL marking |
| xiaoleGun Huawei9.1 import | d8663547249ba30de44e91dec4bf45aaa6cf9eba | 4.9.148 Honor10/Kirin970 import with Huawei source-download URL in commit message; cross-check for vendor interfaces, not proof of PAR compatibility |
| Mashopy Nova3 | 5208809c3fb8faa74ba07abff32015ff69d3b7f3 | Same display and Mali ioctl headers as Huawei9.1 reference; same Hi1102 HCC serialization and firmware loader; includes unconditional EAPOL flag and newer Binder support |
| HoleHolo KernelSU-Next | f014759c294baab2708ce0ceb25f2b4094f8de2f | Modified4.9.149 reference only; pins KernelSU-Next submodule cba275cde2c986a4c050c565fbeb03315f7be796; still gates EAPOL flag on debug mode |

HoleHolo's README reports encrypted-Wi-Fi failures on some firmware and attributes them to HAL compatibility. That is its author's explanation, not a verified root cause. Our device A/B and final EAPOL-fix test demonstrated the marker defect for our firmware. Do not assume the same explanation has been tested on HoleHolo's hardware.

Linux 4.14 / EMUI 12 is outside this migration’s compatibility scope. The selected base remains Linux 4.9.

## Concrete compatibility findings

- Mashopy and the Huawei9.1 reference have byte-identical `hisi_dss.h` and Mali r14 `mali_kbase_ioctl.h`. This supports keeping the current vendor userspace ABI; it does not prove every runtime driver path is identical.
- Hi1102 `hmac_hcc_adapt.c` and `plat_firmware.c` are identical across the selected and Huawei9.1 trees. EAPOL classification moves one assignment outside `_PRE_DEBUG_MODE` in the HarmonyOS driver import. No embedded replacement firmware is needed.
- The selected Binder already supports transaction security contexts and extended context-manager registration. The old9.0 backport is omitted, preserving newer upstream checks.
- GPT `_a` suffix handling is already upstream. Do not duplicate it.
- The old `SMMU_ConfigSMR()` protected-bank writer is absent in the selected VDEC source. The old PAR patch targeting that function is retained as historical reference but is not in the applied series.
- DTB location remains `0x07A00000`. The HarmonyOS import splits the old supersonic region into `0x9B0000` plus a `0x50000` fingerprint reservation at `0x13FB0000`; these header definitions alone do not establish runtime allocation. Fingerprint, camera, video, suspend and restart require device testing.
- EROFS is native in the selected upstream. Do not transplant the earlier9.1 EROFS patch again.

## Migration rules

Keep feature changes explicit and reviewable. Configuration derives from new upstream defaults plus the original project's differences against an expanded Lineage defconfig, not a difference against its abbreviated defconfig file. Selectable features remain KernelSU/SuSFS, Re-Kernel, DroidSpaces prerequisites, NTSync, BBG and network extensions. Re-Kernel network wake monitoring stays disabled by default.

The PAR GSI fstab fix is independently rewritten: disable only `preavs`, remove only exact `avb`/`avb=` tokens, preserve other flags, and update OF properties before sysfs publication. It is controlled by `CONFIG_PAR_GSI_FSTAB`. Host CFC Python3 compatibility is explicit in the patch series.

## Validation status

The source migration has now been tested on the phone. The initial candidate booted and connected to WPA2 Wi-Fi but failed to persist KernelSU authorization. The corrected image described below is installed. The previous EAPOL-fixed kernel and the full pre-flash kernel partition remain available for rollback. AL00 package-extracted kernels are not backups of the phone's original stock kernel.

| Check | Result |
|---|---|
| Pinned source preparation | All patches apply; final clean replay matches the compiled tracked changes and copied feature sources |
| Full default-feature build | Passed with pinned GCC4.9 on the host: switchable SELinux, KernelSU32629, SuSFS2.3.0, Re-Kernel, network extensions, DroidSpaces prerequisites, NTSync and BBG; Re-Kernel network monitor off |
| Enforcing default-feature config | Passed config generation and assertions; not a separate full build |
| All optional features off | Clean preparation, enforcing config and compilation of affected filesystem, Binder, OF, input, signal, reboot and SELinux objects passed; not a full linked image |
| KernelSU only, NTSync/SuSFS/other options off | Clean preparation and config passed; KernelSU linked object and affected core hook objects compiled with generated SELinux headers; not a full image |
| GSI fstab host test | Passed with ASan/UBSan: exact AVB tokens, unrelated-flag preservation, preavs matching, property lengths and allocation/update failures |
| Image validation | Android boot header v1, 2048-byte page, expected PAR load addresses, gzip and ARM64 payload, payload equality and partition limit passed |
| Device validation | Boot, WPA2 reconnect, gateway ping, root, SELinux switching and authorization reload after manual restart passed. Automatic reboot still powers off. Fingerprint/camera/video/audio/suspend remain unvalidated |

Initial candidate (superseded): `KERNEL-PAR-selinux-switchable-ksu1-susfs1-rk1-rkn0-net1-ds1-ntsync1-bbg1.img`, 15,329,280 bytes (partition limit25,165,824), SHA256 `0cdfe65bc5361c05bc322fdc9b6eabe644f644b59ed85b4bb65d0db2fb217177`.

The packaging retains the original Android9.0 / April2019 header metadata. These fields are packaging inputs, not evidence of the phone's original firmware or a claim that this source is EMUI9.0. An explicit `enforcing=1` kernel argument keeps the switchable build enforcing at startup; runtime switching remains available through the original interface.

The build is not warning-free: 23 modpost section warnings refer to unchanged Huawei reserve/probe functions and `.cfc.text`, rather than the rewritten OF/Re-Kernel functions. They have been retained for review; no claim is made that all runtime consequences have been ruled out. Other retained vendor/compiler warnings are in the full build log. The full feature matrix, Docker execution and historical SukiSU-only scripts have not been validated in this migration.

Full build logs and raw device evidence are retained in the maintainer’s local archive, outside this Git repository. Build artifacts include `SOURCE_STATE`, `kernel.config`, `build-info.txt` and `build-inputs.sha256`. The validation table distinguishes complete builds, object-only checks and device observations.


## Integration changes found during clean preparation

- Re-Kernel's pinned automatic injector assumes one `proc->todo` enqueue and fails on Huawei's foreground queue. The explicit integration preserves that queue and places async replacement under the pending-async branch. Superseded buffers are freed after dropping Binder locks, using this upstream's three-argument buffer-release API. Signal reporting and the original freezer compatibility are retained.
- NTSync no longer replaces `overflow.h`: the selected base already supplies checked sizing/arithmetic. Newer include-path compatibility headers are shared with KernelSU and applied independently of the NTSync switch.
- New stock config defaults cannot alone represent the original selectable profile. The switchable config explicitly enables `SECURITY_SELINUX_DEVELOP`; the original disabled Huawei policy-readonly/PMALLOC/LSM-readonly settings are preserved for KernelSU policy updates. These values are asserted after `olddefconfig`.
- Modern host GCC needs the DTC lexer to declare, rather than redefine, `yylloc`. Both generated and source lexer copies are patched. CFC's existing Python3 compatibility is explicit. No broad compiler-warning suppression was introduced.


## Device follow-up: authorization persistence

Current image SHA256: `6266105f9fd491c8b99747f0d9bd0ce1055d423ebe7f8d3e33eb48605898bf0c`, 15,329,280 bytes. Its exact image-length kernel-partition readback matches. It identifies as Linux4.9.148+, build #2, Oct6 09:12:47 CST2026.

The first candidate's manager recognized KernelSU32629-4, but shell authorization was off. Regranting restored root only in memory: `save_allow_list create file failed: -126` (`ENOKEY`) left `/data/adb/ksu/.allowlist` empty. Legacy fscrypt resolves encryption keys through credentials/keyrings; KernelSU's saved `ksu_cred` was created during kernel initialization, before data keys were installed.

`patches/dev/kernelsu/0003-par-allowlist-fscrypt-keyrings.patch` makes the existing init task-work callback copy init's current credentials, preserving its current keyrings, then temporarily use the KernelSU SELinux domain for the save. It releases those temporary credentials on exit. It does not disable encryption or change init's permanent credentials. The patch replays against the independently prepared pinned KernelSU tree and matches the compiled source.

After flashing the correction, regranting shell created a valid792-byte version4 permission file. Following a normal Android reboot request that powered the phone off and a user-assisted power-on, ADB `su` worked immediately without reopening the manager or regranting. The permission file was byte-identical to its pre-restart backup. Wi-Fi reconnected and the gateway replied5/5. SELinux is Enforcing; the earlier bidirectional switch test restored Enforcing.

The older working kernel and this migration use identical KernelSU commit `33d0c9205df47b6b1b61c25c13afa164b88871d1`. Comparing97 kernel/UAPI entries, including added compatibility files and symlinks, found only the new allowlist patch differs. Kernel keyring process code and F2FS file-open code also match in the inspected old/new trees. HWAA differs in config (old disabled, new enabled), but remains enabled in the corrected build. The precise reason the older runtime did not expose the missing-key problem has not been isolated; these tests support the credential/keyring correction, not a claim that HWAA was the root cause.

Raw device logs and the old/new dependency comparison are retained locally. Automatic reboot remains unresolved and is distinct from authorization persistence. The collected post-restart dmesg no longer contains the early allowlist-load messages; reload is established by immediate root access and unchanged permission bytes, not by a claimed startup-log line.

Further comparison with official v0.9.5, HoleHolo's pinned KernelSU-Next and the original SukiSU pin is in [ALLOWLIST-HISTORY.md](ALLOWLIST-HISTORY.md). The user reports an earlier successful test in Permissive; a controlled SELinux-mode A/B was not performed, so SELinux influence has not been ruled out.

## Publication audit (2026-10-07)

A new checkout from the pinned Git objects, followed by the complete default-feature
patch preparation, was compared with the source used for the installed image:

- All 67,037 prepared kernel entries matched after normalizing one equivalent
  relative symlink. The installed source additionally contained three generated
  Python bytecode cache files; these are not source changes.
- All seven dependency trees matched, including 674 KernelSU entries and the
  allowlist credential fix. Complete KernelSU history reports 2,629 commits,
  retaining internal version 32629.
- The regenerated switchable default-feature `.config` was byte-identical to the
  installed image’s archived `kernel.config`.
- The fstab host test passed with ASan/UBSan. Shell syntax, diff whitespace and
  every recorded `SOURCE_STATE` SHA256 input were checked.
- The archived installed image matched SHA256
  `6266105f9fd491c8b99747f0d9bd0ce1055d423ebe7f8d3e33eb48605898bf0c`.

This audit verifies source/configuration replay; it did not rebuild the entire
image or claim byte-identical binary reproducibility. Full-build and device
results above remain the prior validation results.

To repeat source preparation and the fstab test from this repository:

```bash
PREPARE_ONLY=1 scripts/build_par_kernel_dev_ci.sh \
  selinux-switchable /absolute/path/to/empty-audit-directory
python3 tests/test_par_fstab.py /absolute/path/to/empty-audit-directory/kernel
```

A local Git cache is optional. Shared clones depend on their source object stores:
keep those caches available, and update Git alternate-object paths if moving them.
The audit’s machine-readable file comparisons remain in the local archive.

The subsequent publication cleanup translates inherited Chinese comments in
`fs/notify/fdinfo.c` and `kernel/sys.c` and removes redundant editing notes.
Non-comment added code and patch hunk line counts are unchanged. `SOURCE_STATE`
records the updated patch hash; the installed image’s source archive and build
manifest retain the original comments and hashes.
