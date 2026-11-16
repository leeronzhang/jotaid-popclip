#!/bin/zsh
#
# Jotaid PopClip action — hands the selection to the running app through the
# `jotaid://clip-note` deep link. The app sanitises everything it receives
# (see ExternalClipPayload.swift); this script only has to encode faithfully.
#
# Deliberately depends on nothing but /bin/zsh and three binaries that ship with
# macOS. Perl, Python and Ruby are all "deprecated scripting runtimes" Apple has
# said it will stop shipping, and an extension that breaks on an OS upgrade is
# worse than one that is slightly verbose.

emulate -L zsh
set -euo pipefail

# Hard ceiling for one clipping, in characters. This is NOT the real limit —
# the app enforces its own (AppConfig.Security.maxClipTextLength) and appends an
# ellipsis so the truncation is visible. This one only stops a pathological
# selection (a whole file) from building a URL that overruns the argument list.
readonly MAX_CHARS=40000

# Percent-encodes every byte as %XX.
#
# Encoding *everything* rather than only the reserved characters costs three
# bytes per character but removes every edge case at once: multi-byte UTF-8,
# newlines, `&`, `#`, `%` and whatever the source app puts on the pasteboard all
# take the same path. `od` walks the raw bytes, so no locale setting can change
# the result.
percent_encode() {
  printf '%s' "$1" | /usr/bin/od -An -tx1 -v | /usr/bin/tr -d ' \n' | /usr/bin/sed 's/../%&/g'
}

body="${POPCLIP_TEXT:-}"
# Markdown keeps links and emphasis that plain text would flatten — worth having
# in a Markdown note app. Falls back to plain text whenever the source app does
# not offer rich text (POPCLIP_MARKDOWN is then empty).
if [[ "${POPCLIP_OPTION_KEEPFORMATTING:-1}" == "1" && -n "${POPCLIP_MARKDOWN:-}" ]]; then
  body="${POPCLIP_MARKDOWN}"
fi

if [[ -z "${body//[[:space:]]/}" ]]; then
  echo "Nothing to clip." >&2
  exit 1
fi

if (( ${#body} > MAX_CHARS )); then
  body="${body[1,MAX_CHARS]}"
fi

# Modifier flags are decimal strings from PopClip. Validate before arithmetic;
# an explicit destination remains available for command-line callers.
readonly OPTION_MODIFIER_FLAG=524288
target="${1:-inbox}"
if (( $# == 0 )); then
  modifier_flags="${POPCLIP_MODIFIER_FLAGS:-0}"
  if [[ "$modifier_flags" != <-> || ${#modifier_flags} -gt 7 ]]; then
    echo "Invalid modifier flags." >&2
    exit 1
  fi
  if (( (10#$modifier_flags & OPTION_MODIFIER_FLAG) != 0 )); then
    target="sticky"
  fi
fi
if [[ "$target" != "inbox" && "$target" != "sticky" ]]; then
  echo "Unknown clipping destination." >&2
  exit 1
fi

query="text=$(percent_encode "$body")"

if [[ "${POPCLIP_OPTION_INCLUDESOURCE:-1}" == "1" ]]; then
  # Browser title/URL are only set when the selection came from a browser page;
  # the app name is always there. Each is optional on the app side too.
  if [[ -n "${POPCLIP_BROWSER_TITLE:-}" ]]; then
    query+="&title=$(percent_encode "${POPCLIP_BROWSER_TITLE}")"
  fi
  if [[ -n "${POPCLIP_BROWSER_URL:-}" ]]; then
    query+="&url=$(percent_encode "${POPCLIP_BROWSER_URL}")"
  fi
  if [[ -n "${POPCLIP_APP_NAME:-}" ]]; then
    query+="&app=$(percent_encode "${POPCLIP_APP_NAME}")"
  fi
fi

# Which of the two modes this click asked for. Sent on *every* clipping, not
# only when it changes: the app cannot read PopClip's settings, so a value that
# differs from the last one it saw is its only way of noticing that this option
# was touched — and that is what clears a "Don't ask again" ticked earlier.
#
# An older Jotaid ignores the parameter and saves silently, which is exactly
# what it did before this option existed.
if [[ "$target" == "sticky" ]]; then
  query+="&mode=sticky"
elif [[ "${POPCLIP_OPTION_EDITBEFORESAVING:-0}" == "1" ]]; then
  query+="&mode=ask"
  # Only the editor needs this: Jotaid hands the foreground back to the app you
  # were reading once the window closes. The bundle identifier is exact where
  # the app *name* is ambiguous (two "Preview"s, localised names).
  if [[ -n "${POPCLIP_APP_IDENTIFIER:-}" ]]; then
    query+="&bundle=$(percent_encode "${POPCLIP_APP_IDENTIFIER}")"
  fi
else
  query+="&mode=silent"
fi

# `-g` keeps Jotaid in the background: you clipped something while working
# somewhere else, so stealing focus would defeat the point. If Jotaid is not
# running it launches, still without coming to the front.
#
# The editor mode is the one case where the interruption *is* the point, so it
# skips `-g`: a background app raising its own window is a request the system
# may delay or turn into a bouncing Dock icon, and you would be typing into
# whatever still had focus.
if [[ "$target" == "sticky" || "${POPCLIP_OPTION_EDITBEFORESAVING:-0}" == "1" ]]; then
  /usr/bin/open "jotaid://clip-note?${query}"
else
  /usr/bin/open -g "jotaid://clip-note?${query}"
fi
