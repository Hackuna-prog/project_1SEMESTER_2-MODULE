import pytest
from idps_1_mod import check_the_spelling
from idps_1_mod import error_check
from idps_1_mod import string_splitter
from idps_2_mod import aes_encryption
from idps_3_mod import aes_decryption



def test_1_validation():
    assert(check_the_spelling("123.4.5.6", 200, 1731198673) == 0)

def test_2_validation():
    assert(check_the_spelling("12345.5.5.5", 200, 1731198673) == 1)

def test_3_if_error():
    assert(error_check(-1) == 0)

def test_4_if_error():
    assert(error_check(404) == 1)

def test_5_check_strings_concatination():
    assert(string_splitter(f'[30.11.2024 21:30:29 MSK] 10.193.88.8 "-" "10.193.95.108" - --- "GET / HTTP/1.1" 401 381 1192 "-" "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/27.0 Chrome/125.0.0.0 Mobile Safari/537.36" "-"') == ('10.193.88.8', 401, 1732991429))

def test_6_check_strings_concatination():
    assert(string_splitter(f'[30.11.2024 21:30:29 MSK] 10.193.888 "-" "10.193.95.108" - --- "GET / HTTP/1.1" 401 381 1192 "-" "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/27.0 Chrome/125.0.0.0 Mobile Safari/537.36" "-"') == 1)

def test_7_aes_encryption():
    assert(aes_encryption(b"123.4.5.6", b'4Mz7g79VL8gx1b2m5mgihx2/EJxMQjkl') == b'\xee\xff|\x80\x91\xd4)y\xd2\xec\xd3\xa0+\x81\x13\xa6\xd1R\xc6$\xe8a$\xf1\x8d>\xbb\xa0\x1eA\x96?')

def test_8_aes_encryption():
    with pytest.raises(TypeError):
        aes_encryption("123.4.5.6", b'4Mz7g79VL8gx1b2m5mgihx2/EJxMQjkl')

def test_9_aes_decryption():
    assert(aes_decryption(b'm\xab\x08\xbc\xfex\xbc\x87\x8e\xae\xb2\xc9F\xd0c\x0f\xdc\xd2g\xf7\xd3\xde\x14!\x8a\xe1A=\xefL\xf5\xc4', b'Rfr3AjcHTew0Pw/OpDPTXUEYgm9Zq1pU') == b'10.193.91.118')

def test_10_aes_decryption():
    with pytest.raises(TypeError):
        aes_decryption("123.4.5.600", b'4Mz7g79VL8gx1b2m5mgihx2/EJxMQjkl')

