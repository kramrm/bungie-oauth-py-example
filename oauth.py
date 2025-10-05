# discord_auth.py

"""OAuth object models"""

from typing import Optional

import requests


class OAuth:
    """Generic OAuth class to be extended by specific implementations."""

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

    def get_endpoint(self, endpoint, access_token=None, headers: Optional[dict] = None):
        """Generic method to get data from an endpoint."""
        if not headers:
            headers = {}
        url = self.api_url + endpoint
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        data_object = requests.get(url=url, headers=headers, timeout=30)
        data_json = data_object.json()
        return data_json


class BungieOauth(OAuth):
    """Bungie OAuth implementation."""

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
        """Generate the Bungie OAuth login URL."""
        return f"https://www.bungie.net/en/oauth/authorize?client_id={self.client_id}&response_type=code&state={self.state}"

    def get_access_token(self, code):
        """Exchange authorization code for access token."""
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "Content-Type": "application/x-www-form-urlencoded",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        access_token = requests.post(url=self.token_url, data=payload, timeout=30)
        json = access_token.json()
        return json.get("access_token")

    def get_user(self, access_token) -> dict:
        """Get the current user's information."""
        url = self.api_url + "/User/GetMembershipsForCurrentUser/"
        headers = {"Authorization": f"Bearer {access_token}", "X-API-Key": self.api_key}
        user_object = requests.get(url=url, headers=headers, timeout=30)
        user_json = user_object.json()
        return user_json

    def get_linked_profiles(
        self, membership_type, membership_id, access_token=None
    ) -> dict:
        """Get linked profiles for a given user."""
        url = (
            self.api_url
            + f"/Destiny2/{membership_type}/Profile/{membership_id}/LinkedProfiles/"
        )
        headers = {"X-API-Key": self.api_key}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        user_object = requests.get(url=url, headers=headers, timeout=30)
        return user_object.json()
