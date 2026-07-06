# DOCKER — БҮРЭН ГҮНЗГИЙ СУРГАЛТЫН МАТЕРИАЛ
*Cyber Security / DevSecOps фокустой*

---

## АГУУЛГА
1. Docker гэж юу вэ, яагаад үүссэн
2. Docker-ийн дотоод архитектур
3. Linux дахь суурь механизм (Namespaces, Cgroups)
4. Images, Containers, Layers
5. Dockerfile — зөв бичих аргачлал
6. Networking
7. Volumes & Storage
8. Docker Compose
9. Аюулгүй байдал (Security) — гол хэсэг
10. Практик Lab-ууд
11. Troubleshooting
12. Kubernetes руу шилжих зам
13. Cheat Sheet (бүх командууд нэг дор)
14. Ярилцлагын асуултууд

---

## 1. DOCKER ГЭЖ ЮУ ВЭ, ЯАГААД ҮҮССЭН

Docker-ээс өмнө: "манай компьютер дээр ажилладаг байсан" гэдэг асуудал үргэлж гардаг байсан — учир нь server дээрх library-ийн хувилбар, OS-ийн тохиргоо өөр байдаг. Virtual Machine (VM) энэ асуудлыг шийдсэн ч, VM бүр өөрийн бүтэн OS ачаалдаг тул хүнд, удаан асдаг, нөөц их иддэг.

Container өөр аргаар шийддэг: **VM шиг hardware-ийг виртуалчлахгүй**, харин **нэг Linux kernel дээр process-уудыг тусгаарладаг**. Container гэдэг нь ердийн Linux process боловч тодорхой kernel feature-үүдээр "хучигдсан" тул өөрийн гэсэн filesystem, network, process tree байгаа мэт харагддаг.

**Гол ялгаа:**
```
VIRTUAL MACHINE                    CONTAINER
┌──────────────────┐              ┌──────────────────┐
│  App             │              │  App             │
├──────────────────┤              ├──────────────────┤
│Guest OS (бүтэн)  │              │Guest OS байхгүй  │
├──────────────────┤              ├──────────────────┤
│  Hypervisor      │              │Container Runtime │
├──────────────────┤              ├──────────────────┤
│  Host OS         │              │  Host OS Kernel  │
├──────────────────┤              ├──────────────────┤
│  Hardware        │              │  Hardware        │
└──────────────────┘              └──────────────────┘
```
VM хэдэн минут асаадаг бол, container **секундын дотор** асдаг — учир нь тусдаа OS ачаалах шаардлагагүй.

---

## 2. DOCKER-ИЙН ДОТООД АРХИТЕКТУР

```
┌────────────────────────────────────────────┐
│         Docker CLI (docker command)        │  ← та бичдэг команд
└─────────────────────┬──────────────────────┘
                      │ REST API дуудлага
┌─────────────────────▼────────────────────────┐
│           Docker Daemon (dockerd)            │  ← images, network, volume удирдана
└─────────────────────┬────────────────────────┘
                      │
┌─────────────────────▼────────────────────────┐
│                containerd                    │  ← container-ийн lifecycle удирдана
└─────────────────────┬────────────────────────┘
                      │
┌─────────────────────▼────────────────────────┐
│                   runc                       │  ← OCI runtime, kernel-тэй шууд
│                                              │    ажилладаг (namespace/cgroup үүсгэдэг)
└─────────────────────┬────────────────────────┘
                      │
┌─────────────────────▼────────────────────────┐
│    Linux Kernel (namespaces, cgroups)        │  ← жинхэнэ тусгаарлалт эндээс эхэлдэг
└──────────────────────────────────────────────┘
```

