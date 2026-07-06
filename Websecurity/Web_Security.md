# WEB SECURITY — БҮРЭН ГҮНЗГИЙ СУРГАЛТЫН МАТЕРИАЛ ⭐⭐⭐⭐⭐

---

## АГУУЛГА
1. HTTP суурь
2. Cookies
3. Sessions
4. JWT
5. OAuth
6. CORS
7. CSP
8. XSS
9. CSRF
10. SQLi
11. SSRF
12. RCE
13. XXE
14. SSTI
15. Cheat Sheet (нэгтгэсэн)

---

## 1. HTTP СУУРЬ

HTTP бол stateless (төлөвгүй) протокол — сервер таны өмнөх хүсэлтийг санахгүй. Тиймээс cookie/session/token хэрэгтэй болдог.

**Request бүтэц:**
```
GET /profile HTTP/1.1
Host: example.com
Cookie: session=abc123
Authorization: Bearer eyJhbGc...
User-Agent: Mozilla/5.0
```

**Аюулгүй байдлын чухал header-ууд:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains   # зөвхөн HTTPS ашиглахыг албадана
X-Content-Type-Options: nosniff                                  # MIME sniffing хориглоно
X-Frame-Options: DENY                                             # clickjacking-аас хамгаална
Content-Security-Policy: default-src 'self'                       # доор дэлгэрэнгүй
```

---

## 2. COOKIES

Cookie бол клиент талд хадгалагдаж, request бүрт автоматаар серверт илгээгддэг жижиг өгөгдөл.

```
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict; Path=/
```

| Flag | Юу хийдэг | Яагаад чухал |
|---|---|---|
| `HttpOnly` | JavaScript-ээр (`document.cookie`) уншиж болохгүй болгоно | XSS-ээр cookie хулгайлахаас хамгаална |
| `Secure` | Зөвхөн HTTPS дээр илгээгдэнэ | HTTP дээр plaintext дамжихаас сэргийлнэ |
| `SameSite=Strict/Lax/None` | Cross-site request-д cookie дагуулан илгээх эсэхийг тохируулна | CSRF-ээс хамгаалах гол механизм |

**Түгээмэл алдаа:** `HttpOnly` тавихгүй байх → энэ нэг мөрөөр XSS attack cookie хулгайлах чадвартай болно.

---

## 3. SESSIONS

**Session-based auth ажиллах зарчим:**
```
1. Хэрэглэгч нэвтэрнэ → сервер session ID үүсгэж, серверийн санах ойд (Redis/DB) хадгална
2. Session ID-г cookie-оор клиентэд илгээнэ
3. Дараагийн request бүрт клиент энэ cookie-г дагуулан илгээнэ
4. Сервер session ID-гээр хэн нэвтэрсэн болохыг шалгана
```

**Аюулгүй байдлын асуудлууд:**
- **Session Fixation:** attacker өөрийн мэддэг session ID-г victim-д "тогтоож", дараа нь victim нэвтэрсний дараа тэр session ID-гээр victim-ийн эрхээр орох. **Хамгаалалт:** нэвтрэх бүрт шинэ session ID үүсгэх (`session.regenerate()`).
- **Session Hijacking:** cookie хулгайлж авсны дараа тэр session ID-г ашиглан хэн нэгний нэрээр орох. **Хамгаалалт:** `HttpOnly`, `Secure`, IP/User-Agent binding, богино хугацаанд дуусгах.
- **Session ID таамаглах боломжтой байх:** сул random generator ашигласан бол session ID-г таамаглаж болно. **Хамгаалалт:** криптографийн хувьд аюулгүй random (`secrets` module Python-д).

---

## 4. JWT (JSON Web Token)

**Бүтэц:** `header.payload.signature` (base64url encoded, тусдаа цэгээр холбогдоно)

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWRtaW4ifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Header:** `{"alg":"HS256","typ":"JWT"}`
**Payload:** `{"user":"admin","exp":1234567890}`
**Signature:** header+payload-ийг secret key-ээр hash хийсэн — **өгөгдлийг encrypt хийдэггүй, зөвхөн sign хийдэг** (base64 бол хэн ч decode хийж уншиж чадна!)

**Түгээмэл эмзэг байдлууд:**
1. **`alg: none` attack** — attacker header-ийг `{"alg":"none"}` болгож, signature-ийг хоослож илгээнэ. Сул серверүүд үүнийг зөвшөөрдөг байсан. **Хамгаалалт:** сервер талд зөвхөн зөвшөөрөгдсөн algorithm-уудыг (whitelist) хатуу шалгах.
2. **Algorithm confusion (RS256 → HS256)** — сервер RS256 (asymmetric) ашигладаг байхад, attacker HS256 (symmetric) руу солиод, олон нийтэд нээлттэй **public key**-г HS256-ийн secret мэт ашиглаж fake signature үүсгэнэ. **Хамгаалалт:** algorithm-ыг серверийн код дотор хатуу зааж өгөх, client-ээс дамжуулсан header-т итгэхгүй байх.
3. **Сул secret key** — `hashcat -m 16500` ашиглан HS256 JWT-ийн secret-ийг brute-force хийж болно (dictionary attack).
4. **`exp` claim байхгүй/шалгагдаагүй** — token хэзээ ч дуусахгүй, хулгайлагдвал мөнхөд хүчинтэй.

**Хамгаалалтын жагсаалт:**
```
□ Algorithm-ыг server-side хатуу тогтоо, client header-т бүү итгэ
□ Хүчтэй, урт secret ашигла (256-bit+)
□ exp (expiry) заавал оруул, богино хугацаатай байлга
□ Sensitive өгөгдлийг payload-д бүү хадгал (зөвхөн sign хийгддэг, encrypt биш!)
□ Refresh token-ыг HttpOnly cookie-д хадгал, access token-ыг memory-д
```

---

## 5. OAUTH 2.0

OAuth бол **зөвшөөрлийн (authorization)** протокол — "Google-ээр нэвтрэх" гэх мэт. Anхаар: OAuth нь **authentication биш**, харин OpenID Connect (OAuth дээр суурилсан) нь authentication хийдэг.

**Authorization Code Flow (хамгийн түгээмэл, аюулгүй):**
```
1. App → хэрэглэгчийг Google-ийн зөвшөөрлийн хуудас руу чиглүүлнэ (redirect_uri, client_id, scope дамжуулна)
2. Хэрэглэгч зөвшөөрнө
3. Google → App-ийн redirect_uri руу authorization code илгээнэ
4. App (backend-ээс!) энэ code-ыг client_secret-тэй хамт Google руу илгээж access token авна
5. App энэ token-оор Google API-с хэрэглэгчийн мэдээлэл авна
```

**Түгээмэл эмзэг байдлууд:**
1. **Open Redirect via `redirect_uri`** — хэрэв сервер `redirect_uri`-г validate хийхгүй бол, attacker өөрийн domain руу code/token дамжуулж хулгайлж болно. **Хамгаалалт:** `redirect_uri`-г exact-match whitelist-ээр шалгах (wildcard subdomain ашиглахгүй байх).
2. **CSRF via missing `state` parameter** — `state` параметр байхгүй бол, attacker өөрийн OAuth flow-г victim дээр force хийж, victim-ийн акаунтыг attacker-ийн акаунттай "холбож" болно (account linking attack). **Хамгаалалт:** санамсаргүй, session-тэй холбоотой `state` утга ашиглаж, буцаж ирэхэд шалгах.
3. **Implicit flow ашиглах (хуучирсан)** — access token URL fragment-ээр шууд browser руу ирдэг тул browser history, referrer header-ээр алдагдах эрсдэлтэй. **Одоо Authorization Code + PKCE ашиглахыг зөвлөдөг.**
4. **PKCE байхгүй байх (mobile/SPA-д)** — client_secret хадгалж чадахгүй апп (mobile, SPA)-д code interception attack-аас хамгаалахын тулд PKCE (Proof Key for Code Exchange) заавал хэрэгтэй.

---

## 6. CORS (Cross-Origin Resource Sharing)

Browser-ийн **Same-Origin Policy**-г зөвхөн зөвшөөрөгдсөн domain-уудад тайлж өгдөг механизм.

```
Access-Control-Allow-Origin: https://trusted-app.com
Access-Control-Allow-Credentials: true
```

**Түгээмэл алдаа — АЮУЛТАЙ ТОХИРГОО:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true    # ЭНЭ ХОЁРЫГ ХАМТАД НЬ АШИГЛАХ БОЛОМЖГҮЙ (browser блоклоно) —
                                            # гэхдээ зарим сервер Origin header-ийг "reflect" хийж, wildcard-ийн оронд
                                            # ирсэн Origin-ийг шууд буцаадаг — энэ нь бодит байдал дээр wildcard шиг аюултай
```
Хэрэв сервер `Origin` header-ийг шалгалгүйгээр шууд `Access-Control-Allow-Origin`-д reflect хийвэл, **ямар ч сайт** энэ API руу хандаж, cookie/credential-тай хамт хүсэлт илгээж болно — өөрөөр хэлбэл CSRF-ийн CORS хувилбар.

