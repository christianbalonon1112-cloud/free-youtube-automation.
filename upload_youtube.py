import json, os, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN=Path('token.json')
VIDEO=Path('output/kids_short.mp4')
META=Path('output/metadata.json')
if not TOKEN.exists(): raise SystemExit('token.json missing; configure TOKEN_JSON_B64 GitHub secret.')
if not VIDEO.exists() or not META.exists(): raise SystemExit('Generated video or metadata missing.')
creds=Credentials.from_authorized_user_file(str(TOKEN),['https://www.googleapis.com/auth/youtube.upload'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    TOKEN.write_text(creds.to_json(),encoding='utf-8')
metadata=json.loads(META.read_text(encoding='utf-8'))
privacy=os.getenv('YOUTUBE_PRIVACY_STATUS','private').lower()
if privacy not in ('private','unlisted','public'): privacy='private'
body={'snippet':{'title':metadata['title'][:100],'description':metadata['description'][:5000],'tags':metadata['tags'],'categoryId':'1','defaultLanguage':'en'},
      'status':{'privacyStatus':privacy,'selfDeclaredMadeForKids':True}}
youtube=build('youtube','v3',credentials=creds)
request=youtube.videos().insert(part='snippet,status',body=body,media_body=MediaFileUpload(str(VIDEO),mimetype='video/mp4',resumable=True,chunksize=8*1024*1024))
response=None
while response is None:
    status,response=request.next_chunk()
    if status: print(f"Upload progress: {int(status.progress()*100)}%")
print('Upload complete. Video ID:',response.get('id'))
print('Requested privacy:',privacy)
