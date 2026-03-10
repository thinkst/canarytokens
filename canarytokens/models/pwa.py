import enum
from typing import List, Literal, Optional

from pydantic import BaseModel
from .common import (
    TokenHistory,
    TokenHit,
    TokenRequest,
    TokenResponse,
    TokenTypes,
)


class PWAType(enum.StrEnum):
    absa = "absa"
    amex = "amex"
    applemail = "applemail"
    applewallet = "applewallet"
    axis = "axis"
    boa = "boa"
    bunq = "bunq"
    capitec = "capitec"
    chase = "chase"
    cred = "cred"
    dashlane = "dashlane"
    discord = "discord"
    facebook = "facebook"
    fnb = "fnb"
    gmail = "gmail"
    googlepay = "googlepay"
    googlewallet = "googlewallet"
    hdfc = "hdfc"
    icici = "icici"
    instagram = "instagram"
    messenger = "messenger"
    monzo = "monzo"
    n26 = "n26"
    nedbank = "nedbank"
    nordpass = "nordpass"
    oldmutual = "oldmutual"
    onepassword = "onepassword"
    paypal = "paypal"
    paytm = "paytm"
    phonepe = "phonepe"
    protonpass = "protonpass"
    rbc = "rbc"
    revolut = "revolut"
    sbi = "sbi"
    signal = "signal"
    snapchat = "snapchat"
    snapscan = "snapscan"
    standard = "standard"
    starling = "starling"
    telegram = "telegram"
    tiktok = "tiktok"
    twitter = "twitter"
    whatsapp = "whatsapp"
    zapper = "zapper"


PWA_APP_TITLES = {
    PWAType.absa: "Absa",
    PWAType.amex: "American Express",
    PWAType.applemail: "Mail",
    PWAType.applewallet: "Wallet",
    PWAType.axis: "Axis Mobile",
    PWAType.boa: "Bank of America",
    PWAType.bunq: "bunq",
    PWAType.capitec: "Capitec",
    PWAType.chase: "Chase",
    PWAType.cred: "CRED",
    PWAType.dashlane: "Dashlane",
    PWAType.discord: "Discord",
    PWAType.facebook: "Facebook",
    PWAType.fnb: "FNB",
    PWAType.gmail: "Gmail",
    PWAType.googlepay: "GPay",
    PWAType.googlewallet: "Wallet",
    PWAType.hdfc: "HDFC Bank",
    PWAType.icici: "iMobile Pay",
    PWAType.instagram: "Instagram",
    PWAType.messenger: "Messenger",
    PWAType.monzo: "Monzo",
    PWAType.n26: "N26",
    PWAType.nedbank: "Nedbank",
    PWAType.nordpass: "NordPass",
    PWAType.oldmutual: "Old Mutual",
    PWAType.onepassword: "1Password",
    PWAType.paypal: "PayPal",
    PWAType.paytm: "Paytm",
    PWAType.phonepe: "PhonePe",
    PWAType.protonpass: "Proton Pass",
    PWAType.rbc: "RBC Mobile",
    PWAType.revolut: "Revolut",
    PWAType.sbi: "YONO SBI",
    PWAType.signal: "Signal",
    PWAType.snapchat: "Snapchat",
    PWAType.snapscan: "SnapScan",
    PWAType.standard: "Standard Bank",
    PWAType.starling: "Starling",
    PWAType.telegram: "Telegram",
    PWAType.tiktok: "TikTok",
    PWAType.twitter: "X",
    PWAType.whatsapp: "WhatsApp",
    PWAType.zapper: "Zapper",
}


class GeolocationCoordinates(BaseModel):
    accuracy: Optional[float]
    altitude: Optional[float]
    altitudeAccuracy: Optional[float]
    heading: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    speed: Optional[float]


class GeolocationPosition(BaseModel):
    coords: Optional[GeolocationCoordinates]
    timestamp: Optional[int]


class PWATokenRequest(TokenRequest):
    token_type: Literal[TokenTypes.PWA] = TokenTypes.PWA
    icon: PWAType
    app_name: Optional[str]


class PWATokenResponse(TokenResponse):
    token_type: Literal[TokenTypes.PWA] = TokenTypes.PWA
    pwa_icon: str
    pwa_app_name: str


class PWATokenHit(TokenHit):
    token_type: Literal[TokenTypes.PWA] = TokenTypes.PWA
    location: Optional[GeolocationPosition]


class PWATokenHistory(TokenHistory[PWATokenHit]):
    token_type: Literal[TokenTypes.PWA] = TokenTypes.PWA
    hits: List[PWATokenHit]