**Хамгаалалт:**
```
□ Origin-ыг тодорхой whitelist-тэй харьцуулж шалга (regex биш, exact match)
□ Credentials шаардлагагүй бол Access-Control-Allow-Credentials-ыг бүү тавь
□ Wildcard (*)-ийг Credentials-тай хэзээ ч бүү хослуул
```

---

## 7. CSP (Content Security Policy)

CSP бол browser-д "ямар эх сурвалжаас script/style/image ачаалж болохыг" зааж өгдөг header — **XSS-ийн нөлөөг багасгах гол механизм**.

```
Content-Security-Policy: default-src 'self'; script-src 'self' https://cdn.trusted.com; object-src 'none'; base-uri 'self'
```

| Directive | Тайлбар |
|---|---|
| `default-src 'self'` | Default-аар зөвхөн өөрийн domain-аас л resource ачаалах |
| `script-src` | Script хаанаас ажиллаж болохыг хязгаарлана — `'unsafe-inline'` ашиглавал CSP-ийн XSS хамгаалалт бараг үгүй болно |
| `object-src 'none'` | Flash/plugin-ийг бүрэн хориглоно |
| `base-uri 'self'` | `<base>` tag ашиглан relative URL хийх attack-аас хамгаална |

**CSP bypass жишээ:** хэрэв `script-src 'self' https://*.cdn.com` гэж хэт өргөн зөвшөөрсөн бол, attacker CDN дээрх аль нэг JSONP endpoint-ыг ашиглан script inject хийж болно. **CSP-ийг хэтэрхий уян хатан бичих нь хамгаалалтыг сулруулна.**

