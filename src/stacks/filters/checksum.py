import hashlib


def md5(ctx, string):
    return hashlib.md5(string.encode()).hexdigest()


def sha1(ctx, string):
    return hashlib.sha1(string.encode()).hexdigest()


def sha256(ctx, string):
    return hashlib.sha256(string.encode()).hexdigest()


def sha512(ctx, string):
    return hashlib.sha512(string.encode()).hexdigest()
