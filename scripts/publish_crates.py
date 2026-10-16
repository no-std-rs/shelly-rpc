"""Publish verified workspace archives, resuming an interrupted release safely."""

import hashlib
import json
from pathlib import Path
import subprocess
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ("shelly-rpc", "shellyctl")


def published_version(name, version):
    url = f"https://crates.io/api/v1/crates/{quote(name, safe='')}/{quote(version, safe='')}"
    request = Request(url, headers={"User-Agent": "shelly-rpc-release (https://github.com/no-std-rs/shelly-rpc)"})
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)["version"]
    except HTTPError as error:
        if error.code == 404:
            return None
        raise


def publish_package(name, version, archive):
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    existing = published_version(name, version)
    if existing is not None:
        if existing["num"] != version or existing["checksum"] != checksum or existing["yanked"]:
            raise RuntimeError(f"{name} {version}: existing publication is yanked or differs from the verified archive")
        print(f"{name} {version}: identical archive already published; continuing", flush=True)
        return
    subprocess.run(["cargo", "publish", "--locked", "-p", name], cwd=ROOT, check=True)


def publish_all(version, target_directory):
    for name in PACKAGES:
        publish_package(name, version, target_directory / "package" / f"{name}-{version}.crate")


def main():
    metadata = json.loads(subprocess.check_output(
        ["cargo", "metadata", "--locked", "--no-deps", "--format-version", "1"],
        cwd=ROOT, text=True,
    ))
    versions = {package["name"]: package["version"] for package in metadata["packages"]}
    version = versions[PACKAGES[0]]
    if any(versions[name] != version for name in PACKAGES):
        raise RuntimeError("Public workspace versions must match")
    publish_all(version, Path(metadata["target_directory"]))


if __name__ == "__main__":
    main()