**Тайлбар:**
- **Docker CLI** — зүгээр л тонгойх (thin) client, командыг daemon-д дамжуулдаг.
- **dockerd (daemon)** — фон дээр ажилладаг сервис, `/var/run/docker.sock` гэсэн Unix socket-оор дамжуулж CLI-тай харилцдаг. Images, network, volume бүгдийг энэ удирддаг.
- **containerd** — Docker анх бүгдийг нэг дор хийдэг байсан ч, дараа нь энэ хэсгийг тусад нь гаргасан. Одоо CNCF (Cloud Native Computing Foundation)-ийн бие даасан project. Kubernetes ч мөн адил containerd-ийг шууд ашигладаг — тиймээс Docker дээр сурсан зүйл чинь Kubernetes дээр хэрэгтэй хэвээр байдаг.
- **runc** — **OCI (Open Container Initiative)** стандартын дагуу бодит container-ийг үүсгэдэг хамгийн доод түвшний tool. Энэ нь kernel syscall дуудаж namespace/cgroup-ыг үнэхээр үүсгэдэг.
- **OCI** — стандарт байдгаас болж, аль ч OCI-compliant runtime (runc, crun, gVisor) нь аль ч OCI-compliant image-ийг ажиллуулж чадна — vendor lock-in байхгүй.

**Яагаад ингэж хуваасан бэ?**
- Тус тусдаа модуль байх нь аюулгүй байдлын хувьд шалгахад хялбар (Unix philosophy: нэг зорилготой жижиг хэсгүүд)
- Kubernetes шиг систем containerd-ийг дан ганцаар нь ашиглах боломжтой болсон, Docker daemon бүхэлдээ шаардлагагүй болсон

---

## 3. LINUX ДАХЬ СУУРЬ МЕХАНИЗМ

### Namespaces — "Юу харагдах вэ" гэдгийг тодорхойлдог
Container доторх process нь host дээрх бусад бүх зүйлийг харахгүй, зөвхөн өөрийн "ертөнц"-ийг харна. Үүнийг Linux-ийн дараах namespace-үүд хийдэг:

| Namespace | Тусгаарладаг зүйл |
|---|---|
| PID | Process ID-ууд (container дотор PID 1 нь host дээр өөр PID байдаг) |
| NET | Network interfaces, IP хаяг, port-ууд |
| MNT | Mount points (filesystem харагдац) |
| UTS | Hostname |
| IPC | Inter-process communication (shared memory) |
| USER | User/Group ID mapping (rootless Docker-д чухал) |

**Жишээ:** container дотор `ps aux` бичихэд зөвхөн тухайн container-ийн process-үүд харагдана, host дээрх бусад process харагдахгүй — учир нь тэдгээр нь өөр PID namespace-д байгаа.

### Cgroups (Control Groups) — "Хэр их ашиглаж болох вэ" гэдгийг хязгаарладаг
Namespace нь **харагдацыг** хязгаарладаг бол, cgroups нь **нөөцийг** хязгаарладаг:
- CPU хэдэн % ашиглаж болох
- Memory хэдэн MB/GB ашиглаж болох
- Disk I/O хурд
- Network bandwidth

```bash
docker run --memory="512m" --cpus="1.5" nginx
```
Энэ команд nginx container-т 512MB memory, 1.5 CPU core-оос илүү ашиглахыг хориглоно — өөр container/process-ийг DoS (Denial of Service)-оос хамгаалдаг.

### Linux Capabilities
Уламжлалт Unix дээр root эсвэл root биш гэсэн хоёр л түвшин байсан. Capabilities нь root-ийн эрхийг **жижиг хэсгүүдэд хуваасан**:
- `CAP_NET_BIND_SERVICE` — 1024-с доош port дээр listen хийх эрх
- `CAP_SYS_ADMIN` — маш өргөн (бараг бүх root эрх) — **аюултай, боломжийн эсэхийг сайн бод**
- `CAP_CHOWN`, `CAP_KILL`, гэх мэт олон жижиг эрх

Docker нь container-т **default-аар зөвхөн заримыг нь** олгодог (бүх capability биш):
```bash
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx   # хамгийн бага эрхтэй ажиллуулах
```

### Seccomp, AppArmor, SELinux
- **Seccomp** — container-д зөвшөөрөгдөх syscall-уудыг white-list хийдэг (жишээ: `reboot()` syscall-ыг container дотроос дуудахыг хориглох)
- **AppArmor** — файл, эрхийн profile-based хязгаарлалт (Ubuntu-д default идэвхтэй)
- **SELinux** — RHEL/CentOS системд ашигладаг илүү нарийн mandatory access control

