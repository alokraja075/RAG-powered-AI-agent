from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hash_and_verify():
    hashed = hash_password('secret')
    assert verify_password('secret', hashed)
    assert not verify_password('wrong', hashed)


def test_jwt_roundtrip():
    token = create_access_token('1', 'test-secret', 5)
    assert decode_access_token(token, 'test-secret') == '1'
