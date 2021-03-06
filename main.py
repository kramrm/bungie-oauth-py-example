# main.py


import os
from flask import (
    Flask,
    request,
    redirect,
    session,
    url_for,
)
from oauth import BungieOauth
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = os.environ["BUNGIE_SECRET"]


bungie = BungieOauth(
    client_id=os.environ["BUNGIE_CLIENT"],
    client_secret=os.environ["BUNGIE_SECRET"],
    state=os.environ["BUNGIE_STATE"],
    api_key=os.environ["BUNGIE_KEY"],
)


@app.route("/")
def home_page():
    return "Home page"


@app.route("/login")
@app.route("/login/")
def bungie_login():
    bungie.redirect_uri = f"{request.url_root}/authorized"
    return redirect(bungie.get_login_url())


@app.route("/authorized")
@app.route("/bungie/authorized")
def bungie_authorized():
    code = request.args.get("code")
    # print(f'code: {code}')
    token = bungie.get_access_token(code)
    # print(token)
    if token:
        session["bungie_token"] = token
        me = bungie.get_user(session["bungie_token"])
        session["bungie_type"] = 254
        session["bungie_id"] = str(me["Response"]["bungieNetUser"]["membershipId"])
    redirect_uri = url_for("bungie_user")
    return redirect(redirect_uri)


@app.route("/logout")
def bungie_logout():
    session.pop("bungie_token", None)
    session.pop("bungie_id", None)
    session.pop("bungie_type", None)
    return redirect(url_for("home_page"))


@app.route("/user")
def bungie_user():
    if "bungie_id" in session:
        try:
            me = bungie.get_linked_profiles(
                session["bungie_type"], session["bungie_id"]
            )
        except Exception:
            return redirect(url_for("bungie_login"))
        return me
    else:
        return redirect(url_for("bungie_login"))
