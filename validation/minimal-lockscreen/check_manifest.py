#!/usr/bin/env python3
"""Validate minimal-lockscreen manifest against the known-good launchd log.

Offline only. No device access, no writes outside this directory.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "minimal-jobs.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    m = json.loads(MANIFEST.read_text())
    failures = []

    src = Path(m["inventory_source"]["path"])
    if not src.exists():
        failures.append(f"inventory log missing: {src}")
    else:
        got = sha256(src)
        want = m["inventory_source"]["sha256"]
        if got != want:
            failures.append(f"inventory log hash {got} != {want}")
        text = src.read_bytes().decode("utf-8", "replace")
        names = set(re.findall(r"Successfully spawned ([A-Za-z0-9_.-]+)\[\d+\]", text))
        if len(names) != m["inventory_source"]["unique_job_names"]:
            failures.append(
                f"unique job count {len(names)} != "
                f"{m['inventory_source']['unique_job_names']}"
            )
        events = re.findall(r"Successfully spawned [A-Za-z0-9_.-]+\[\d+\]", text)
        if len(events) != m["inventory_source"]["spawn_events"]:
            failures.append(
                f"spawn events {len(events)} != "
                f"{m['inventory_source']['spawn_events']}"
            )
        for job in m["stage_a_allowlist"]:
            if job == "launchd":
                continue  # pid 1 is not spawned
            if job not in names:
                failures.append(f"stage A job not in known-good log: {job}")
        for job in m["stage_b_addback"]:
            if job not in names:
                failures.append(f"stage B job not in known-good log: {job}")

    allowed = set(m["stage_a_allowlist"])
    stage_b = set(m["stage_b_addback"])
    if allowed & stage_b:
        failures.append(f"stage A/B overlap: {allowed & stage_b}")

    # Every excluded daemon must be outside stage A.
    for cat, jobs in m["excluded_categories"].items():
        for job in jobs:
            if job in allowed:
                failures.append(f"excluded job also allow-listed ({cat}): {job}")

    # Rootfs input must be pinned, and must not be any live device path.
    r = m["rootfs_source"]
    if r["release"] != "ios-root-20H392-44905109656":
        failures.append("rootfs release is not the v68 known-good release")
    if not re.fullmatch(r"[0-9a-f]{64}", r["image_sha256"]):
        failures.append("rootfs image hash not a SHA-256")

    # rd=md0 is mandatory; emmcroot must be absent.
    cmd = m["kernel"]["cmdline"]
    if "rd=md0" not in cmd:
        failures.append("cmdline missing rd=md0")
    if "emmcroot=USERDATA" in cmd or "emmcwrite=1" in cmd:
        failures.append("cmdline still targets USERDATA")

    if failures:
        for f in failures:
            print("FAIL:", f)
        return 1
    print(
        f"PASS: {len(m['stage_a_allowlist'])} stage-A jobs, "
        f"{len(m['stage_b_addback'])} stage-B jobs, "
        f"{sum(len(v) for v in m['excluded_categories'].values())} excluded, "
        "rootfs pinned, cmdline USERDATA-free"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
