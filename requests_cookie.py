import requests

CONSENT = "YES+shp.gws-20220427-0-RC1.fr+FX+150"
USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
    )

def _request(self):
    # Setting up the request
    session = requests.Session()
    session.headers.update({"User-Agent": self.USER_AGENT})
    consent_cookie = requests.cookies.create_cookie(
        domain=".google.com", name="CONSENT", value=self.CONSENT
    )
    session.cookies.set_cookie(consent_cookie)