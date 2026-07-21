enc = "7iyx_y9kdtyk_jo$uu"
flag_prefix = "HZ2025{"  # known format

# Try simple XOR key brute-force
for key in range(1, 256):
    dec = ''.join([chr(ord(c) ^ key) for c in enc])
    if dec.startswith(flag_prefix[6:]):  # skip "HZ2025{" prefix
        print(f"Key {key}: HZ2025{{{dec}}}")
