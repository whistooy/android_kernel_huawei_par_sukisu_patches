# Authorization persistence: older KernelSU implementations

This is source comparison, not a controlled SELinux A/B test. The user recalls an earlier successful test running Permissive. That is a material difference from the new image's explicit `enforcing=1` boot argument. Current runtime was checked as Enforcing, and the corrected image saved and reloaded the authorization file across a user-assisted restart. These results establish that the correction works in the tested state; they do not isolate every reason the earlier kernel appeared unaffected.

## Compared implementations

| Source | Save context | Legacy keyring handling |
|---|---|---|
| [Official KernelSU v0.9.5](https://github.com/tiann/KernelSU/blob/v0.9.5/kernel/kernel_compat.c#L80) | Workqueue, `ksu_filp_open_compat()` | For Linux <4.10 or `CONFIG_IS_HW_HISI`, installs `init_session_keyring` when a worker lacks a session keyring |
| [HoleHolo's pinned KernelSU-Next](https://github.com/rifsxd/KernelSU-Next/blob/cba275cde2c986a4c050c565fbeb03315f7be796/kernel/kernel_compat.c#L80) | Same workqueue/open-wrapper pattern | Same init-keyring installation, also enabled by `CONFIG_KSU_ALLOWLIST_WORKAROUND` |
| [Original project's SukiSU builtin pin](https://github.com/SukiSU-Ultra/SukiSU-Ultra/blob/b1d534bc41941b2c818d7a1a1dac341e4aabfc2d/kernel/policy/allowlist.c) | Task-work on PID1, `override_creds(ksu_cred)` and direct `filp_open()` | No equivalent keyring installation in this save path |
| Current official KernelSU pin `33d0c920` before the PAR fix | Task-work on PID1, `override_creds(ksu_cred)` | Captured boot-time credentials used instead of init's current credentials |

In v0.9.5, `kernel/core_hook.c:629` captures `cred->session_keyring` when its key-permission hook runs for init. The open wrapper subsequently installs that saved ring for a worker lacking one.

The older workaround is narrower than globally disabling protections: it supplies an appropriate keyring to an execution context that lacks one. Our current execution context is already init task-work, so importing the old workqueue/namespace machinery is unnecessary. The PAR patch prepares a temporary copy of init's current credentials and changes its SELinux domain for the save, preserving current keyring references.

## Upstream history and SELinux relevance

- [bc352398084e385ba94326782cbec93c4c90efa6](https://github.com/tiann/KernelSU/commit/bc352398084e385ba94326782cbec93c4c90efa6), November2025: removes compatibility open/read/write wrappers with the rationale “because we're in the right context now”. Older non-GKI support had already been dropped earlier in the official lineage; this does not mean a Huawei4.9 port can assume the same environment as supported upstream kernels.
- [28fedfa1b3e739c1fb5da44309f32ecc99e85d26](https://github.com/tiann/KernelSU/commit/28fedfa1b3e739c1fb5da44309f32ecc99e85d26), March2026: adds `override_creds(ksu_cred)` to the save callback. Its stated purpose is to handle modules changing the allowlist's context so init cannot modify it, referencing issue3234. Simply removing the credential override would discard that SELinux-related intent.
- The [Huawei integration guide](https://github.com/xixiaobei-bei/KernelSU_on_Huawei/blob/f0b3dabd03548f4f5e1c2ffc0415269049fdc387/website/docs/guide/how-to-intergrate-kernelsu.md) explicitly discusses Huawei SELinux read-only protections and enabling `SECURITY_SELINUX_DEVELOP` for permissive startup. This pinned repository is a guide, not a separate `kernel/allowlist.c` implementation. Its advice is not proof that HWAA caused our ENOKEY.

## What is proven and what remains uncertain

Observed before correction: in-memory root grant succeeds, saving returns ENOKEY, permission file remains empty. Observed after correction: a valid792-byte permission file is saved and the same bytes reload after power-on; root works immediately in Enforcing. HWAA stays enabled.

The source history independently supports treating init's keyring as a required legacy compatibility concern. It does not prove the observed ENOKEY was solely caused by a null keyring pointer: key searches involve access checks, and available/cached inode keys and SELinux state can affect the result. No matched unpatched-Permissive versus unpatched-Enforcing test, with controlled inode/key cache state, was performed. Do not claim SELinux has been ruled out or that an older Permissive test proves the original code is correct in Enforcing.

Our previous working-kernel dependency and the current dependency use the same official KernelSU commit. A comparison of97 kernel/UAPI entries, including added compatibility files and symlinks, found only the new PAR allowlist patch differs. That rules out an unnoticed difference in those KernelSU files, but not differences in boot mode, kernel configuration, filesystem state or initialization timing.

Downloaded reference trees, raw device logs and the old/new dependency comparison are retained in the maintainer’s local archive; they are not included in this repository. The pinned upstream links above identify the implementations being compared.
