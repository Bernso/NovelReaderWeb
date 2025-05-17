import json
import os
import gzip
import msgpack
import zstandard as zstd

# Paths
input_path = os.path.join(os.getcwd(), r"templates\novels\A Regressor’s Tale of Cultivation-chapters\chapters.json")

# Load JSON
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Helper to save and get file size
def save_and_report(path, write_func):
    full_path = os.path.join("Experiments", path)
    write_func(full_path)
    size = os.path.getsize(full_path)
    print(f"{path}: {size / 1024:.2f} KB")


# 1. Save original (pretty)
save_and_report("original.json", lambda path: open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2)))

# 2. Save minified
save_and_report("minified.json", lambda path: open(path, "w", encoding="utf-8").write(json.dumps(data, separators=(",", ":"))))

# 3. Save gzipped
def save_gzip(path):
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
save_and_report("data.json.gz", save_gzip)

# 4. Save Zstandard compressed
def save_zstd(path):
    compressor = zstd.ZstdCompressor(level=10)
    compressed = compressor.compress(json.dumps(data, separators=(",", ":")).encode("utf-8"))
    with open(path, "wb") as f:
        f.write(compressed)
save_and_report("data.json.zst", save_zstd)

# 5. Save as MessagePack
def save_msgpack(path):
    with open(path, "wb") as f:
        f.write(msgpack.packb(data))
save_and_report("data.msgpack", save_msgpack)
