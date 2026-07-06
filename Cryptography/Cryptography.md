# CRYPTOGRAPHY — БҮРЭН ГҮНЗГИЙ СУРГАЛТЫН МАТЕРИАЛ ⭐⭐⭐⭐☆

---

## АГУУЛГА
1. Cryptography-ийн үндсэн ойлголт (Symmetric vs Asymmetric)
2. AES
3. RSA
4. ECC
5. Hashes
6. HMAC
7. Digital Signatures
8. PKI
9. Certificates (TLS/SSL)
10. Cheat Sheet + Түгээмэл алдаанууд

---

## 1. ҮНДСЭН ОЙЛГОЛТ

**Symmetric encryption** — нэг л түлхүүрээр encrypt/decrypt хийнэ (AES). Хурдан, гэхдээ түлхүүрийг хэрхэн аюулгүй дамжуулах вэ гэдэг асуудалтай.

**Asymmetric encryption** — хос түлхүүр: public key (encrypt/verify) + private key (decrypt/sign). Удаан, гэхдээ түлхүүр дамжуулах асуудлыг шийддэг (RSA, ECC).

**Практикт хосолж ашигладаг:** TLS handshake-д RSA/ECC-ээр session key солилцоод, дараа нь бодит өгөгдлийг AES-ээр encrypt хийдэг — учир нь AES хурдан, asymmetric нь зөвхөн жижиг key солилцоход л ашиглагддаг.

```
┌──────────────┐         ┌──────────────┐
│  Symmetric    │         │  Asymmetric   │
│  (AES)        │         │  (RSA/ECC)    │
├──────────────┤         ├──────────────┤
│ 1 key         │         │ 2 key (pub/priv)│
│ Хурдан        │         │ Удаан          │
│ Их өгөгдөлд    │         │ Key солилцоо,   │
│               │         │ signature-д      │
└──────────────┘         └──────────────┘
```

---

## 2. AES (Advanced Encryption Standard)

Symmetric block cipher — 128-bit блокоор өгөгдлийг шифрлэнэ. Key хэмжээ: 128/192/256-bit.

### Ажиллах горим (Mode of Operation) — маш чухал!
| Mode | Тайлбар | Ашиглах уу? |
|---|---|---|
| **ECB** | Блок бүрийг тусад нь, ижил аргаар encrypt хийдэг | **ЯЛАН АШИГЛАХГҮЙ** — ижил plaintext блок нь ижил ciphertext өгдөг тул pattern алдагдана (ялгаатай зурагт харагддаг алдартай "ECB penguin" жишээ) |
| **CBC** | Блок бүрийг өмнөх ciphertext-тэй XOR хийгээд encrypt хийдэг | Ашиглаж болно, IV нь санамсаргүй байх ёстой |
| **GCM** | CBC-ийн санааг + authentication (баталгаажуулалт)-ыг нэгтгэсэн | **ХАМГИЙН ЗӨВ СОНГОЛТ** — encryption + integrity хамт |
| **CTR** | Counter-based stream cipher маягаар ажилладаг | Сайн, гэхдээ authentication тусад нь хэрэгтэй |

