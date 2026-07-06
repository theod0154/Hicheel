# NETWORKING — БҮРЭН ГҮНЗГИЙ СУРГАЛТЫН МАТЕРИАЛ ⭐⭐⭐⭐⭐ (Заавал)

---

## АГУУЛГА
1. OSI Model
2. TCP/IP
3. ARP
4. DNS
5. DHCP
6. NAT
7. VLAN
8. Routing
9. Switching
10. VPN
11. HTTP/HTTPS
12. TLS
13. SSH
14. SMTP
15. FTP
16. SMB
17. Cheat Sheet — нэгтгэсэн

---

## 1. OSI MODEL

7 давхаргатай онолын загвар — сүлжээний харилцаа хэрхэн бүтэцлэгддэгийг ойлгоход тусалдаг.

```
┌──────────────────────────────────────────────────────┐
│ 7. Application  │ HTTP, FTP, SMTP, DNS                 │  ← хэрэглэгчийн апп харьцдаг давхарга
│ 6. Presentation │ Encryption (TLS), compression, encode│  ← өгөгдлийн формат/шифрлэлт
│ 5. Session      │ Session establish/maintain/terminate │  ← харилцааны session удирдах
│ 4. Transport    │ TCP, UDP                              │  ← найдвартай/найдваргүй дамжуулалт
│ 3. Network      │ IP, ICMP, Routing                     │  ← host хооронд packet чиглүүлэх
│ 2. Data Link    │ Ethernet, MAC, ARP, Switch             │  ← физик segment доторх frame дамжуулалт
│ 1. Physical     │ Cable, radio, voltage                  │  ← физик дохио дамжуулалт
└──────────────────────────────────────────────────────┘
```

**Санах арга (доороос дээш):** "Please Do Not Throw Sausage Pizza Away" (Physical, Data Link, Network, Transport, Session, Presentation, Application)

**Яагаад чухал вэ:** Troubleshooting хийхэд "аль давхаргад асуудал байна вэ" гэдгээр эрэмбэлж бодох боломж олгодог. Жишээ: cable тасарсан бол Layer 1, IP тохиргоо буруу бол Layer 3, DNS ажиллахгүй бол Layer 7.

**Аюулгүй байдлын хувьд:** Attack бүр тодорхой давхаргад чиглэдэг:
- Layer 2: ARP spoofing, MAC flooding
- Layer 3: IP spoofing, ICMP flood
- Layer 4: SYN flood, port scanning
- Layer 7: SQLi, XSS, application-level DoS

---

## 2. TCP/IP

Практик дээр бодитоор ашиглагддаг 4-давхаргат загвар (OSI-г хялбаршуулсан хувилбар):
```
Application  (HTTP, DNS, SSH...)
Transport    (TCP, UDP)
Internet     (IP, ICMP)
Link         (Ethernet, WiFi)
```

### TCP (Transmission Control Protocol) — найдвартай, холболт-суурьтай
**3-Way Handshake:**
```
Client → Server:  SYN (seq=x)               "холболт нээе"
Server → Client:  SYN-ACK (seq=y, ack=x+1)  "зөвшөөрч байна, миний seq"
Client → Server:  ACK (ack=y+1)             "баталгаажлаа"
─── Холболт нээгдлээ, өгөгдөл дамжина ───
```
**Холболт хаах (4-way):** `FIN → ACK → FIN → ACK` (хоёр тал тус тусад нь хаана)

**TCP-ийн онцлог:** дараалал баталгаажуулна (sequence number), алдагдсан packet-ийг дахин илгээнэ (retransmission), flow control (window size), congestion control.

### UDP (User Datagram Protocol) — хурдан, холболтгүй
Handshake байхгүй, дараалал баталгаажуулахгүй, алдагдсан packet дахин илгээхгүй — **хурдыг чухалчилсан** протокол (DNS query, video streaming, VoIP, gaming).

| | TCP | UDP |
|---|---|---|
| Найдвартай байдал | Баталгаатай (retransmit) | Баталгаагүй |
| Хурд | Удаан (handshake, ack) | Хурдан |
| Хэрэглээ | HTTP, SSH, FTP, email | DNS query, streaming, gaming |

### IP Addressing
```
IPv4: 192.168.1.1/24    → 32-bit, 4 октет
Private range (RFC 1918):
  10.0.0.0/8
  172.16.0.0/12
  192.168.0.0/16
```
`/24` (subnet mask 255.255.255.0) гэдэг нь эхний 24 bit нь network хэсэг, үлдсэн 8 bit нь host хэсэг гэсэн үг — тухайн subnet-д 254 host байрлуулж болно (0 ба 255 нь network/broadcast хаяг тул ашиглагдахгүй).

