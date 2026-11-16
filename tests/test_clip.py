"""Exercise the real encoder without launching Jotaid."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit


PACKAGE = Path(__file__).resolve().parents[1] / "Jotaid.popclipext"


class ClipTests(unittest.TestCase):
    def run_clip(self, target="inbox", **options):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            recorder = root / "open"
            recorder.write_text('#!/bin/zsh\nprintf "%s\\n" "$@"\n')
            recorder.chmod(0o700)
            script = root / "clip.zsh"
            script.write_text((PACKAGE / "clip.zsh").read_text().replace(
                "/usr/bin/open", str(recorder)))
            (root / "sticky.zsh").write_text((PACKAGE / "sticky.zsh").read_text())
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith("POPCLIP_")}
            env["POPCLIP_TEXT"] = "中文 & #\nselection"
            env.update(options)
            command = ["/bin/zsh", str(root / "sticky.zsh")] if target == "sticky" else [
                "/bin/zsh", str(script), target]
            return subprocess.run(command, env=env, capture_output=True, text=True, check=False)

    def test_sticky_ignores_composer_and_preserves_markdown_source(self):
        result = self.run_clip("sticky", POPCLIP_OPTION_EDITBEFORESAVING="1",
                               POPCLIP_MARKDOWN="**中文 & #**\nselection",
                               POPCLIP_BROWSER_URL="https://example.com/?a=1&b=2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("-g\n", result.stdout)
        url = urlsplit(result.stdout.strip())
        self.assertEqual((url.scheme, url.netloc), ("jotaid", "clip-note"))
        query = parse_qs(url.query)
        self.assertEqual(query["mode"], ["sticky"])
        self.assertEqual(query["text"], ["**中文 & #**\nselection"])
        self.assertEqual(query["url"], ["https://example.com/?a=1&b=2"])

    def test_inbox_remains_background_silent(self):
        result = self.run_clip()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("-g\n"))
        self.assertEqual(parse_qs(urlsplit(result.stdout.splitlines()[-1]).query)["mode"], ["silent"])

    def test_plain_text_without_source(self):
        result = self.run_clip("sticky", POPCLIP_OPTION_KEEPFORMATTING="0",
                               POPCLIP_MARKDOWN="rich", POPCLIP_OPTION_INCLUDESOURCE="0",
                               POPCLIP_BROWSER_URL="https://example.com")
        query = parse_qs(urlsplit(result.stdout.strip()).query)
        self.assertEqual(query["text"], ["中文 & #\nselection"])
        self.assertNotIn("url", query)

    def test_invalid_destination_fails(self):
        self.assertNotEqual(self.run_clip("unknown").returncode, 0)

    def test_blank_selection_fails(self):
        self.assertNotEqual(self.run_clip(POPCLIP_TEXT=" \n ").returncode, 0)


if __name__ == "__main__":
    unittest.main()
