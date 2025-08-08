import os

def scan_null_bytes(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                        if b'\x00' in content:
                            print(f"[!] NULL byte found in: {path}")
                except Exception as e:
                    print(f"[!] Error reading {path}: {e}")

scan_null_bytes("app")  # or "D:/pycrawler/app"
