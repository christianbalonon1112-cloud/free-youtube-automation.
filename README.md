# Free YouTube automation starter

This starter generates a simple vertical cartoon-style children's short using Pillow + espeak-ng + FFmpeg, then uploads it through the official YouTube Data API. It is a template-based animation, not AI-generated cinematic animation. It can run on GitHub Actions while your PC is off.

## Important limitations
- Free services do not guarantee unlimited AI generation or exact execution times.
- YouTube API projects that have not passed YouTube's audit can have uploads restricted to private. Do not assume this can publish publicly until your API project is approved/audited.
- Review children's content, copyright, and YouTube's Made for Kids settings. This starter marks videos as Made for Kids.
- Do not commit `token.json`, OAuth client secrets, or credentials to Git.

## Files
- `generate_video.py`: creates a simple 30-second vertical cartoon short.
- `upload_youtube.py`: uploads one video through the official API.
- `oauth_setup.py`: run locally once to authorize your YouTube channel.
- `.github/workflows/daily.yml`: scheduled cloud workflow.

## Setup
1. Create a GitHub repository. For privacy, use a private repository; GitHub Free currently includes a monthly Actions-minute allowance for private repositories. See GitHub's billing documentation.
2. Upload these files to the repository.
3. On your PC, install Python 3.11+ and run `pip install -r requirements.txt`.
4. In Google Cloud Console, create a project, enable YouTube Data API v3, configure OAuth consent, and create an OAuth client ID of type **Desktop app**. Download the client file and save it as `client_secret.json` in this folder.
5. Run `python oauth_setup.py`. A browser opens; sign in to the channel and approve upload access. It creates `token.json` locally.
6. Create a Base64 version of the token file in PowerShell:
   ` [Convert]::ToBase64String([IO.File]::ReadAllBytes('token.json')) | Set-Clipboard `
7. In GitHub repo → Settings → Secrets and variables → Actions → New repository secret, add `TOKEN_JSON_B64` and paste the clipboard contents. Never put it in the code or a public issue.
8. In GitHub repo → Settings → Secrets and variables → Actions, add variable `YOUTUBE_PRIVACY_STATUS` with value `private` initially. Once YouTube has approved/audited the API project for public uploads, you may change it to `public` if you want immediate publication. If you want review first, leave it private.
9. Open Actions, enable workflows, and run **Daily kids short** manually once. Check the job log and the channel's Studio.
10. The schedule is set to 10:00 UTC daily (6:00 PM Philippines time). GitHub cron can be delayed; it is not an exact-time guarantee.

## Local test
Install FFmpeg and espeak-ng on your PC, then run:
`python generate_video.py`
This creates `output/kids_short.mp4` and `output/metadata.json`.

## Troubleshooting
- `TOKEN_JSON_B64` missing/invalid: recreate the secret from the exact local `token.json`, without extra quotes or line breaks.
- `invalid_grant` / token expired: run `python oauth_setup.py` again, then update the secret.
- Upload succeeds but video is private: expected for an unverified/un-audited API project; check YouTube's current API audit requirements.
- `ffmpeg` or `espeak-ng` not found locally: install them and reopen the terminal. GitHub Actions installs them automatically.
- Action did not run at exact time: scheduled GitHub workflows can be delayed; check Actions manually.
- Duplicate upload after retry: inspect YouTube Studio before rerunning. This starter is simple and does not yet maintain a durable upload ledger.
- Poor narration/pronunciation: change the text in `generate_video.py`; espeak-ng voices sound synthetic.
- Copyright: use only original scripts and assets or material whose license explicitly allows your intended use. Avoid recognizable copyrighted characters, songs, and melodies.
