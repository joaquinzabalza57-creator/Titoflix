with open('.env', 'rb') as f:
    raw = f.read()
    
print("Raw bytes:")
print(repr(raw))
print()
print("Content as UTF-8 (may show errors):")
try:
    print(raw.decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
print()
print("Content as Latin-1:")
print(raw.decode('latin-1'))
print()
print("Byte at position 85:")
if len(raw) > 85:
    print(f"0x{raw[85]:02x} = '{chr(raw[85])}'")
