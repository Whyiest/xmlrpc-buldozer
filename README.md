# 🐍 XML-RPC Buldozer
<br>

Bruteforce WordPress like a buldozer 🚜 — using the power of `system.multicall`. 

<br>
You found an XML-RPC endpoints on WordPress that expose XML-RPC "multicall" endpoints ? Brute force any user with this tool !By abusing the XML-RPC endpoint, this tool can test thousands of passwords per request, making bruteforcing stealthier and faster than traditional HTTP POST login attempts.

<br>

## 🚀 Usage

<br>

```bash
python3 bruteforce.py --user <username> --wordlist <file> [OPTIONS]
```
<br>

### ✅ Basic Example

<br>

```bash
python3 bruteforce.py --user admin --wordlist rockyou.txt
```
<br>

### ✅ Advanced Example

<br>

```bash
python3 bruteforce.py \
  --user admin \
  --wordlist rockyou.txt \
  --url https://target.com/xmlrpc.php \
  --batch 5000 \
  --delay 30 \
  --startfrom 100000 \
  --proxy http://127.0.0.1:8080 \
  --stop-on-success
```
<br>

## 🧩 Arguments

| Option               | Description |
|----------------------|-------------|
| `--user`             | Username to bruteforce (**required**) |
| `--wordlist`         | Path to your password list (**required**) |
| `--url`              | Full URL to the `xmlrpc.php` endpoint (default: `https://target.com/xmlrpc.php`) |
| `--batch`            | Number of passwords to test per request (default: `20`) |
| `--delay`            | Time (in seconds) to wait between batches |
| `--proxy`            | Proxy address (for Burp, ZAP, etc), ex: `http://127.0.0.1:8080` |
| `--startfrom`        | Skip the first X lines of the wordlist |
| `--stop-on-success`  | Stop immediately when a valid password is found |

<br>

## 🔍 What's XML-RPC?

WordPress exposes an API called `XML-RPC` via the endpoint:

```
https://target.com/xmlrpc.php
```

This interface allows external apps to manage the blog remotely (like posting articles, uploading files, retrieving comments, etc).

It supports a special method:

```xml
system.multicall
```

Which allows multiple method calls in a **single XML request** — ideal for bruteforce attacks, since you can craft a single request that tests thousands of passwords (meaning you can often bypass WAFs or rate-limits).

<br>

## 🕵️ How to detect if XML-RPC is enabled?

1. Try a direct POST to `/xmlrpc.php` with minimal content:
```bash
curl -X POST https://target.com/xmlrpc.php -d "<?xml version='1.0'?><methodCall><methodName>demo.sayHello</methodName></methodCall>"
```

2. Use tools like `wpscan`:
```bash
wpscan --url https://target.com --enumerate
```

If you get a response like `XML-RPC seems to be enabled`, you’re good to go 🚀

<br>

## ⚙️ Features

- Bruteforce using `system.multicall`
- Large batch support (e.g. 5000 passwords/request)
- Start from a specific line in the wordlist
- Proxy support (Burp, ZAP, etc)
- Delay between batches
- Automatic escape of XML special characters
- Stop on first success

<br>

## 💡 Tips

- Default `batch` size is 20 — you can go up to 5000+ safely
- Combine with `--startfrom` to resume a previous attack
- Use `--delay` to avoid triggering WAFs or rate-limits
- Add Burp with `--proxy http://127.0.0.1:8080` to inspect each call
- Works great with huge files (14M+ passwords)
- XML escaping is handled automatically, so passwords with `<`, `&`, `"`, etc won't break the XML

<br>

## ⚠️ Legal Disclaimer

This tool is provided for **educational purposes** only.  
Do **NOT** use it on websites you do not own or have explicit permission to test.  
The author is not responsible for any misuse or damage caused.

<br>

## 📦 License

MIT
