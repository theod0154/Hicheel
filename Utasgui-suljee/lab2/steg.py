from PIL import Image
from sympy import primerange
import re

# PNG доторх LSB prime-index bits унших функц
def extract_primes_lsb(img_path):
    img = Image.open(img_path).convert("RGB")
    pixels = list(img.getdata())
    bits = []

    values = []
    for r, g, b in pixels:
        values.extend([r, g, b])

    primes = list(primerange(0, len(values)))
    for i in primes:
        bits.append(values[i] & 1)

    # Bits → бүх ASCII
    chars = []
    for b in range(0, len(bits)-7, 8):
        byte = bits[b:b+8]
        val = int("".join(map(str, byte)), 2)
        try:
            chars.append(chr(val))
        except:
            chars.append("?")

    text = "".join(chars)
    return text

# --- Main ---
text = extract_primes_lsb("/home/theod/Desktop/chall.png")

# Flag хайх
m = re.search(r'ccsCTF\{.*?\}', text)
if m:
    print("[+] Flag found:", m.group())
else:
    print("[!] Flag олдсонгүй, эхний 500 тэмдэгтийг харуулна:")
    print(text[:500])
