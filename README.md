# The Horizon 360

Website for **The Horizon 360**, a female student-run newspaper. Live at **horizon360press.com**.

Everything you add here appears on the website within a few minutes. New articles get the Horizon voice audio edition automatically.

## Post an article

1. Open the **articles** folder.
2. Tap **Add file → Create new file**.
3. Name it with dashes and `.txt`, for example `career-in-marine-biology.txt`.
4. Paste this at the top, then fill it in:

```
title: Your headline here
author: Your name
section: Career spotlight
issue: 2026-11
---
Paste the full article here.

Leave a blank line between paragraphs.
```

5. Tap **Commit changes**. The article and its audio appear on the site in about 5 minutes.

Sections you can use: Career spotlight, Women at Work, Interview, Organization partner, Club news, Opinion, Other.

To **fix** an article, open its file, tap the pencil, edit, and commit. The audio is re-recorded automatically.
To **delete** an article, open its file, tap the **⋯** menu, choose **Delete file**, and commit.

## Post a full edition (PDF)

1. Open the **editions** folder.
2. Tap **Add file → Upload files** and choose the PDF.
3. Name it with the year and month first, for example `2026-10 October 2026 Edition.pdf`.
4. Tap **Commit changes**.

## Update the team or contact email

- **team.txt**: one person per line. Add a role after a dash, like `Dorothy - Founder & Editor-in-Chief`.
- **contact.txt**: put the club email after `email:`.

## Add a YouTube video (Watch page)

1. Upload the video to YouTube first.
2. Open the **assets** folder, then **videos.txt**, and tap the pencil.
3. Add the video at the top (newest first), like this:

```
title: Rapid Fire: an ER nurse
series: Rapid Fire
link: https://youtu.be/xxxxxxxxxxx
about: One sentence about the video.
transcript:
Paste the words spoken in the video.
---
```

4. Tap **Commit changes**. Until there's a video, the Watch page shows "Coming soon."
To add a "Visit our channel" button, put `channel: https://www.youtube.com/@yourchannel` on its own block at the top, followed by `---`.

## Add a Women at Work nominee

Ask her first; the page is public. Open **assets/nominees.txt**, tap the pencil, and add:

```
name: Her full name
career: Her job
nominated by: Your name
link:
why: One to three sentences about why we nominated her.
---
```

When her story is out, paste the article or video link after `link:` and her card changes to **Featured**.

## Use your real logo

Upload the image into the **assets** folder and name it `logo.png` (or `logo.jpg`).

## Use your own recording instead of the Horizon voice

Upload an `.mp3` into the **audio** folder with the same name as the article file, for example `career-in-marine-biology.mp3`.

## Check that it worked

Open the **Actions** tab. A green check means the site is updated. A red X means something went wrong; ask for help with a screenshot.