---

## 4. IMAGES, CONTAINERS, LAYERS

- **Image** — тогтмол template (жор шиг). Өөрчлөгддөггүй.
- **Container** — image-ээс үүссэн **ажиллаж буй instance**. Нэг image-ээс олон container үүсгэж болно.
- **Layer** — image нь давхарга давхаргаар (layer) бүтдэг. Dockerfile-ийн мөр бүр шинэ layer үүсгэдэг. Layer-ууд **cache** хийгддэг тул давхардсан build хурдан явна.

```bash
docker images          # local image-уудыг харах
docker ps -a           # бүх container (ажиллаж буй + зогссон)
docker history nginx   # image-ийн layer-уудыг харах
```

---

## 5. DOCKERFILE — ЗӨВ БИЧИХ АРГАЧЛАЛ

```dockerfile
FROM node:20-alpine                    # base image — жижиг (alpine) ашигла
WORKDIR /app                           # container доторх ажлын directory
COPY package*.json ./                  # эхлээд зөвхөн dependency файлуудыг хуулах (cache-д сайн)
RUN npm ci --only=production           # dependency суулгах
COPY . .                               # үлдсэн код хуулах
RUN adduser -D appuser && chown -R appuser /app  # non-root хэрэглэгч үүсгэх
USER appuser                           # root биш хэрэглэгчээр ажиллуулах
EXPOSE 3000
HEALTHCHECK CMD wget -q --spider http://localhost:3000/health || exit 1
CMD ["node", "server.js"]
```

**Мөр мөрөөр тайлбар:**
- `FROM` — эхлэх суурь image. **Alpine** (жижиг Linux distro) ашиглах нь attack surface-ийг багасгадаг.
- `WORKDIR` — дараагийн бүх команд энэ directory-д ажиллана.
- `COPY package*.json ./` эхэлж хуулах шалтгаан: Docker layer cache-ийг ашиглах гэсэн санаа — код өөрчлөгдөх бүрт dependency дахин суулгахгүй.
- `USER appuser` — **энэ маш чухал!** Root-оор ажиллуулбал, аюулгүй байдлын эвдрэл гарвал attacker container дотор root эрхтэй болно.
- `HEALTHCHECK` — Docker/Kubernetes-д container "эрүүл" эсэхийг мэдэгдэнэ.

**Multi-stage build** (production image-ийг жижигрүүлэх):
```dockerfile
FROM golang:1.22 AS builder
WORKDIR /src
COPY . .
RUN go build -o app

FROM scratch                    # хамгийн жижиг боломжит суурь (юу ч байхгүй)
COPY --from=builder /src/app /app
ENTRYPOINT ["/app"]
```
Энд build хийхэд хэрэгтэй бүх tool (compiler гэх мэт) эцсийн image-д орохгүй — зөвхөн эцсийн binary л орно. **Аюулгүй байдлын хувьд ч давуу тал:** attack surface хамгийн бага.

---

## 6. NETWORKING

| Network Driver | Тайлбар |
|---|---|
| `bridge` (default) | Host дээр виртуал switch үүсгэж, container-уудыг холбодог |
| `host` | Container нь host-ийн network stack-ийг шууд ашиглана (тусгаарлалт байхгүй — болгоомжтой байх) |
| `none` | Network огт байхгүй, бүрэн тусгаарлагдсан |
| `overlay` | Олон host дээрх container-ыг холбодог (Swarm/Kubernetes-д) |
| `macvlan`/`ipvlan` | Container-д физик MAC/IP хаяг өгдөг |

```bash
docker network create my-net
docker run --network=my-net --name=web nginx
docker run --network=my-net --name=db postgres
# web container-аас "db" гэдэг hostname-ээр db container руу хандаж болно (DNS-based discovery)
```

**Packet замнал (жишээ: port mapping):**
```bash
docker run -p 8080:80 nginx
```
1. Host-ийн 8080 порт руу ирсэн хүсэлт
2. Docker-ийн үүсгэсэн `iptables` NAT rule нь энэ traffic-ийг container-ийн 80 порт руу дамжуулна
3. Container-ийн `eth0` (virtual interface) руу орж, nginx хариу өгнө

