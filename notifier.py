"""
Sends a push notification for each new listing found.

Default: ntfy.sh — free, no signup, no API keys.
  1. Install the "ntfy" app on your phone (iOS/Android).
  2. Pick a unique topic name (e.g. "chris-sf-rentals-8k2j") and subscribe
     to it in the app. Anyone who knows the topic name can see your
     notifications, so make it hard to guess.
  3. Put that name in NTFY_TOPIC below (or set env var NTFY_TOPIC).

If you'd rather get real SMS texts, see the commented Twilio block at
the bottom — needs a Twilio account + phone number (not free).
"""
import os
import requests

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "changeme-pick-a-unique-topic")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"


def send_notification(title: str, message: str, url: str | None = None):
    headers = {"Title": title}
    if url:
        headers["Click"] = url
    try:
        requests.post(NTFY_URL, data=message.encode("utf-8"), headers=headers, timeout=10)
    except requests.RequestException as e:
        print(f"[notifier] failed to send push notification: {e}")


def notify_new_listings(site: str, new_listings: list[dict]):
    if not new_listings:
        return
    for listing in new_listings:
        addr = listing.get("address", "New listing")
        unit = listing.get("unit")
        price = listing.get("price", "")
        title = f"{site}: new listing"
        message = f"{addr}" + (f" #{unit}" if unit else "") + f" — {price}"
        send_notification(title, message, url=listing.get("url"))


# --- Optional: real SMS via Twilio instead of / in addition to ntfy ---
# pip install twilio
# from twilio.rest import Client
# TWILIO_SID = os.environ["TWILIO_SID"]
# TWILIO_AUTH = os.environ["TWILIO_AUTH"]
# TWILIO_FROM = os.environ["TWILIO_FROM"]   # your Twilio number
# TWILIO_TO = os.environ["TWILIO_TO"]       # your cell number
#
# def send_sms(body: str):
#     client = Client(TWILIO_SID, TWILIO_AUTH)
#     client.messages.create(body=body, from_=TWILIO_FROM, to=TWILIO_TO)
