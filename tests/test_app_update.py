import hashlib
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "desk", "app"))
import update  # noqa: E402


class Versions(unittest.TestCase):
    def test_newer_compares_numbers_not_text(self):
        self.assertTrue(update.newer("1.10.0", "1.9.3"))
        self.assertTrue(update.newer("v2.0.0", "1.99.99"))
        self.assertFalse(update.newer("1.0.0", "1.0.0"))
        self.assertFalse(update.newer("1.0", "1.0.1"))

    def test_check_finds_the_release_asset_and_never_raises(self):
        rel = {"tag_name": "v9.9.9", "body": "notes", "html_url": "https://example.test/r",
               "assets": [{"name": "Saladi-Setup.exe", "browser_download_url": "https://example.test/s.exe"},
                          {"name": "Saladi-Setup.exe.sha256", "browser_download_url": "https://example.test/s.sha"}]}
        import json
        with mock.patch.object(update, "_get", return_value=json.dumps(rel).encode()):
            info = update.check(force=True)
        self.assertTrue(info["available"])
        self.assertEqual((info["latest"], info["asset"], info["sha"]),
                         ("9.9.9", "https://example.test/s.exe", "https://example.test/s.sha"))
        with mock.patch.object(update, "_get", side_effect=OSError("offline")):
            info = update.check(force=True)
        self.assertFalse(info["available"])
        self.assertIn("could not reach GitHub", info["error"])


class Download(unittest.TestCase):
    def test_a_download_that_fails_its_checksum_is_refused(self):
        data = b"new exe bytes"
        good = hashlib.sha256(data).hexdigest()
        info = {"asset": "A", "sha": "S"}
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(update, "_get", side_effect=lambda u, timeout=0: (good + "  x").encode() if u == "S" else data):
                path = update.download(info, d)
            with open(path, "rb") as fh:
                self.assertEqual(fh.read(), data)
            with mock.patch.object(update, "_get", side_effect=lambda u, timeout=0: b"0" * 64 if u == "S" else data):
                with self.assertRaises(RuntimeError):
                    update.download(info, d)
        with self.assertRaises(RuntimeError):
            update.download({"asset": "A", "sha": None})

    def test_install_copies_the_exe_into_the_install_folder(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "Saladi-Setup.exe")
            with open(src, "wb") as fh:
                fh.write(b"exe")
            with mock.patch.dict(os.environ, {"LOCALAPPDATA": os.path.join(d, "local")}):
                dst = update.install(src, shortcuts=False, register=False)
                self.assertTrue(dst.endswith(os.path.join("Programs", "Saladi", "Saladi.exe")))
                self.assertTrue(update.is_installed_copy(dst))
                self.assertFalse(update.is_installed_copy(src))
            with open(dst, "rb") as fh:
                self.assertEqual(fh.read(), b"exe")

    def test_the_swap_script_waits_copies_and_restarts(self):
        with tempfile.TemporaryDirectory() as d:
            new = os.path.join(d, "Saladi-Setup.exe")
            target = os.path.join(d, "app", "Saladi.exe")
            script = update.swap_script(new, target, 4321)
            with open(script) as fh:
                text = fh.read()
            self.assertIn('PID eq 4321', text)
            self.assertIn('copy /y "%s" "%s"' % (new, target), text)
            self.assertIn('start "" "%s"' % target, text)


if __name__ == "__main__":
    unittest.main()
