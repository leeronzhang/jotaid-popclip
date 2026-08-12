# Jotaid × PopClip

Select text anywhere on macOS, click **Jotaid** in the [PopClip](https://www.popclip.app) bar,
and the selection lands in your Jotaid **Inbox** — with the page title, link, source app and
capture time recorded underneath it.

```markdown
The part you selected, kept verbatim.

---

> Source: Safari · [The page title](https://example.com/post)
> Clipped Aug 12, 2026 at 2:30 PM
```

Every clipping is tagged `clipping`, so the whole collection is one filter away in the note list.

## Install

1. Double-click `Jotaid.popclipext`. PopClip installs it.
2. macOS will warn that the extension contains executable code — it does: a shell script that
   builds a `jotaid://` link and opens it. The script is `clip.zsh`, right next to this file,
   and it is short enough to read in a minute.

Jotaid does **not** need to be running: the link launches it in the background if necessary.

## Settings

Both live in PopClip → Extensions → Jotaid.

| Option | Default | What it does |
| --- | --- | --- |
| Keep formatting | on | Sends Markdown when the source app offers rich text, so links and emphasis survive. Off = always plain text. |
| Include source | on | Adds the page title, link and app name to the footnote. Off = the selection alone. |

## How it behaves

- **Nothing comes to the front.** The clipping is saved in the background; you stay in whatever
  app you were reading. The tick in the PopClip bar is your confirmation.
- **Only `https:` source links are kept.** The footnote renders the source as a clickable link,
  and a link that cannot be opened safely is worse than no link at all. A page on plain `http:`
  still contributes its title and app name.
- **Long selections are truncated**, with an ellipsis marking where. The limit is
  `AppConfig.Security.maxClipTextLength` (20 000 characters) on the app side.

## The link behind it

The extension is a thin wrapper over a deep link that anything can call — Shortcuts, Raycast,
Alfred, a cron job:

```
jotaid://clip-note?text=<required>&title=<optional>&url=<optional>&app=<optional>
```

All values are percent-encoded. The app treats every field as untrusted: it strips control
characters, collapses metadata to a single line, caps lengths and drops any source URL that
is not a safely openable `https:` address. A missing or empty `text` means the link is ignored.

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