---

## 8. XSS (Cross-Site Scripting)

### Төрлүүд
- **Reflected XSS** — payload URL параметрт байгаад, серверийн хариунд шууд тусгагдана (victim-д тусгайлан бэлдсэн холбоос илгээх шаардлагатай)
- **Stored XSS** — payload өгөгдлийн санд хадгалагдаад, дараа нь бусад хэрэглэгчид харагдана (жишээ: сэтгэгдэл, форум пост) — **хамгийн аюултай**, учир нь олон хэрэглэгчид автоматаар нөлөөлнө
- **DOM-based XSS** — сервер хамаагүй, зөвхөн клиент талын JavaScript (`innerHTML`, `document.write`, `location.hash`) дотор эх сурвалж шалгагдалгүй ашиглагдана

### Payload жишээнүүд (тест хийхэд)
```html
<script>alert(document.cookie)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
"><script>alert(1)</script>
```

### Илрүүлэх арга
- Input бүрт HTML/JS meta-тэмдэгт (`<`, `>`, `"`, `'`) оруулж, хариунд escape хийгдэж байгаа эсэхийг шалгах
- Burp Suite/OWASP ZAP-ээр автоматжуулсан scan хийх

### Хамгаалалт (гол механизмууд)
```
□ Output encoding — HTML context-д гарч буй бүх user input-ыг context-specific encode хийх
  (HTML entity encode, JS string encode, URL encode — байрлалаас хамаарна)
□ Framework-ийн default escaping-ыг бүү унтраа (React/Vue/Angular default-аар escape хийдэг —
  dangerouslySetInnerHTML, v-html гэх мэт функцийг болгоомжтой ашигла)
□ CSP header нэмэлт давхар хамгаалалт болгож ашигла
□ HttpOnly cookie — XSS амжилттай болсон ч ядаж session cookie хулгайлагдахгүй
□ Input validation (whitelist) — гэхдээ энэ ганцаараа хангалтгүй, output encoding заавал хэрэгтэй
```

---

## 9. CSRF (Cross-Site Request Forgery)

Хэрэглэгч нэвтэрсэн session-тойгоо (browser cookie автоматаар илгээдэг тул) мэдэлгүй хортой сайтын шаардсан үйлдлийг өөрийн эрхээр гүйцэтгүүлэх attack.

**PoC жишээ:**
```html
<form action="https://bank.com/transfer" method="POST" id="f">
  <input name="to" value="attacker-account">
  <input name="amount" value="10000">
</form>
<script>document.getElementById('f').submit()</script>
```
Victim энэ хуудсыг зочилмогц, browser нь bank.com-ийн cookie-г **автоматаар** дагуулан илгээдэг тул сервер энэ хүсэлтийг хууль ёсны victim-ийн хүсэлт мэт хүлээж авна.

