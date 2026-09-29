import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
CXS = PROJECT / "cxs"


class CxsCliTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="cxs-test-"))
        self.home = self.root / "codex-home"
        self.dummy = self.root / "codex"
        self.dummy.write_text(
            "#!/bin/sh\n"
            "printf 'CODEX_HOME=%s\\n' \"$CODEX_HOME\"\n"
            "printf 'ARGS=%s\\n' \"$*\"\n",
            encoding="utf-8",
        )
        self.dummy.chmod(0o755)
        self.env = os.environ.copy()
        self.env["CODEX_HOME"] = str(self.home)
        self.env["CODEX_CLI_PATH"] = str(self.dummy)

    def run_cxs(self, *args, check=True):
        result = subprocess.run(
            [str(CXS), *args],
            env=self.env,
            text=True,
            capture_output=True,
        )
        if check and result.returncode != 0:
            self.fail("%s\nstdout=%s\nstderr=%s" % (args, result.stdout, result.stderr))
        return result

    def test_create_select_show_and_permissions(self):
        self.run_cxs("new", "proxy", "--model", "proxy-model", "--base-url", "https://proxy.example/v1", "--env-key", "PROXY_KEY")
        self.run_cxs("use", "proxy")
        profile = self.home / "proxy.config.toml"
        state = self.home / "cli-switch" / "state.json"
        self.assertEqual(stat.S_IMODE(profile.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(state.stat().st_mode), 0o600)
        self.assertIn("wire_api = \"responses\"", profile.read_text(encoding="utf-8"))
        shown = self.run_cxs("show").stdout
        self.assertIn("model_provider: proxy", shown)
        self.assertIn("PROXY_KEY", shown)
        self.assertNotIn("proxy.example/v1?", shown)

    def test_run_sets_home_and_profile_and_respects_explicit_profile(self):
        self.run_cxs("new", "native", "--model", "gpt-test")
        self.run_cxs("use", "native")
        result = self.run_cxs("run", "exec", "hello")
        self.assertIn("CODEX_HOME=%s" % self.home.resolve(), result.stdout)
        self.assertIn("ARGS=--profile native exec hello", result.stdout)
        result = self.run_cxs("run", "--profile", "other", "exec", "hello")
        self.assertIn("ARGS=--profile other exec hello", result.stdout)
        self.assertNotIn("--profile native", result.stdout)

    def test_rejects_credentials_in_base_url(self):
        result = self.run_cxs(
            "new", "bad", "--model", "m", "--base-url", "https://user:pass@example/v1", check=False
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.home / "bad.config.toml").exists())


if __name__ == "__main__":
    unittest.main()
