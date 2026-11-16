# Jotaid × PopClip

A [PopClip](https://www.popclip.app) extension that saves the selected text to your
[Jotaid](https://jotaid.com) Inbox, with the page title, link, source app and capture time
recorded underneath it. Choose **Sticky Jot** to open the new note on your desktop.

**→ [Full documentation](Jotaid.popclipext/readme.md)** — options, privacy, the deep link
behind it, and troubleshooting.

That file lives inside the package because the PopClip Extensions Directory reads it from
there; this one is for people arriving on GitHub. Keeping it short is deliberate — one of the
two has to be the copy that gets updated, and it is the one in the package.

## Layout

```
Jotaid.popclipext/       the extension itself
├── Config.yaml          name, options, the action
├── clip.zsh             builds a jotaid:// link and opens it
├── sticky.zsh           invokes the shared encoder for Sticky Jot
├── jotaid.svg           monochrome bar icon
├── readme.md            shown on the directory page
└── demo.mp4             looping demo on the directory page
popclip-directory.yaml   tells the directory bot where the package is
LICENSE                  Apache-2.0
```

## Installing without the directory

Download or clone, then double-click `Jotaid.popclipext`. macOS will warn that the extension
contains executable code — it does: `clip.zsh`, which is short enough to read in a minute.
The signed copy from the [PopClip Extensions Directory](https://www.popclip.app/extensions/)
does not carry that warning.
