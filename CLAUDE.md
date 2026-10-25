# video-classroom

Bridge pages on GitHub Pages for SafeShare videos shared in Google Classroom.
SafeShare is behind Cloudflare, which blocks Classroom's link-preview crawler:
a SafeShare link shows up as "Just a moment..." with the Cloudflare challenge as
thumbnail. Each page here carries the real title + thumbnail (Open Graph tags)
and forwards the pupil to SafeShare via JavaScript (no meta refresh, so the
crawler stays on the page and reads the tags).

Language note: `dev/` subproject — code, comments and docs in English, except
`README.md` (Italian, for the user). Conversation stays Italian.

## Layout
```
docs/                 published by GitHub Pages (branch main, folder /docs)
  index.html          list of all pages (rebuilt by the script)
  <slug>/index.html   one bridge page per video
tools/new_page.py     generator: SafeShare URL -> docs/<slug>/index.html
```

## Procedure: the user sends a SafeShare link
1. `python -I dev/video-classroom/tools/new_page.py <url>` (from the workspace root).
   The script reads title and YouTube id from the SafeShare page using a browser
   user agent (Cloudflare lets that through). `--title` overrides the title,
   `--slug` the folder name.
2. Commit (`Add page: <title>`) and push to both remotes (`origin` Forgejo, `github`).
3. Give back the URL `https://teacheratwork.github.io/video-classroom/<slug>/`.
   Pages takes ~1 minute to publish after the push.

## Remotes
- `origin` → `forgejo:samuele/video-classroom.git` (backup of the history)
- `github` → `https://github.com/teacheratwork/video-classroom.git` (public, Pages)

## Status
Set up 2026-10-25. First real test on Classroom pending: check that the card
shows title and thumbnail, and that Classroom's fetcher does not follow the JS
redirect. Support request to SafeShare (whitelist Google's fetcher) sent the same
day via their web form — if they fix it, this project becomes unnecessary.