---

## 7. VOLUMES & STORAGE

Container устахад дотор нь бичсэн өгөгдөл бас устана — тиймээс тогтмол өгөгдөлд **volume** хэрэгтэй:

```bash
docker volume create mydata
docker run -v mydata:/var/lib/postgresql/data postgres
```
- **Named volume** (`mydata`) — Docker удирддаг, хамгийн зөв арга
- **Bind mount** (`-v /host/path:/container/path`) — host-ийн бодит directory-г шууд холбоно (dev-д тохиромжтой, production-д болгоомжтой — host filesystem-ийг container-т нээж өгч байгаа гэсэн үг)

---

## 8. DOCKER COMPOSE

`compose.yaml`:
```yaml
services:
  web:
    build: .
    ports:
      - "8080:80"
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DB_HOST=db
    networks:
      - app-net

  db:
    image: postgres:16
    volumes:
      - dbdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
    networks:
      - app-net

networks:
  app-net:

volumes:
  dbdata:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

```bash
docker compose up -d          # бүх service-ийг background-д асаах
docker compose logs -f web    # web service-ийн log-ыг realtime харах
docker compose down           # зогсоож, network устгах (volume хэвээр үлдэнэ)
```

**Анхаарах:** нууц үг (password) шууд `environment`-д бичихгүй, `secrets` ашигла — учир нь `environment` variable-ыг `docker inspect` командаар хэн ч харж чадна.

---

## 9. АЮУЛГҮЙ БАЙДАЛ (SECURITY) — ГОЛ ХЭСЭГ

### 9.1 Docker Socket Abuse — хамгийн түгээмэл алдаа
```bash
# ЭНЭ МАШ АЮУЛТАЙ:
docker run -v /var/run/docker.sock:/var/run/docker.sock some-image
```
**Яагаад аюултай вэ:** `docker.sock`-ыг container дотор mount хийвэл, тухайн container нь host-ийн Docker daemon-той шууд харилцах чадвартай болно — өөрөөр хэлбэл, **шинэ container үүсгэж, host-ийн `/` directory-г mount хийгээд, host дээр root эрхтэй код ажиллуулж чадна**. Энэ бол container escape-ийн хамгийн энгийн бөгөөд түгээмэл арга.

**Илрүүлэх (Detection):** Falco эсвэл audit log-оор `docker.sock` mount хийсэн container-уудыг хянах.
**Урьдчилан сэргийлэх:** хэрэв заавал шаардлагатай бол (жишээ нь CI/CD dind pattern), тусгайлан хязгаарласан socket proxy ашиглах (`docker-socket-proxy`).

### 9.2 Root Container-ийн эрсдэл
Default-аар container root-оор ажилладаг. Хэрэв container дотор code injection (жишээ: web app-ийн vulnerability)-ээр attacker code ажиллуулж чадвал, тэр нь **container доторх root** эрхтэй болно. Хэрэв энэ container нь `--privileged` flag-тай эсвэл олон эрхтэй бол, host руу escape хийх магадлал нэмэгддэг.

**Хамгаалалт:**
```dockerfile
RUN adduser -D appuser
USER appuser
```
```bash
docker run --user 1000:1000 --read-only --cap-drop=ALL nginx
```
- `--read-only` — container-ийн filesystem-ийг зөвхөн уншиж болохоор хийх (malware disk дээр бичих боломжгүй болно)
- `--cap-drop=ALL` — бүх capability-г устгаж, зөвхөн хэрэгтэйг нь нэмэх

### 9.3 `--privileged` Flag — АНХААР
```bash
docker run --privileged ...   # энэ container-д HOST-ийн БҮХ device, capability-г олгоно
```
Энэ нь бараг VM-ийн тусгаарлалтыг устгаж байгаатай ижил — зөвхөн Docker-in-Docker гэх мэт маш тусгай тохиолдолд, маш болгоомжтойгоор ашиглах.

### 9.4 Image Scanning — Trivy
```bash
trivy image nginx:latest              # image дэх мэдэгдэж буй vulnerability (CVE)-г шалгах
trivy image --severity HIGH,CRITICAL myapp:latest
```
CI/CD pipeline дотор энэ шалгалтыг **build хийх бүрт автоматаар** ажиллуулах нь "shift-left security"-ийн жишээ — production-д хүрэхээс өмнө асуудлыг олох.

### 9.5 Runtime Detection — Falco
Falco нь ажиллаж буй container доторх **хэвийн бус үйлдлийг** realtime хянадаг (жишээ: container дотор shell нээгдэх, `/etc/passwd` файл руу бичих гэх мэт) — энэ нь attack эхэлсэн даруйд мэдэгдэх боломж олгодог.

### 9.6 Docker Bench for Security
```bash
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -v /var/lib:/var/lib -v /var/run/docker.sock:/var/run/docker.sock \
  docker/docker-bench-security