**CIDR тооцоолол жишээ:** `/26` = 255.255.255.192 = subnet бүрт 62 host

---

## 3. ARP (Address Resolution Protocol)

IP хаягийг **MAC хаяг** руу хөрвүүлдэг протокол (Layer 2-Layer 3-ийн гүүр).

```
1. Host A "192.168.1.5-ийн MAC хаяг хэн бэ?" гэж broadcast илгээнэ (ARP Request)
2. 192.168.1.5 эзэмшигч host "Миний MAC AA:BB:CC:DD:EE:FF" гэж хариулна (ARP Reply)
3. Host A энэ mapping-ыг ARP cache-даа хадгална
```

```bash
arp -a                    # local ARP cache харах
```

### Security: ARP Spoofing
ARP протокол **баталгаажуулалт (authentication) байхгүй** — хэн ч "би 192.168.1.1 (gateway)-ийн MAC хаяг нь" гэж хуурамч ARP Reply илгээж болно. Ингэснээр victim-ийн traffic attacker-ийн машин руу чиглэнэ (Man-in-the-Middle).

**Илрүүлэх:** ARP cache дотор нэг IP хаягт хоёр өөр MAC харагдах, эсвэл gateway-ийн MAC гэнэт өөрчлөгдөх.
**Хамгаалалт:** Dynamic ARP Inspection (switch-ийн feature), static ARP entry чухал host-д, ARP spoofing detection tool (arpwatch).

---

## 4. DNS (Domain Name System)

Domain нэрийг IP хаяг руу хөрвүүлдэг, "интернэтийн утасны дэвтэр".

### Query flow
```
1. Client → Recursive Resolver (ISP/8.8.8.8): "example.com гэж юу вэ?"
2. Resolver → Root server: "→ .com-ийн TLD server рүү яв"
3. Resolver → TLD (.com) server: "→ example.com-ийн Authoritative server рүү яв"
4. Resolver → Authoritative server: "example.com = 93.184.216.34"
5. Resolver → Client: хариу буцаана (болон cache-д хадгална)
```

### Record төрлүүд
| Type | Тайлбар |
|---|---|
| A | Domain → IPv4 хаяг |
| AAAA | Domain → IPv6 хаяг |
| CNAME | Domain → өөр domain (alias) |
| MX | Email server чиглүүлэлт |
| TXT | Текст мэдээлэл (SPF/DKIM/domain verification-д ашиглагддаг) |
| NS | Domain-ийн authoritative name server-үүд |

```bash
dig example.com A
dig example.com MX
nslookup example.com
```

### Security
- **DNS Spoofing/Cache Poisoning** — attacker хуурамч DNS хариу оруулж, хэрэглэгчийг fake сайт руу чиглүүлэх
- **DNSSEC** — DNS хариунд digital signature нэмж, хуурамчаар үүсгэсэн хариуг илрүүлэх боломж олгодог
- **DNS tunneling** — DNS query-д нуугдаж firewall-аар өгөгдөл гаргах attack арга (защита: DNS traffic-ийн pattern/хэмжээг хянах)

---

## 5. DHCP (Dynamic Host Configuration Protocol)

Сүлжээнд шинээр холбогдож буй host-д автоматаар IP хаяг, subnet mask, gateway, DNS server олгодог протокол.

### DORA процесс
```
Discover: Client → Broadcast: "DHCP server та байна уу?"
Offer:    Server → Client: "энэ IP-г санал болгож байна"
Request:  Client → Broadcast: "энэ IP-г авъя" (бусад server-т ч мэдэгдэнэ)
Ack:      Server → Client: "баталгаажлаа, энэ IP чинийх"
```

### Security
- **Rogue DHCP Server** — attacker өөрийн DHCP server ажиллуулж, victim-д буруу gateway/DNS олгож MITM хийх боломж
- **DHCP Starvation** — attacker бүх боломжит IP хаягийг өөрийн MAC-аар шаардаж, жинхэнэ хэрэглэгчид IP авах боломжгүй болгох (DoS)
- **Хамгаалалт:** DHCP Snooping (switch feature — зөвшөөрөгдсөн port-оос ирсэн DHCP Offer-ийг л зөвшөөрдөг)

---

## 6. NAT (Network Address Translation)