### Хамгаалалт
```
□ CSRF Token — session бүрт өвөрмөц, таамаглах боломжгүй token үүсгэж, form/AJAX бүрт шалгах
□ SameSite=Strict/Lax cookie — cross-site request-д cookie огт илгээгдэхгүй болгоно (орчин үеийн гол хамгаалалт)
□ Double Submit Cookie pattern — token-ыг cookie болон request body/header-т хоёуланд нь илгээж таарч байгаа эсэхийг шалгах
□ Custom header шаардах (жишээ: X-Requested-With) — энгийн HTML form-оор дуурайлган үүсгэх боломжгүй
□ State-changing үйлдэлд GET биш зөвхөн POST/PUT/DELETE ашигла
```

---

## 10. SQL INJECTION (SQLi)

### Илрүүлэх
```
' (ганц quote) → error эсвэл хариу өөрчлөгдвөл шинжлэх шинж тэмдэг
' OR SLEEP(5)-- -   → хариу 5 секунд саатвал time-based blind SQLi
```

### Union-based
```sql
' ORDER BY 10-- -                                    -- багана тоог олох
' UNION SELECT null,username,password FROM users-- -  -- өгөгдөл гаргаж авах
```

### Blind (boolean/time-based)
```sql
' AND 1=1-- -     -- true үед хариу хэвийн
' AND 1=2-- -     -- false үед хариу өөр/хоосон
' AND IF(1=1,SLEEP(5),0)-- -
```

### Хамгаалалт (гол механизм)
```
□ Parameterized Queries / Prepared Statements — ЯГ Л ЦОРЫН ГАНЦ найдвартай хамгаалалт
  (Python: cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,)))
□ ORM ашиглах (SQLAlchemy, Django ORM) — гэхдээ raw SQL query бичихээс болгоомжлох
□ Least privilege — DB user-д зөвхөн шаардлагатай эрх өгөх (жишээ: SELECT-only account тайлан гаргах хэсэгт)
□ Input validation нэмэлт давхарга болгож ашиглах (гэхдээ ганцаараа хангалтгүй)
□ WAF нэмэлт давхарга (гэхдээ bypass хийгддэг тул гол хамгаалалт биш)
```
**Чухал ойлголт:** string concatenation-аар query бүтээх нь SQLi-ийн үндсэн шалтгаан. Parameterized query ашигласнаар user input **хэзээ ч SQL код болж хувирахгүй**, зөвхөн өгөгдөл гэж тооцогдоно.

---

## 11. SSRF (Server-Side Request Forgery)

Attacker сервер өөрөө дотоод/гадаад руу хүсэлт илгээхийг өдөөж, ердөө хандах эрхгүй байх ёстой дотоод resource-д хандах attack.

```
?url=http://127.0.0.1/admin
?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/   # Cloud metadata endpoint (AWS)
?url=file:///etc/passwd
```

**Filter bypass арга:**
```
http://127.0.0.1.nip.io      # DNS rebinding-той төстэй
http://0177.0.0.1            # octal encoding
http://2130706433            # decimal IP (127.0.0.1)-тэй тэнцүү
Redirect chain ашиглах (allowed domain → 302 redirect → internal IP)
```

### Хамгаалалт
```
□ URL validation-ыг whitelist-ээр хий (зөвшөөрөгдсөн domain/протокол л)
□ Дотоод IP хүрээг (127.0.0.0/8, 169.254.0.0/16, 10.0.0.0/8 гэх мэт) блоклох
□ Redirect-ийг автоматаар дагахгүй байх (эсвэл дагасны дараа дахин шалгах)
□ Cloud metadata endpoint рүү хандахыг network түвшинд хориглох (IMDSv2 ашиглах AWS-д)
```

---

## 12. RCE (Remote Code Execution)

Attacker сервер дээр дурын код ажиллуулах чадвартай болох — **хамгийн ноцтой vulnerability**.

**Түгээмэл эх сурвалж:**
- Insecure deserialization (Python `pickle`, Java `ObjectInputStream`, PHP `unserialize`)
- Command injection: `os.system(user_input)` шиг код
- File upload → web-accessible directory-д ажиллах боломжтой файл (`.php`, `.jsp`) байршуулах
- Template injection (доор SSTI хэсэгт)

