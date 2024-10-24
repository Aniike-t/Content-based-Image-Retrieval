import hashlib

def calculate_file_hash(file_stream):
    """Calculate the file hash using SHA-256."""
    sha256_hash = hashlib.sha256()
    file_stream.seek(0)  # Ensure the stream is at the beginning
    for byte_block in iter(lambda: file_stream.read(4096), b""):
        sha256_hash.update(byte_block)
    file_stream.seek(0)  # Reset stream again after hashing
    return sha256_hash.hexdigest()