Дотоод (private) IP хаягийг гадаад (public) IP хаяг руу хөрвүүлдэг — интернэт дээрх public IP хомсдлыг шийддэг.

### NAT төрлүүд
| Төрөл | Тайлбар |
|---|---|
| Static NAT | 1 private IP ↔ 1 public IP (тогтмол) |
| Dynamic NAT | Private IP-үүд public IP pool-оос авдаг |
| PAT (Port Address Translation, "NAT overload") | Олон private IP нэг public IP-г **өөр өөр порт**-оор хуваалцдаг — гэрийн router-ийн ердийн горим |

```
Дотоод: 192.168.1.5:54321 → Router NAT → Гадаад: 203.0.113.10:61234 → Интернэт
```
Router нь энэ mapping-ыг NAT table-д хадгалж, хариу ирэхэд буцааж зөв дотоод host руу чиглүүлдэг.

**Аюулгүй байдлын үр нөлөө:** NAT нь **firewall биш**, гэхдээ талын үр дүнд дотоод host-уудыг гаднаас шууд хандахаас "нуудаг" (учир нь гадна талаас private IP руу шууд хандах боломжгүй, зөвхөн NAT table-д бүртгэгдсэн session-ий хариу л дотогш орж чадна).

---

## 7. VLAN (Virtual LAN)

Нэг физик switch-ийг **логикоор олон тусдаа сүлжээ** болгон хуваах технологи.

```
┌─────────────── Switch ───────────────┐
│  Port 1-8   → VLAN 10 (Санхүү хэлтэс) │
│  Port 9-16  → VLAN 20 (IT хэлтэс)      │
│  Port 17-24 → VLAN 30 (Guest WiFi)     │
└───────────────────────────────────────┘
```
VLAN 10 дахь host, VLAN 20 дахь host-той шууд харилцахгүй (өөр broadcast domain) — тэдгээрийг холбохын тулд **Layer 3 router (Router-on-a-stick эсвэл Layer 3 switch)** шаардлагатай.

**802.1Q Tagging:** Trunk port дээр frame бүрт VLAN ID (tag) нэмж, аль VLAN-д харьяалагдахыг заана.

### Аюулгүй байдал
- **VLAN Hopping** — attacker буруу тохируулагдсан trunk port ашиглан зөвшөөрөгдөөгүй VLAN руу нэвтрэх (Double Tagging attack)
- **Хамгаалалт:** unused port-уудыг unused VLAN-д оруулах, native VLAN-ыг 1-ээс өөр болгох, DTP (Dynamic Trunking Protocol)-ийг унтраах

---

## 8. ROUTING

Router нь **өөр өөр сүлжээ хооронд** packet чиглүүлдэг (Layer 3 төхөөрөмж).

### Static vs Dynamic Routing
- **Static** — гараар тохируулсан зам, жижиг сүлжээнд энгийн, гэхдээ том сүлжээнд удирдахад хэцүү
- **Dynamic** — router-ууд протокол ашиглан **автоматаар** зам солилцдог

### Dynamic Routing Protocol-ууд
| Protocol | Төрөл | Тайлбар |
|---|---|---|
| RIP | Distance-vector | Хамгийн энгийн, hop count-оор шийддэг, жижиг сүлжээнд |
| OSPF | Link-state | Том enterprise сүлжээнд өргөн ашиглагддаг, хурдан convergence |
| BGP | Path-vector | **Интернэтийн гол протокол** — ISP хоорондын routing |

```bash
ip route show              # local routing table харах (Linux)
traceroute example.com     # packet-ийн явсан замыг харах (hop бүрийг)
```

### Аюулгүй байдал
- **BGP Hijacking** — attacker буруу route мэдэгдэж (announce), traffic-ийг өөрийн сүлжээгээр дамжуулах (том хэмжээний интернэт эвдрэл үүсгэж болно)
- **Route Poisoning** — Dynamic routing protocol-д хуурамч route оруулах attack

---

## 9. SWITCHING

Switch нь **нэг сүлжээний доторх** device-үүдийг холбодог (Layer 2 төхөөрөмж), MAC хаягаар frame чиглүүлдэг.

### MAC Address Table
Switch нь ирсэн frame-ийн эх MAC хаягийг үзэж, аль port-той холбоотойг сурч, дараагийн удаа тэр MAC руу зөвхөн тэр port руу л frame илгээдэг (broadcast биш, targeted).

```bash
show mac address-table    # Cisco switch-ийн команд
```

