"""Exercise the real encoder without launching Jotaid."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit


PACKAGE = Path(__file__).resolve().parents[1] / "Jotaid.popclipext"


class ClipTests(unittest.TestCase):
    def run_clip(self, target=None, **options):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            recorder = root / "open"
            recorder.write_text('#!/bin/zsh\nprintf "%s\\n" "$@"\n')
            recorder.chmod(0o700)
            script = root / "clip.zsh"
            script.write_text((PACKAGE / "clip.zsh").read_text().replace(
                "/usr/bin/open", str(recorder)))
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith("POPCLIP_")}
            env["POPCLIP_TEXT"] = "中文 & #\nselection"
            env.update(options)
            command = ["/bin/zsh", str(script)]
            if target is not None:
                command.append(target)
            return subprocess.run(command, env=env, capture_output=True, text=True, check=False)

    def test_sticky_ignores_composer_and_preserves_markdown_source(self):
        result = self.run_clip(POPCLIP_MODIFIER_FLAGS="524288", POPCLIP_OPTION_EDITBEFORESAVING="1",
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
        result = self.run_clip(POPCLIP_MODIFIER_FLAGS="524288", POPCLIP_OPTION_KEEPFORMATTING="0",
                               POPCLIP_MARKDOWN="rich", POPCLIP_OPTION_INCLUDESOURCE="0",
                               POPCLIP_BROWSER_URL="https://example.com")
        query = parse_qs(urlsplit(result.stdout.strip()).query)
        self.assertEqual(query["text"], ["中文 & #\nselection"])
        self.assertNotIn("url", query)

    def test_option_combined_with_other_modifiers_still_opens_sticky(self):
        for flags in ("524288", "655360", "786432", "917504", "1572864", "1703936", "1835008", "1966080"):
            with self.subTest(flags=flags):
                result = self.run_clip(POPCLIP_MODIFIER_FLAGS=flags)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse(result.stdout.startswith("-g\n"))
                self.assertEqual(parse_qs(urlsplit(result.stdout.strip()).query)["mode"], ["sticky"])

    def test_other_modifiers_keep_inbox_destination(self):
        for flags in ("0", "131072", "262144", "1048576"):
            with self.subTest(flags=flags):
                result = self.run_clip(POPCLIP_MODIFIER_FLAGS=flags)
                self.assertTrue(result.stdout.startswith("-g\n"))
                self.assertEqual(parse_qs(urlsplit(result.stdout.splitlines()[-1]).query)["mode"], ["silent"])

    def test_inbox_still_honors_edit_before_saving(self):
        result = self.run_clip(POPCLIP_OPTION_EDITBEFORESAVING="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(result.stdout.startswith("-g\n"))
        self.assertEqual(parse_qs(urlsplit(result.stdout.strip()).query)["mode"], ["ask"])

    def test_invalid_modifier_flags_fail_without_opening(self):
        for flags in ("-1", "x", "1+524288", "12345678"):
            with self.subTest(flags=flags):
                result = self.run_clip(POPCLIP_MODIFIER_FLAGS=flags)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")

    def test_each_editing_preference_has_one_icon_with_both_gestures_in_tooltip(self):
        result = subprocess.run(
            ["ruby", "-rjson", "-ryaml", "-e", "puts JSON.generate(YAML.load_file(ARGV[0]))",
             str(PACKAGE / "Config.yaml")], capture_output=True, text=True, check=True)
        config = json.loads(result.stdout)
        self.assertEqual(config["icon"], "jotaid.svg")
        for edit in ("0", "1"):
            visible = [action for action in config["actions"]
                       if all(not item.startswith("option-editbeforesaving=") or item.endswith("=" + edit)
                              for item in action["requirements"])]
            self.assertEqual(len(visible), 1)
            action = visible[0]
            self.assertEqual(action["shell script file"], "clip.zsh")
            for language in ("en", "zh-hans", "zh-hant"):
                title = action["title"][language]
                for label in ("Jotaid", "Inbox", "⌥", "Option", "Sticky Jot"):
                    self.assertIn(label, title)

    def test_invalid_destination_fails(self):
        self.assertNotEqual(self.run_clip("unknown").returncode, 0)

    def test_blank_selection_fails(self):
        self.assertNotEqual(self.run_clip(POPCLIP_TEXT=" \n ").returncode, 0)


if __name__ == "__main__":
    unittest.main()