**Яагаад GCM хамгийн зөв вэ:** GCM нь зөвхөн нууцлал (confidentiality) төдийгүй **бүрэн бүтэн байдал (integrity)**-ыг хамт баталгаажуулдаг (authentication tag үүсгэдэг). Хэрэв ciphertext-ийг хэн нэгэн өөрчилбөл, decrypt хийхэд алдаа гарна — CBC дан ганцаараа үүнийг мэдэхгүй.

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)                    # IV/nonce ДАВХАРДАЖ БОЛОХГҮЙ, key бүрт өвөрмөц байх ёстой
ciphertext = aesgcm.encrypt(nonce, b"secret message", None)
plaintext = aesgcm.decrypt(nonce, ciphertext, None)
```

### Түгээмэл алдаа
```
□ ECB mode ашиглах — pattern алдагддаг
□ IV/nonce давхардуулах эсвэл тогтмол утга ашиглах — key-той хамт nonce давтагдвал encryption бүхэлдээ эвдэрдэг
□ Key-ийг код дотор hardcode хийх
□ Padding oracle attack-ад өртөмтгий (CBC + буруу error handling) — GCM ашигласнаар энэ асуудал арилдаг
```

---

## 3. RSA

Asymmetric алгоритм, том тоог үржих амархан, харин үржвэрийг factoring хийх хэцүү гэдэг математик зарчим дээр суурилдаг.

**Түлхүүр үүсгэх:**
```
1. Хоёр том анхны тоо p, q сонго
2. n = p × q  (public modulus)
3. φ(n) = (p-1)(q-1)
4. e сонго (ихэвчлэн 65537), gcd(e, φ(n)) = 1
5. d = e⁻¹ mod φ(n)  (private exponent)
Public key: (n, e)   Private key: (n, d)
```

**Encrypt/Decrypt:** `ciphertext = plaintext^e mod n` | `plaintext = ciphertext^d mod n`

### Түгээмэл эмзэг байдал
| Асуудал | Тайлбар |
|---|---|
| **Padding байхгүй (Textbook RSA)** | Deterministic — ижил plaintext нь үргэлж ижил ciphertext өгдөг. **OAEP padding заавал хэрэглэх ёстой.** |
| **Small e (e=3) + padding байхгүй** | Хэрэв мессеж богино, padding байхгүй бол cube root attack-аар шууд decrypt хийж болно |
| **Common modulus attack** | Хэрэв хоёр хэрэглэгч ижил `n` ашиглавал (буруу тохиргоо), ижил мессежийн хоёр өөр ciphertext-ээс plaintext сэргээж болно |
| **Wiener's attack** | `d` (private exponent) хэт жижиг бол continued fraction algorithm-аар `d`-г бодож олж болно |
| **Factoring сул n** | Хэрэв `p`, `q` хоорондоо хэт ойрхон эсвэл `n` нь дутуу урттай (жишээ 512-bit) бол factordb.com/GNFS-ээр factoring хийж болно |

**Зөв хэрэглээ:**
```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

ciphertext = public_key.encrypt(
    b"secret",
    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                 algorithm=hashes.SHA256(), label=None)
)
```

**Практик зөвлөмж:** RSA-г шууд том өгөгдөл encrypt хийхэд бүү ашигла (удаан, хязгаарлагдмал урттай) — зөвхөн AES key солилцоход ашигла (hybrid encryption).

---

## 4. ECC (Elliptic Curve Cryptography)

Elliptic curve дээрх математик бүтцэд суурилсан asymmetric крипто — **RSA-тай ижил түвшний аюулгүй байдлыг хамаагүй богино түлхүүрээр** олгодог.

```
RSA 3072-bit  ≈  ECC 256-bit    (ойролцоо аюулгүй байдлын түвшин)
```
Тиймээс ECC нь **хурдан, бага нөөц ашигладаг** — mobile, IoT, TLS-д өргөн ашиглагддаг.

**Түгээмэл curve-ууд:** P-256 (secp256r1), Curve25519 (X25519 key exchange-д, Ed25519 signature-д — орчин үеийн, side-channel attack-аас илүү сайн хамгаалагдсан).

### ECDH (Elliptic Curve Diffie-Hellman) — key exchange
```python
from cryptography.hazmat.primitives.asymmetric import ec

private_key = ec.generate_private_key(ec.SECP384R1())
public_key = private_key.public_key()
# Хоёр тал өөр өөрийн private key + нөгөөгийн public key-ээр ижил shared secret тооцно
shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
```

### Түгээмэл алдаа
```
□ Random nonce (k утга)-ыг ECDSA signature-д давхардуулах — энэ нь private key-г бүрэн задлах боломж олгодог
  (алдартай жишээ: Sony PS3-ийн ECDSA private key энэ алдаагаар алдагдсан)
