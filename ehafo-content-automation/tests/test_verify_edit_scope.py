import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "verify_edit_scope.py"


class EditScopeTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            ["python3", str(SCRIPT), *map(str, args)],
            capture_output=True,
            text=True,
        )

    def test_allows_only_whitelisted_changes_and_keeps_locked_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "src" / "Body.tsx"
            locked = root / "assets" / "header.png"
            target.parent.mkdir()
            locked.parent.mkdir()
            target.write_text("before", encoding="utf-8")
            locked.write_bytes(b"locked")
            baseline = root.parent / f"{root.name}-baseline.json"

            snapshot = self.run_script("snapshot", root, "--output", baseline)
            self.assertEqual(snapshot.returncode, 0, snapshot.stderr)
            target.write_text("after", encoding="utf-8")

            verify = self.run_script(
                "verify", root, "--baseline", baseline,
                "--allow", "src/Body.tsx", "--lock",
                f"assets/header.png={hashlib.sha256(b'locked').hexdigest()}",
            )
            self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)

    def test_rejects_change_outside_whitelist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            allowed = root / "src" / "Body.tsx"
            forbidden = root / "src" / "Root.tsx"
            allowed.parent.mkdir()
            allowed.write_text("before", encoding="utf-8")
            forbidden.write_text("before", encoding="utf-8")
            baseline = root.parent / f"{root.name}-baseline.json"

            self.assertEqual(
                self.run_script("snapshot", root, "--output", baseline).returncode, 0
            )
            forbidden.write_text("after", encoding="utf-8")
            verify = self.run_script(
                "verify", root, "--baseline", baseline,
                "--allow", "src/Body.tsx",
            )
            self.assertNotEqual(verify.returncode, 0)
            self.assertIn("changed_outside_allowlist:src/Root.tsx", verify.stdout)

    def test_rejects_locked_asset_that_does_not_match_expected_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            locked = root / "assets" / "header.png"
            locked.parent.mkdir()
            locked.write_bytes(b"wrong-file")
            baseline = root.parent / f"{root.name}-baseline.json"

            self.assertEqual(
                self.run_script("snapshot", root, "--output", baseline).returncode, 0
            )
            verify = self.run_script(
                "verify", root, "--baseline", baseline,
                "--lock", f"assets/header.png={'0' * 64}",
            )
            self.assertNotEqual(verify.returncode, 0)
            self.assertIn("locked_asset_checksum_mismatch:assets/header.png", verify.stdout)


if __name__ == "__main__":
    unittest.main()
