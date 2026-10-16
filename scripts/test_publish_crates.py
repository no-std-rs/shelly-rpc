import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

import publish_crates


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.target = Path(self.directory.name)
        (self.target / "package").mkdir()
        for name in publish_crates.PACKAGES:
            (self.target / "package" / f"{name}-0.1.1.crate").write_bytes(name.encode())

    def existing(self, name):
        return {"num": "0.1.1", "checksum": hashlib.sha256(name.encode()).hexdigest(), "yanked": False}

    def test_resume_skips_identical_library_and_publishes_cli(self):
        with patch.object(publish_crates, "published_version", side_effect=[self.existing("shelly-rpc"), None]), patch.object(publish_crates.subprocess, "run") as run:
            publish_crates.publish_all("0.1.1", self.target)
        run.assert_called_once_with(["cargo", "publish", "--locked", "-p", "shellyctl"], cwd=publish_crates.ROOT, check=True)

    def test_completed_release_does_not_upload_again(self):
        with patch.object(publish_crates, "published_version", side_effect=[self.existing(name) for name in publish_crates.PACKAGES]), patch.object(publish_crates.subprocess, "run") as run:
            publish_crates.publish_all("0.1.1", self.target)
        run.assert_not_called()

    def test_different_existing_archive_stops_before_upload(self):
        existing = self.existing("different bytes")
        with patch.object(publish_crates, "published_version", return_value=existing), patch.object(publish_crates.subprocess, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "differs"):
                publish_crates.publish_all("0.1.1", self.target)
        run.assert_not_called()

    def test_yanked_version_is_not_silently_accepted(self):
        existing = self.existing("shelly-rpc") | {"yanked": True}
        with patch.object(publish_crates, "published_version", return_value=existing), patch.object(publish_crates.subprocess, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "yanked"):
                publish_crates.publish_all("0.1.1", self.target)
        run.assert_not_called()

    def test_registry_not_found_means_unpublished(self):
        error = HTTPError("https://crates.io", 404, "Not Found", {}, None)
        with patch.object(publish_crates, "urlopen", side_effect=error):
            self.assertIsNone(publish_crates.published_version("shelly-rpc", "0.1.1"))

    def test_registry_outage_is_not_treated_as_unpublished(self):
        error = HTTPError("https://crates.io", 503, "Unavailable", {}, None)
        with patch.object(publish_crates, "urlopen", side_effect=error), patch.object(publish_crates.subprocess, "run") as run:
            with self.assertRaises(HTTPError):
                publish_crates.publish_all("0.1.1", self.target)
        run.assert_not_called()

    def test_lookup_reads_registry_metadata(self):
        expected = self.existing("shelly-rpc")
        response = io.BytesIO(json.dumps({"version": expected}).encode())
        with patch.object(publish_crates, "urlopen", return_value=response):
            self.assertEqual(publish_crates.published_version("shelly-rpc", "0.1.1"), expected)


if __name__ == "__main__":
    unittest.main()