**Command injection жишээ:**
```python
# ЭМЗЭГ КОД:
os.system(f"ping {user_input}")
# attacker input: "8.8.8.8; rm -rf /"  эсвэл  "8.8.8.8 && cat /etc/passwd"
```

### Хамгаалалт
```
□ Хэрэглэгчийн input-ыг shell command-д шууд бүү дамжуул
□ subprocess ашиглах бол shell=False, аргументыг list хэлбэрээр дамжуул
  (subprocess.run(["ping", user_input], shell=False))
□ Deserialization хийхээс өмнө эх сурвалжийг битгий итгэ — JSON шиг аюулгүй формат ашигла (pickle биш)
□ File upload-ыг web root-оос гадуур хадгалах, ажиллуулах эрхгүй болгох
□ Least privilege — код ажиллуулж буй хэрэглэгчийн эрхийг хамгийн бага байлга
```

---

## 13. XXE (XML External Entity Injection)

XML parser нь гаднаас тодорхойлсон "entity"-г уншиж, файл унших эсвэл SSRF хийхэд ашиглагдах боломж олгодог.

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<foo>&xxe;</foo>
```
Хэрэв энэ XML-ийг parser боловсруулбал, `&xxe;` орсон хэсэгт `/etc/passwd`-ийн агуулга орж ирнэ.

**SSRF хувилбар:**
```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://internal-server/admin"> ]>
```

### Хамгаалалт
```
□ XML parser-т External Entity, DTD processing-ийг ЗААВАЛ УНТРААХ
  (Python lxml: resolve_entities=False; Java: setFeature disallow-doctype-decl)
□ Боломжтой бол XML-ийн оронд JSON ашиглах
□ Хэрэв XML заавал хэрэгтэй бол, upload хийсэн файлыг strict schema validation-оор шалгах
```

---

## 14. SSTI (Server-Side Template Injection)

Хэрэглэгчийн input нь template engine-ийн **код** гэж буруу тайлагдаж, серверийн талд ажиллах attack.

**Илрүүлэх (Jinja2/Python жишээ):**
```
{{7*7}}     → хариу "49" гарвал SSTI байгааг илтгэнэ (49 бол simple text биш, тооцоолол хийгдсэн)
```

**RCE хүртэл хөгжих жишээ (Jinja2):**
```
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
```
Ийм маягаар template engine-ийн Python object graph-аар дамжуулж, эцэст нь `os.popen`-д хүрч, дурын команд ажиллуулж болно.

### Хамгаалалт
```
□ Хэрэглэгчийн input-ыг template-ийн "код" хэсэгт хэзээ ч шууд битгий оруул
  (зөвхөн template-ийн ӨГӨГДӨЛ (variable) хэсэгт л ашигла)
□ Sandbox хийгдсэн template engine ашиглах (Jinja2 SandboxedEnvironment)
  — гэхдээ sandbox bypass олддог тул цорын ганц хамгаалалт болгож бүү найд
□ String-аас template render хийхийн оронд, template-ийг тогтмол файлаас ачаалах
```

---

## 15. CHEAT SHEET — НЭГТГЭСЭН

| Vulnerability | 1-р шатны хамгаалалт |
|---|---|
| XSS | Output encoding + CSP + HttpOnly cookie |
| CSRF | SameSite cookie + CSRF token |
| SQLi | Parameterized queries |
| SSRF | URL whitelist + дотоод IP блок |
| RCE | Shell-ээс зайлсхийх, list-аргумент ашиглах, least privilege |
| XXE | External entity parsing-ийг унтраах |
| SSTI | User input-ыг зөвхөн variable болгон дамжуулах, sandbox |
| JWT | Algorithm whitelist server-side, богино exp, хүчтэй secret |
| OAuth | `state` параметр, exact redirect_uri match, PKCE |
| CORS | Origin-ыг whitelist-ээр exact match шалгах |

### Хурдан тест хийх payload-ууд
```
XSS:    <script>alert(1)</script>
SQLi:   ' OR SLEEP(5)-- -
SSTI:   {{7*7}}   эсвэл   ${7*7}   (template engine-ээс хамаарна)
XXE:    <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
SSRF:   http://169.254.169.254/latest/meta-data/
CSRF:   auto-submit form, SameSite/token байгаа эсэхийг шалгах
```

---

*Энэ материал бол OWASP Top 10-ийн үндсэн ойлголтуудыг гүнзгийрүүлсэн хувилбар. Аль нэг сэдвийг илүү нарийвчлан (жишээ: зөвхөн JWT attack-уудыг лабораторийн жишээтэйгээр) үргэлжлүүлж болно.*
