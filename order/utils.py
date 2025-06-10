import hashlib
import hmac

def verify_hash_key(secret_key, payload, hash):
        
    hash_obj = hmac.new(secret_key.encode('utf-8'), payload, hashlib.sha256)
    generated_hash = hash_obj.hexdigest()

    if generated_hash != hash:
        return False
    return True