### Аюулгүй байдал
- **MAC Flooding** — attacker маш олон хуурамч MAC хаягаар switch-ийн MAC table-ыг дүүргэж, switch "fail-open" горимд орж бүх frame-ийг бүх port руу broadcast хийхэд хүргэдэг (энэ нь sniffing боломж олгодог)
- **Хамгаалалт:** Port Security (нэг port дээр зөвшөөрөгдөх MAC хаягийн тоог хязгаарлах)

---

## 10. VPN (Virtual Private Network)

Нээлттэй сүлжээгээр (интернэт) **encrypt хийгдсэн, "хувийн" гэсэн мэт** сүлжээний холболт үүсгэдэг технологи.

### VPN протоколууд
| Protocol | Тайлбар |
|---|---|
| **IPsec** | Network давхаргад ажилладаг, site-to-site VPN-д түгээмэл, хүчтэй encryption |
| **OpenVPN** | SSL/TLS дээр суурилсан, уян хатан, open-source |
| **WireGuard** | Орчин үеийн, маш хурдан, энгийн код (аюулгүй байдлын audit хийхэд хялбар), ChaCha20 encryption ашигладаг |
| **L2TP/PPTP** | Хуучин протокол — PPTP **аюулгүй биш**, бүү ашигла |

### Site-to-Site vs Remote Access VPN
- **Site-to-Site** — хоёр оффисийн сүлжээг байнга холбоно (router-router хооронд)
- **Remote Access** — ганц хэрэглэгч гэрээсээ компанийн сүлжээ рүү холбогдоно (client software ашиглан)

### Аюулгүй байдал
- Split tunneling эсэхийг анхаарах — split tunnel хийвэл зөвхөн компанийн traffic VPN-ээр явж, бусад нь шууд интернэтэд гардаг (тодорхой эрсдэлтэй тохиолдолд)
- Хуучин, эвдэрсэн протокол (PPTP) хэрэглэхгүй байх

---

## 11. HTTP / HTTPS

HTTP — веб хуудас дамжуулах протокол (Layer 7), stateless.

**HTTPS = HTTP + TLS** — traffic encrypt хийгдэж, дундаас нь хэн нэгэн уншиж/өөрчилж чадахгүй болдог.

```
GET /page HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
Content-Type: text/html
```

### Status code бүлгүүд
```
1xx — Informational
2xx — Success (200 OK)
3xx — Redirection (301 Moved, 302 Found)
4xx — Client error (404 Not Found, 403 Forbidden)
5xx — Server error (500 Internal Server Error)
```

---

## 12. TLS (Transport Layer Security)

HTTPS/SSH зэрэг олон протоколын доор ажилладаг encryption давхарга (өмнөх Cryptography материалд дэлгэрэнгүй авсан).

**Богино давталт:**
```
1. Client/Server cipher suite тохирно
2. Server certificate илгээнэ, client CA chain-ээр шалгана
3. ECDH-ээр session key солилцоно
4. Цаашид AES-GCM-ээр бүх traffic encrypt хийгдэнэ
```

```bash
openssl s_client -connect example.com:443
```

**TLS 1.3 vs 1.2:** TLS 1.3 нь handshake-ийг богиносгосон (1-RTT), сул cipher suite-уудыг устгасан, илүү хурдан бөгөөд аюулгүй.

---

## 13. SSH (Secure Shell)

Алсын серверт **encrypt хийгдсэн** аргаар нэвтрэх протокол (Telnet-ийн орлуулагч — Telnet бол plaintext тул ашиглахгүй).

```bash
ssh user@server.com
ssh -i ~/.ssh/id_ed25519 user@server.com    # key-based auth
ssh-keygen -t ed25519                        # шинэ key pair үүсгэх
```

### Auth арга
- **Password-based** — сул, brute-force-д эмзэг
- **Key-based (public key auth)** — илүү аюулгүй, private key-г хэзээ ч бусадтай бүү хуваалц

### Аюулгүй байдал
```
□ Password auth-ыг унтраа, зөвхөн key-based auth зөвшөөр
□ Root login-ыг шууд SSH-ээр хориглох (PermitRootLogin no)
□ Default port (22)-ыг солих нь "security through obscurity" — жижиг хамгаалалт, гол шийдэл биш
□ fail2ban ашиглаж brute-force оролдлогыг блоклох
□ SSH key-ийн passphrase-ийг тавь
```

---

## 14. SMTP (Simple Mail Transfer Protocol)

Email **илгээх** протокол (email унших нь IMAP/POP3-ээр хийгддэг).