□ Сул/стандарт бус curve ашиглах — зөвхөн сайн шалгагдсан curve (P-256, Curve25519) ашигла
```

---

## 5. HASHES

Hash function нь дурын урттай input-ыг **тогтмол урттай, нэг чиглэлтэй (one-way)** гаралт руу хувиргадаг.

**Шинж чанарууд:**
- **Deterministic** — ижил input үргэлж ижил hash өгнө
- **One-way** — hash-аас эх input-ыг буцаан гаргах боломжгүй байх ёстой
- **Collision resistance** — хоёр өөр input ижил hash өгөх магадлал бараг тэг байх ёстой
- **Avalanche effect** — input-д 1 bit өөрчлөлт хийвэл, hash бүрэн өөр болно

| Algorithm | Төлөв |
|---|---|
| MD5 | **Эвдэрсэн** — collision амархан үүсгэж болно, бүү ашигла |
| SHA-1 | **Эвдэрсэн** (2017 оны SHAttered attack-аар collision батлагдсан) |
| SHA-256/SHA-3 | Одоогийн стандарт, аюулгүй |
| bcrypt/scrypt/Argon2 | **Password hashing-д зориулагдсан**, зориудаар удаан/нөөц ихтэй (доор дэлгэрэнгүй) |

### Чухал ойлголт: Password hash ≠ ердийн hash
Password-ыг SHA-256-аар хэшлэх нь **буруу** — учир нь SHA-256 хэт хурдан, GPU-аар секундэд тэрбум удаа тооцоолж, brute-force хийж болно.

**Зөв арга:** bcrypt, scrypt, Argon2 — эдгээр нь **зориудаар удаан**, мөн **salt**-ыг автоматаар оруулдаг:
```python
import bcrypt
hashed = bcrypt.hashpw(b"my_password", bcrypt.gensalt())
bcrypt.checkpw(b"my_password", hashed)   # True/False
```

**Salt-ийн ач холбогдол:** salt байхгүй бол, ижил password ашигласан хоёр хэрэглэгч ижил hash-тай болно — attacker нэг л удаа rainbow table бэлдээд олон хэрэглэгчийн password-ыг зэрэг тайлж болно. Salt бүр өвөрмөц байх тул энэ боломжгүй болно.

---

## 6. HMAC (Hash-based Message Authentication Code)

HMAC нь hash function + secret key-г хослуулж, **мессежийн бүрэн бүтэн байдал болон эх сурвалжийг** баталгаажуулдаг.

```
HMAC(key, message) = Hash((key ⊕ opad) || Hash((key ⊕ ipad) || message))
```

```python
import hmac, hashlib
signature = hmac.new(b"secret_key", b"message", hashlib.sha256).hexdigest()
# хүлээн авагч тал ижил key-ээр дахин тооцоод, ирсэн signature-тай харьцуулна
```

**Яагаад зөвхөн `hash(key + message)` ашиглахгүй вэ?** Ердийн hash concatenation нь **length extension attack**-д өртөмтгий (SHA-256/MD5 шиг Merkle-Damgård бүтэцтэй hash-уудад) — attacker өгөгдсөн hash-д шинэ өгөгдөл нэмж, шинэ хүчинтэй hash тооцож чадна, key-г мэдэхгүй ч гэсэн. HMAC-ийн тусгай бүтэц энэ attack-аас бүрэн хамгаалдаг.

**Хэрэглээ:** API request signing (AWS Signature V4), webhook баталгаажуулалт (Stripe, GitHub webhook-ууд HMAC ашигладаг), JWT-ийн HS256 signature.

**Чухал:** signature харьцуулахдаа **constant-time comparison** ашигла (`hmac.compare_digest()`), ердийн `==` ашиглавал **timing attack**-аар signature-ыг аажмаар таамаглаж болно.

---

## 7. DIGITAL SIGNATURES

HMAC-ээс ялгаатай нь: digital signature нь **asymmetric** — private key-ээр sign хийж, **хэн ч** public key-ээр verify хийж чадна (secret key хуваалцах шаардлагагүй тул **non-repudiation** буюу татгалзах боломжгүй байдлыг олгодог).

```python
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

signature = private_key.sign(
    b"important message",
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256()
)
public_key.verify(signature, b"important message", padding.PSS(...), hashes.SHA256())
```

**Ажиллах зарчим:**
```
1. Мессежийг эхлээд hash хийнэ (SHA-256)
2. Hash-ыг private key-ээр encrypt хийнэ (энэ нь signature)
3. Хүлээн авагч: ирсэн мессежийг дахин hash хийгээд,
   signature-ыг public key-ээр decrypt хийж, хоёр hash тохирч байгаа эсэхийг шалгана
```

**Хэрэглээ:** код sign хийх (software update баталгаажуулах), TLS certificate chain, blockchain transaction, email signing (PGP).

---

## 8. PKI (Public Key Infrastructure)

PKI бол public key-үүдийг **найдвартай хэн эзэмшиж байгааг баталгаажуулах** систем — учир нь "энэ бол Google-ийн public key" гэдгийг хэн нэгэн батлах ёстой, эс бөгөөс Man-in-the-Middle attack хийж fake public key орлуулж болно.

```
┌─────────────────────────────────────────┐
│     Root CA (өөрийгөө sign хийсэн)        │  ← хамгийн итгэмжлэгдсэн, OS/browser-т суусан
└─────────────────┬───────────────────────┘
                   │ sign хийнэ
┌─────────────────▼───────────────────────┐
│     Intermediate CA                       │  ← Root CA-г хамгаалахын тулд давхарга нэмдэг
└─────────────────┬───────────────────────┘
                   │ sign хийнэ
