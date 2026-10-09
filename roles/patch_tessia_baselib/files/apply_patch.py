#!/usr/bin/env python3
"""
apply_patch.py <path_to_hmc.py> <patch_name>

Applies a single named patch to the tessia-baselib hmc.py file.
Each patch is idempotent: prints "PATCHED" if the change was made,
"ALREADY_APPLIED" if the new string was already present,
"NOT_FOUND" if neither old nor new string was found (upstream changed).

Exit codes:
  0 — success (patched, already applied, or not found — all non-fatal)
  1 — file could not be read/written
"""
import sys

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <hmc.py path> <patch_name>", file=sys.stderr)
    sys.exit(1)

path = sys.argv[1]
patch_name = sys.argv[2]

# ---------------------------------------------------------------------------
# Patch definitions: each entry is (old_string, new_string)
# The old_string is what the unpatched library contains.
# The new_string is the replacement.
# ---------------------------------------------------------------------------
PATCHES = {

    # -------------------------------------------------------------------------
    # Patch 1: LOGIN PROMPT
    # tessia waits for the literal "debirf-rescue login:" console message before
    # sending credentials. RHEL shows "<hostname> login:" instead.
    # The tuple format is (pattern_to_wait_for, command_to_send).
    # -------------------------------------------------------------------------
    "login_prompt": (
        "[('debirf-rescue login:', 'root'), ('Password:', os_passwd)]",
        "[(r'login:\\s*$', 'root'), ('Password:', os_passwd)]",
    ),

    # -------------------------------------------------------------------------
    # Patch 2: SHELL PROMPT PATTERN
    # After login, every command waits for MESSAGES_DEFAULT_PATTERN before
    # sending the next one. The debirf-specific pattern never matches RHEL.
    # -------------------------------------------------------------------------
    "shell_prompt": (
        "MESSAGES_DEFAULT_PATTERN = r'debirf-rescue:~#\\s*$'",
        "MESSAGES_DEFAULT_PATTERN = r'[#$]\\s*$'",
    ),

    # -------------------------------------------------------------------------
    # Patch 3: SCSI LOAD STATUS TIMEOUT
    # The default zhmcclient status_timeout (60 s) is too short for a RHEL
    # live disk to reach "operating" on s390x. Raise it to 300 s and accept
    # "exceptions" as a valid interim status.
    # -------------------------------------------------------------------------
    "scsi_load_timeout": (
        """\
            guest_obj.scsi_load(
                load_address=self._normalize_address(boot_params['devicenr']),
                wwpn=boot_params['wwpn'],
                lun=boot_params['lun'],
                wait_for_completion=True,
                force=True
            )""",
        """\
            guest_obj.scsi_load(
                load_address=self._normalize_address(boot_params['devicenr']),
                wwpn=boot_params['wwpn'],
                lun=boot_params['lun'],
                wait_for_completion=True,
                force=True,
                allow_status_exceptions=True,
                status_timeout=300
            )""",
    ),

    # -------------------------------------------------------------------------
    # Patch 4: HMC 500,263 RACE CONDITION
    # The HMC sometimes returns HTTP 500 reason 263 ("The load failed") even
    # when the LPAR booted successfully. Catch it and log a warning so
    # _do_netsetup / kexec can still proceed.
    # This patch depends on patch 3 (scsi_load_timeout) being applied first.
    # -------------------------------------------------------------------------
    "scsi_load_500_263": (
        """\
            guest_obj.scsi_load(
                load_address=self._normalize_address(boot_params['devicenr']),
                wwpn=boot_params['wwpn'],
                lun=boot_params['lun'],
                wait_for_completion=True,
                force=True,
                allow_status_exceptions=True,
                status_timeout=300
            )""",
        """\
            try:
                guest_obj.scsi_load(
                    load_address=self._normalize_address(boot_params['devicenr']),
                    wwpn=boot_params['wwpn'],
                    lun=boot_params['lun'],
                    wait_for_completion=True,
                    force=True,
                    allow_status_exceptions=True,
                    status_timeout=300
                )
            except zhmcclient.HTTPError as exc:
                # 500,263: HMC reports load failed but LPAR often boots
                # successfully anyway (race in HMC status reporting).
                if exc.http_status == 500 and exc.reason == 263:
                    self._logger.warning(
                        'HMC returned 500,263 for scsi_load - LPAR may still '
                        'have booted. Proceeding with netsetup.')
                else:
                    raise""",
    ),

    # -------------------------------------------------------------------------
    # Patch 5: WAIT FOR LPAR OPERATING STATUS BEFORE SENDING OS COMMANDS
    # After scsi_load completes, the HMC briefly leaves the LPAR in a
    # transitional status before it reaches "operating" or "exceptions".
    # Calling send_os_command during that window fails with HTTP 409,332
    # "The image is not in the operating or exceptions state."
    # This patch adds a polling loop in _do_netsetup that waits up to 120 s
    # for the LPAR to reach one of those states before opening the OS messages
    # channel.
    # The OLD string is the result after patch_1 (login_prompt) is applied.
    # -------------------------------------------------------------------------
    "wait_for_operating": (
        """\
        with Messages.connect(_get_guest_os_channel, self.host_name, self.user, self.passwd) as receiver:
            self._logger.debug("Waiting for live image login prompt")
            self._send_commands(
                guest_obj,
                [(r'login:\\s*$', 'root'), ('Password:', os_passwd)],
                receiver)""",
        """\
        # Wait for LPAR to reach 'operating' or 'exceptions' before trying
        # to send OS commands (HTTP 409,332 if we call too early).
        _wait_deadline = time.monotonic() + 120
        while time.monotonic() < _wait_deadline:
            _lpar_status = guest_obj.get_property('status')
            if _lpar_status in ('operating', 'exceptions'):
                break
            self._logger.debug(
                "LPAR status is '%s', waiting for operating/exceptions ...",
                _lpar_status)
            time.sleep(5)
        else:
            self._logger.warning(
                "LPAR did not reach operating/exceptions within 120 s "
                "(status=%s); proceeding anyway", _lpar_status)
        with Messages.connect(_get_guest_os_channel, self.host_name, self.user, self.passwd) as receiver:
            self._logger.debug("Waiting for live image login prompt")
            self._send_commands(
                guest_obj,
                [(r'login:\\s*$', 'root'), ('Password:', os_passwd)],
                receiver)""",
    ),
}

if patch_name not in PATCHES:
    print(f"Unknown patch name: {patch_name}", file=sys.stderr)
    print(f"Available patches: {', '.join(PATCHES)}", file=sys.stderr)
    sys.exit(1)

old, new = PATCHES[patch_name]

try:
    with open(path) as f:
        content = f.read()
except OSError as exc:
    print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
    sys.exit(1)

if new in content:
    print(f"ALREADY_APPLIED: {patch_name}")
    sys.exit(0)

if old not in content:
    print(f"NOT_FOUND: {patch_name} — old string not present; library may have changed upstream")
    sys.exit(0)

try:
    with open(path, "w") as f:
        f.write(content.replace(old, new, 1))
except OSError as exc:
    print(f"ERROR: cannot write {path}: {exc}", file=sys.stderr)
    sys.exit(1)

print(f"PATCHED: {patch_name}")
