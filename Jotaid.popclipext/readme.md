# Jotaid

Select text anywhere on macOS, click **Jotaid** in the PopClip bar, and the selection lands in
your Jotaid **Inbox** — with the page title, link, source app and capture time recorded
underneath it.

```markdown
The part you selected, kept verbatim.

---

> Source: Safari · [The page title](https://example.com/post)
> Clipped Aug 12, 2026 at 2:30 PM
```

Every clipping is tagged `clipping`, so the whole collection is one filter away in the note list.

Requires [Jotaid](https://jotaid.com) 1.1.3 or later — a Markdown notes app for macOS with
backlinks, a knowledge graph and a co-occurrence matrix. The app does **not** need to be
running: the clipping launches it in the background if necessary.

## Options

In PopClip → Extensions → Jotaid.

| Option | Default | What it does |
| --- | --- | --- |
| Keep formatting | on | Sends Markdown when the source app offers rich text, so links and emphasis survive. Off = always plain text. |
| Include source | on | Adds the page title, link and app name to the footnote. Off = the selection alone. |
| Edit before saving | off | Opens a small window in Jotaid so you can fix up the clipping first. Off = saved straight to the Inbox. Needs Jotaid 1.1.4. |

## Edit before saving

*Needs Jotaid 1.1.4 or later. On 1.1.3 the option is simply ignored and the clipping is saved
silently, as it always was — nothing breaks, the window just does not appear.*

With the option on, clicking **Jotaid** opens a window holding the selection. Edit it, then
**Save** (or ⌘⏎) files it in the Inbox; **Cancel** (or Esc) throws it away. Either way the
foreground goes back to the app you were reading.

The window only carries the selection. The source line and the timestamp are added underneath
when it is saved — they are not in the editing area, where they would be deleted by accident.

Ticking **Don't ask again** in that window switches back to silent saving without going through
the settings. To bring the window back, turn **Edit before saving** off and on again here in
PopClip: Jotaid cannot read PopClip's settings, so a changed value is how it learns you have
made up your mind again. That is the whole of it — there is no third switch hidden in Jotaid's
own settings.

## How it behaves

- **Nothing comes to the front** — unless you asked it to, above. The clipping is saved in the
  background; you stay in whatever app you were reading. The tick in the PopClip bar is your
  confirmation.
- **Only `https:` source links are kept.** The footnote renders the source as a clickable link,
  and a link that cannot be opened safely is worse than no link at all. A page on plain `http:`
  still contributes its title and app name.
- **Long selections are truncated**, with an ellipsis marking where, at 20 000 characters.

## Privacy

The selected text goes to one place: the copy of Jotaid installed on this Mac, over its
`jotaid://` URL scheme. **Nothing is sent over the network, and no third party is involved** —
neither by this extension nor by Jotaid when it stores the clipping.

The script it runs (`clip.zsh`, about seventy lines) percent-encodes the selection, appends the
page title, page URL and app name that PopClip provides, and hands the result to `open`. It
shells out to nothing but `od`, `tr`, `sed` and `open`, all of which ship with macOS.

The source app's bundle identifier is sent along **only** when *Edit before saving* is on, and
is used for exactly one thing: giving that app the foreground back once the window closes. It
never reaches the note.

## The link behind it

The extension is a thin wrapper over a deep link that anything can call — Shortcuts, Raycast,
Alfred, a cron job:

```
jotaid://clip-note?text=<required>&title=&url=&app=&bundle=&mode=silent|ask
```

All values are percent-encoded. The app treats every field as untrusted: it strips control
characters, collapses metadata to a single line, caps lengths and drops any source URL that is
not a safely openable `https:` address. A missing or empty `text` means the link is ignored.

`mode` picks between saving silently and opening the editor; anything missing or unrecognised
means `silent`. `bundle` is the source app's bundle identifier, described above — a value
outside `[A-Za-z0-9.-]` is dropped rather than trimmed, since a truncated identifier names a
*different* app.

## Troubleshooting

**Nothing appears in Jotaid.** Check that the link opens at all:

```sh
open -g "jotaid://clip-note?text=hello"
```

A note titled `hello` should appear in the Inbox. If it does not, macOS may have registered a
different build of Jotaid for the `jotaid://` scheme — launch the copy you actually use once,
then retry.

**The PopClip bar shows a cross.** The script failed. Run it by hand to see why:

```sh
POPCLIP_TEXT="hello" POPCLIP_APP_NAME="Terminal" zsh Jotaid.popclipext/clip.zsh
```

**The Jotaid action never appears in the bar.** The extension hides itself when Jotaid is not
installed. Install the app, then select some text again.

## Changelog

**1.0** — First release: clipping to the Inbox with source and capture time, silently or
through the editing window.

## Send to Sticky Jot

Hold **⌥ Option** and click the **Jotaid** icon to save a new note in Inbox and open it as a desktop sticky
note. Each click creates a separate note. Keep formatting and Include source
apply to both destinations; Edit before saving applies only to a normal Inbox click.
Hover over the single Jotaid icon to see both gestures in its tooltip (English,
Simplified Chinese or Traditional Chinese, following your preferred language).
This action requires a Jotaid version supporting `jotaid://clip-note?mode=sticky`;
older versions save to Inbox silently instead of opening a sticky note.