```
Client → Server: HELO/EHLO
Client → Server: MAIL FROM:<sender@example.com>
Client → Server: RCPT TO:<recipient@example.com>
Client → Server: DATA ... email агуулга ... .
```

### Аюулгүй байдал
- **Open Relay** — зөв тохируулаагүй SMTP server нь хэн ч ашиглаж spam илгээх боломж олгодог
- **SPF, DKIM, DMARC** — email spoofing-ээс хамгаалах TXT record-based механизмууд:
  - **SPF** — тухайн domain-аас email илгээх зөвшөөрөгдсөн server-үүдийг жагсаана
  - **DKIM** — email-ийг digital signature-ээр баталгаажуулна
  - **DMARC** — SPF/DKIM амжилтгүй бол юу хийхийг зааж өгнө (reject/quarantine)

---

## 15. FTP (File Transfer Protocol)

Файл дамжуулах хуучин протокол — **plaintext** (username/password ч encrypt хийгддэггүй) тул орчин үед **SFTP (SSH-based)** эсвэл **FTPS (TLS-based)** ашиглахыг зөвлөдөг.

```bash
ftp server.com              # анонимous/plaintext, аюулгүй биш
sftp user@server.com        # SSH дээр суурилсан, encrypt хийгдсэн
```

### Аюулгүй байдал
- Anonymous FTP login зөвшөөрөх нь мэдээлэл алдагдах эрсдэлтэй
- Plaintext FTP ашиглах нь credential sniffing-д маш эмзэг

---

## 16. SMB (Server Message Block)

Windows орчинд файл/принтер хуваалцах протокол (`\\server\share` — Windows network share).

```bash
smbclient -L //server/ -N          # anonymous session-оор share жагсаах
smbclient //server/share -U user   # холбогдох
```

### Аюулгүй байдал
- **SMBv1** — маш хуучирсан, **WannaCry ransomware** (EternalBlue exploit, MS17-010) энэ протоколын weakness-ийг ашигласан. **SMBv1-ийг унтраах шаардлагатай.**
- **Null session** — зөвшөөрөлгүй хэрэглэгч anonymous share/user жагсаалт харах боломж (буруу тохиргоо)
- **SMB relay attack** — captured authentication-ыг өөр server руу дамжуулж, victim-ийн нэрээр нэвтрэх (NTLM relay)
- **Хамгаалалт:** SMBv1 унтраах, SMB signing идэвхжүүлэх, null session хориглох

---

## 17. CHEAT SHEET — НЭГТГЭСЭН

### Порт дугаарууд (санах ёстой)
```
20/21  FTP (data/control)     22   SSH        23   Telnet (бүү ашигла)
25     SMTP                   53   DNS        67/68 DHCP
80     HTTP                   443  HTTPS      110  POP3
143    IMAP                   161  SNMP       389  LDAP
445    SMB                    3389 RDP        3306 MySQL
```

### Troubleshooting командууд
```bash
ping HOST                  # basic reachability (ICMP)
traceroute HOST            # замын hop бүрийг харах
nslookup / dig HOST        # DNS шалгах
netstat -tulnp             # local listening port харах
ss -tulnp                  # netstat-ийн шинэ хувилбар
ip addr / ip route         # IP/routing тохиргоо харах (Linux)
arp -a                     # ARP cache харах
tcpdump -i eth0            # packet capture
```

### Давхарга бүрийн attack ба хамгаалалт (хураангуй)
| Layer | Attack | Хамгаалалт |
|---|---|---|
| L2 | ARP spoofing, MAC flooding | Dynamic ARP Inspection, Port Security |
| L2 | VLAN Hopping | Native VLAN солих, unused port-ыг unused VLAN-д |
| L3 | IP spoofing, BGP hijack | Ingress filtering, RPKI |
| L4 | SYN flood, port scan | SYN cookies, rate limiting, firewall |
| L7 | DNS spoofing | DNSSEC |
| L7 | SMB exploit (EternalBlue) | SMBv1 унтраах, patch |
| Auth | Rogue DHCP | DHCP Snooping |

---

*Networking бол Cyber Security-ийн бүх бусад чиглэлийн (Web, Cloud, AD pentest) суурь юм — эдгээр protocol-уудыг гүнзгий ойлгосноор, attack-ийн логикийг ч, хамгаалалтын логикийг ч илүү сайн ойлгох боломжтой болно. Дараагийн үргэлжлэл болгож Wireshark-аар эдгээр протокол бүрийг бодит траффикт хэрхэн харагддагийг (packet-by-packet) судалж болно.*
