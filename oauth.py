# discord_auth.py

import requests
import base64
from urllib.parse import quote_plus


class OAuth:
    def __init__(
        self,
        client_id,
        client_secret,
        state,
        scope,
        redirect_uri,
        token_url,
        api_url,
        api_key,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.state = state
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.token_url = token_url
        self.api_url = api_url
        self.api_key = api_key

    def get_endpoint(self, endpoint, access_token=None, headers: dict = {}):
        url = self.api_url + endpoint
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        data_object = requests.get(url=url, headers=headers)
        data_json = data_object.json()
        return data_json


class BungieOauth(OAuth):
    def __init__(self, client_id, client_secret, state, api_key) -> None:
        OAuth.__init__(
            self,
            client_id=client_id,
            client_secret=client_secret,
            state=state,
            scope=None,
            redirect_uri=None,
            token_url="https://www.bungie.net/platform/app/oauth/token",
            api_url="https://www.bungie.net/Platform",
            api_key=api_key,
        )

    def get_login_url(self) -> str:
        return f"https://www.bungie.net/en/oauth/authorize?client_id={self.client_id}&response_type=code&state={self.state}"

    def get_access_token(self, code):
        payload = {
            "grant_type": "authorization_code",
            "code": code,
        }
        auth_string = str(
            base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("ascii")),
            "utf-8",
        )
        print(f"auth_string: {auth_string}")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_string}",
        }

        access_token = requests.post(url=self.token_url, data=payload, headers=headers)
        print(f"{access_token}")
        json = access_token.json()
        return json.get("access_token")

    def get_user(self, access_token) -> dict:
        url = self.api_url + "/User/GetMembershipsForCurrentUser/"
        headers = {"Authorization": f"Bearer {access_token}", "X-API-Key": self.api_key}
        user_object = requests.get(url=url, headers=headers)
        user_json = user_object.json()
        return user_json

    def get_linked_profiles(
        self, membershipType, membershipId, access_token=None
    ) -> dict:
        url = (
            self.api_url
            + f"/Destiny2/{membershipType}/Profile/{membershipId}/LinkedProfiles/"
        )
        headers = {"X-API-Key": self.api_key}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        user_object = requests.get(url=url, headers=headers)
        return user_object.json()
