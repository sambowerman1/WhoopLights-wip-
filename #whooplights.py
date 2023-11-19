import requests
import webbrowser
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Constants
WHOOP_CLIENT_ID = 'e3f95909-084f-41fc-9e7b-5540bcb6dd2b'
WHOOP_CLIENT_SECRET = '0d99a8d4ec59119582c19ebc5023bcaeb67f1fbedd8f1c6f751ea58dacc14091'
WHOOP_REDIRECT_URI = 'http://localhost:25565/callback'

# Global variable to store the access token
access_token = None

def exchange_code_for_token(code):
    token_url = "https://api.prod.whoop.com/oauth/oauth2/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": WHOOP_CLIENT_ID,
        "client_secret": WHOOP_CLIENT_SECRET,
        "code": code,
        "redirect_uri": WHOOP_REDIRECT_URI
    }
    response = requests.post(token_url, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Failed to retrieve access token")
        return None

def authenticate_with_whoop():
    global access_token

    # Generate a random state value
    state = secrets.token_urlsafe(16)

    # Include the state in the authorization URL
    auth_url = (f"https://api.prod.whoop.com/oauth/oauth2/auth?"
                f"response_type=code&client_id={WHOOP_CLIENT_ID}&"
                f"redirect_uri={WHOOP_REDIRECT_URI}&scope=read:sleep&state={state}")
    webbrowser.open(auth_url)

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            global access_token

            query = urlparse(self.path).query
            query_components = parse_qs(query)
            received_state = query_components.get("state", [""])[0]
            code = query_components.get("code")

            if state != received_state:
                print("Invalid state parameter received.")
                return

            if code:
                code = code[0]
                access_token = exchange_code_for_token(code)
            else:
                print("No code found in the callback URL")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Authentication process completed. You can close this tab.")
            httpd.server_close()

    httpd = HTTPServer(('localhost', 25565), CallbackHandler)
    httpd.handle_request()

def get_sleep_status():
    global access_token

    if access_token:
        # Replace with the actual WHOOP API endpoint to get sleep data
        whoop_api_url = "https://api.prod.whoop.com/some-endpoint"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(whoop_api_url, headers=headers)
        if response.status_code == 200:
            # Process and display the sleep data
            data = response.json()
            print(data)
        else:
            print("Error fetching data from WHOOP")
    else:
        print("No access token available")

def main():
    authenticate_with_whoop()
    get_sleep_status()
    

if __name__ == "__main__":
    main()