┌─────────────────▼───────────────────────┐
│     End-entity Certificate (жишээ:         │
│     google.com-ийн cert)                  │
└─────────────────────────────────────────┘
```

**Chain of Trust:** Browser нь Root CA-уудын жагсаалтыг урьдчилан итгэмжилдэг (OS/browser дотор суусан байдаг). Тэднээс доош chain-ээр орж, хэрэв аль нэг шат баталгаажвал, эцсийн certificate-д итгэдэг.

**CRL/OCSP:** Certificate хүчингүй болсон эсэхийг шалгах механизм (Certificate Revocation List, Online Certificate Status Protocol) — private key алдагдвал certificate-ыг revoke хийх шаардлагатай.

---

## 9. CERTIFICATES (TLS/SSL)

Certificate бол **public key + identity мэдээлэл + CA-ийн signature**-ыг агуулсан файл (X.509 формат).

### TLS Handshake (хялбарчилсан, TLS 1.3):
```
1. Client → Server: "Hello, TLS 1.3 дэмждэг, эдгээр cipher suite ашиглая"
2. Server → Client: Certificate + Public key + "энэ cipher ашиглая"
3. Client: Certificate-ийг CA chain-ээр шалгана (хүчинтэй, revoke хийгдээгүй, domain таарч байгаа эсэх)
4. Client & Server: ECDH-ээр session key солилцоно (Diffie-Hellman)
5. Цаашид бүх харилцаа AES-GCM-ээр encrypt хийгдэнэ (session key ашиглан)
```

### Certificate шалгах командууд
```bash
openssl s_client -connect example.com:443 -showcerts
openssl x509 -in cert.pem -text -noout          # certificate-ийн дэлгэрэнгүй мэдээлэл харах
openssl verify -CAfile ca.pem cert.pem          # chain of trust шалгах
```

### Түгээмэл алдаа/эмзэг байдал
```
□ Self-signed certificate production-д ашиглах — хэрэглэгчид "unsafe" анхааруулга авдаг, MITM-ийн эрсдэл нэмэгддэг
□ Хугацаа дууссан certificate шинэчлэхгүй байх
□ Weak cipher suite зөвшөөрөх (жишээ: RC4, SSLv3) — орчин үеийн attack-д эмзэг
□ Certificate pinning байхгүй байх (mobile app-д MITM-ээс хамгаалах нэмэлт давхарга)
□ Wildcard certificate (*.example.com) хэт өргөн ашиглах — нэг subdomain compromise хийгдвэл бусад бүх subdomain-д ч нөлөөлж болно
```

---

## 10. CHEAT SHEET + ТҮГЭЭМЭЛ АЛДААНУУД

### Алгоритм сонголтын хурдан заавар
```
Symmetric encryption:     AES-256-GCM
Asymmetric encryption:    RSA-OAEP (2048-bit+) эсвэл ECC (Curve25519/P-256)
Hashing (ерөнхий):        SHA-256 эсвэл SHA-3
Password hashing:         Argon2id (шинэ систем), bcrypt (хуучин систем)
Message authentication:   HMAC-SHA256
Digital signature:        RSA-PSS эсвэл ECDSA/Ed25519
Key exchange:             ECDH (X25519)
```

### АЛДАА БОЛГООМЖИЛ ЖАГСААЛТ
```
✗ Өөрийн crypto алгоритм зохион бүтээх ("don't roll your own crypto")
✗ ECB mode ашиглах
✗ MD5/SHA-1-ийг аюулгүй байдлын зорилгоор ашиглах
✗ Password-ыг ердийн hash (salt-гүй)-аар хадгалах
✗ IV/nonce-ыг давхардуулах эсвэл тогтмол утга болгох
✗ Signature/HMAC харьцуулахад constant-time comparison ашиглахгүй байх (timing attack)
✗ Textbook RSA (padding-гүй) ашиглах
✗ Хугацаа дууссан/weak certificate-тай TLS ашиглах
```

### Хэрэгслүүд
```bash
openssl enc -aes-256-gcm -in file -out file.enc -k password   # AES encrypt
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048   # RSA key үүсгэх
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365  # self-signed cert
hashcat -m 3200 hash.txt wordlist.txt                          # bcrypt hash crack хийж туршиж үзэх (лабораторид)
```

---

*Cryptography-ийн гол зарчим: аюулгүй байдал нь алгоритмын нууцлалаас биш, харин **сайн судлагдсан, нээлттэй стандарт алгоритм зөв хэрэглэхээс** шалтгаална (Kerckhoffs's principle). Дараагийн үргэлжлэл болгож зэрэгцээ CTF-style crypto challenge-үүд (RSA CTF techniques, XOR crypto) хийж болно.*