```
Энэ нь CIS Benchmark-ийн дагуу таны Docker тохиргоог автоматаар шалгаж, алдаануудыг жагсаадаг (Automated audit tool).

### 9.7 Rootless Docker
Docker daemon-ыг өөрийг нь root биш хэрэглэгчээр ажиллуулах горим — daemon compromise хийгдсэн ч host root эрх авахгүй.

### 9.8 Distroless Images
`gcr.io/distroless/*` — shell, package manager, гэх мэт attacker-т хэрэгтэй tool-уудыг огт агуулаагүй image. Attacker container дотор орсон ч `bash`, `sh` олдохгүй тул цаашид явахад маш хэцүү болно.

### 9.9 SBOM (Software Bill of Materials)
Image дотор ямар package, version орсон бүгдийг жагсаасан баримт — supply chain attack (жишээ: SolarWinds шиг) илрүүлэхэд чухал.

### 9.10 Хураангуй Security Checklist
```
□ Root биш хэрэглэгчээр ажиллуул (USER instruction)
□ --cap-drop=ALL, зөвхөн хэрэгтэйг нэм
□ --read-only filesystem ашигла боломжтой бол
□ docker.sock-ыг хэзээ ч untrusted container-т mount хийхгүй
□ --privileged flag зөвхөн туйлын шаардлагатай үед
□ Image-аа Trivy-ээр байнга scan хий
□ :latest tag биш, тодорхой version/digest ашигла
□ Distroless/Alpine суурь ашигла
□ Secret-ийг environment variable-д биш, Docker secrets/Vault-д хадгал
□ Falco шиг runtime monitoring нэвтрүүл
```

---

## 10. ПРАКТИК LAB-УУД

### Lab 1: Анхны container
```bash
docker run -it ubuntu bash
ps aux    # зөвхөн container-ийн process харагдана
exit
```

### Lab 2: Multi-container app (Compose)
Дээрх `compose.yaml`-ийг ашиглан:
```bash
docker compose up -d
docker compose ps
docker compose logs -f
docker compose down
```

### Lab 3: DVWA (Damn Vulnerable Web App) — тусгаарлагдсан орчинд практик
```bash
docker run -d -p 8081:80 vulnerables/web-dvwa
# http://localhost:8081 — ЗӨВХӨН өөрийн лабораторийн орчинд, интернэтэд нээлттэй биш байдлаар ашигла
```

### Lab 4: Security Scan Lab
```bash
docker pull nginx:1.19          # хуучин, vulnerability ихтэй version
trivy image nginx:1.19          # HIGH/CRITICAL vulnerability-үүдийг харах
docker pull nginx:latest
trivy image nginx:latest        # харьцуулж үзэх
```

### Lab 5: Docker Socket Abuse-ийг ойлгох (зөвхөн лабораторид!)
```bash
# ЭНЭ ЗӨВХӨН СУРАЛЦАХ ЗОРИЛГООР, ӨӨРИЙН ЛАБОРАТОРИЙН ОРЧИНД
docker run -it -v /var/run/docker.sock:/var/run/docker.sock docker:cli sh
# container дотор:
docker ps    # host-ийн container-уудыг харж байгааг анзаараарай — энэ бол escape-ийн эхлэл
```

---

## 11. TROUBLESHOOTING

| Алдаа | Учир шалтгаан | Шийдэл |
|---|---|---|
| `Cannot connect to the Docker daemon` | daemon ажиллахгүй байна | `sudo systemctl start docker` |
| `permission denied ... docker.sock` | хэрэглэгч `docker` group-д байхгүй | `sudo usermod -aG docker $USER` (Анхаар: энэ нь бараг root эрхтэй тэнцүү) |
| `port is already allocated` | тухайн port дээр өөр container/process ажиллаж байна | `docker ps` -ээр шалгаад зогсоох, эсвэл өөр port ашиглах |
| Container яг л асаад шууд унадаг (Exited 0) | Container-ийн main process дуусчихсан (foreground process байхгүй) | Dockerfile-ийн `CMD`/`ENTRYPOINT`-ийг шалгах, log харах: `docker logs <id>` |
| `no space left on device` | disk дүүрсэн (хуучин image/container хуримтлагдсан) | `docker system prune -a` |

---

## 12. KUBERNETES РУУ ШИЛЖИХ ЗАМ

Kubernetes нь container-ийг дахин зохион бүтээдэггүй — харин олон host дээр олон container-ийг **удирдах, зохион байгуулах** (orchestration) асуудлыг шийддэг:

| Docker ойлголт | Kubernetes ойлголт |
|---|---|
| `docker run` | Pod (нэг буюу хэд хэдэн container-ийн бүлэг) |
| Compose service | Deployment (Pod-уудыг удирдаж, автоматаар дахин асаадаг) |
| `-p` port mapping | Service (Pod-уудад тогтвортой сүлжээний хаяг өгдөг) |
| Docker network | Ingress + Network Policy |
| `.env` файл | ConfigMap / Secret |
| Volume | PersistentVolume |

Kubernetes дотор ч, Pod бүрийн container-ийг бодит байдал дээр **яг л containerd → runc** гэсэн ижил chain ажиллуулдаг — тиймээс энд сурсан бүх зүйл (namespace, cgroup, security) шууд хэрэг болно.

---

## 13. CHEAT SHEET — БҮХ КОМАНД НЭГ ДОР

```bash
# Image
docker pull IMAGE                    docker images
docker build -t NAME:TAG .           docker rmi IMAGE
docker history IMAGE

# Container
docker run -d -p HOST:CONT IMAGE     docker ps -a
docker exec -it CONTAINER bash       docker logs -f CONTAINER
docker stop/start/restart CONTAINER  docker rm CONTAINER
docker inspect CONTAINER

# Compose
docker compose up -d                 docker compose down
docker compose logs -f               docker compose ps

# Network
docker network create NAME           docker network ls
docker network inspect NAME

# Volume
docker volume create NAME            docker volume ls
docker volume inspect NAME

# Security
trivy image IMAGE                    docker scout cves IMAGE
docker run --rm docker/docker-bench-security

# Cleanup
docker system prune -a               docker volume prune
```

---

## 14. ЯРИЛЦЛАГЫН АСУУЛТУУД

1. Container болон VM-ийн ялгааг архитектурын түвшинд тайлбарла.
2. Namespaces болон Cgroups-ийн ялгаа юу вэ? Аль нь юуг хязгаарладаг вэ?
3. `docker.sock`-ыг container дотор mount хийх нь яагаад аюултай вэ?
4. `--privileged` flag юу хийдэг, хэзээ ашиглаж болох вэ?
5. Multi-stage build яагаад аюулгүй байдлын хувьд давуу талтай вэ?
6. Root биш хэрэглэгчээр container ажиллуулах ач холбогдол юу вэ?
7. OCI стандарт юуг шийдсэн бэ?
8. Docker Compose дахь `depends_on` болон `healthcheck`-ийн ялгаа/уялдаа юу вэ?

---

*Энэ материалыг эхнээс нь дараалан уншиж, Lab бүрийг өөрийн лабораторийн орчинд (VM/local machine) хийж үзэх нь хамгийн үр дүнтэй. Асуулт гарвал үргэлжлүүлэн асуугаарай.*
