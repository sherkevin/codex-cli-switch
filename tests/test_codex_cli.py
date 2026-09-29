import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
MANAGER = PROJECT / "codex-cli"
SHIM = PROJECT / "codex"


class CodexCliTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="codex-cli-test-"))
        self.default_home = self.root / "official"
        self.jessica_home = self.root / "jessica"
        self.default_home.mkdir()
        self.jessica_home.mkdir()
        self.state_home = self.root / "manager"
        self.real_codex = self.root / "real-codex"
        self.real_codex.write_text(
            "#!/bin/sh\n"
            "printf 'CODEX_HOME=%s\\n' \"$CODEX_HOME\"\n"
            "printf 'ARGS=%s\\n' \"$*\"\n",
            encoding="utf-8",
        )
        self.real_codex.chmod(0o755)
        self.env = os.environ.copy()
        self.env.update(
            {
                "HOME": str(self.root),
                "CODEX_CLI_HOME": str(self.state_home),
                "CODEX_CLI_DEFAULT_HOME": str(self.default_home),
                "CODEX_REAL_BIN": str(self.real_codex),
            }
        )

    def run_manager(self, *args, check=True):
        result = subprocess.run(
            [str(MANAGER), *args],
            env=self.env,
            text=True,
            capture_output=True,
        )
        if check and result.returncode != 0:
            self.fail("%s\nstdout=%s\nstderr=%s" % (args, result.stdout, result.stderr))
        return result

    def test_add_list_use_and_reset(self):
        self.run_manager("add", "jessica", "CODEX_HOME=" + str(self.jessica_home))
        self.run_manager("use", "jessica")
        listed = self.run_manager("list").stdout
        self.assertIn("* jessica", listed)
        self.assertIn(str(self.jessica_home), listed)
        state = self.state_home / "config.json"
        self.assertEqual(stat.S_IMODE(state.stat().st_mode), 0o600)

        self.run_manager("reset")
        current = self.run_manager("current").stdout
        self.assertIn("Current: default", current)
        self.assertIn(str(self.default_home), current)

    def test_shim_uses_selected_home_from_any_directory(self):
        self.run_manager("add", "jessica", "CODEX_HOME=" + str(self.jessica_home))
        self.run_manager("use", "jessica")
        result = subprocess.run(
            [str(SHIM), "exec", "hello"],
            cwd=str(self.root),
            env=self.env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CODEX_HOME=%s" % self.jessica_home.resolve(), result.stdout)
        self.assertIn("ARGS=exec hello", result.stdout)

    def test_interactive_alias_adds_no_daemon(self):
        self.run_manager("add", "jessica", "CODEX_HOME=" + str(self.jessica_home))
        self.run_manager("use", "jessica")
        result = subprocess.run(
            [str(SHIM), "hello"],
            cwd=str(self.root),
            env=self.env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ARGS=--no-daemon hello", result.stdout)

    def test_resume_alias_adds_no_daemon(self):
        self.run_manager("add", "jessica", "CODEX_HOME=" + str(self.jessica_home))
        self.run_manager("use", "jessica")
        result = subprocess.run(
            [str(SHIM), "resume", "--last"],
            cwd=str(self.root),
            env=self.env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ARGS=--no-daemon resume --last", result.stdout)

    def test_exec_alias_keeps_subcommand_arguments(self):
        self.run_manager("add", "jessica", "CODEX_HOME=" + str(self.jessica_home))
        self.run_manager("use", "jessica")
        result = subprocess.run(
            [str(SHIM), "exec", "hello"],
            cwd=str(self.root),
            env=self.env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ARGS=exec hello", result.stdout)

    def test_help_has_global_operations(self):
        result = self.run_manager("help")
        for command in ("add", "list", "use", "reset", "help"):
            self.assertIn(command, result.stdout)

    def test_add_requires_existing_directory(self):
        result = self.run_manager(
            "add", "missing", "CODEX_HOME=" + str(self.root / "missing"), check=False
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
