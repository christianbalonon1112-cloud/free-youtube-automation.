from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

if __name__ == "__main__":
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    credentials = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    with open("token.json", "w", encoding="utf-8") as f:
        f.write(credentials.to_json())
    print("Saved token.json. Keep it private; add its Base64 contents as GitHub secret TOKEN_JSON_B64.")
