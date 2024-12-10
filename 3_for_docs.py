import os
import socket
import sys
from diffiehellman import DiffieHellman
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding



def aes_decryption(ct, key):
    '''AES256 decryption with constat vector and key from Diffie Hellman key exchange. Returns encrypted ip-adress.

    :param iv: constant vector
    :type iv: bytes string

    :param ip_addr: ip-address
    :type ip_addr: string

    :param key: key after Diffie Hellman exchange
    :type key: string

    :param cipher: cryptography object data
    :type cipher: cryptography object

    :param encryptor: cryptography object encryption data 
    :type encryptor: cryptography object

    :param unpadder: aes256 block
    :type unpadder: cryptography object

    :param padded_data: ip_addr in block, lenght = 16 * k, k is Natural number
    :type padded_data: cryptography object

    :param data: decrypted ip_addr
    :type data: base64 string

    :param ct: encrypted ip_addr
    :type ct: base64 string
    '''  
    #AES256 дишифрование
    iv =  b'X\x8f(\xcfx\xd5\x92>\xe6\xd3D\xf1\x02,u\x10'
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ct) + decryptor.finalize()
    unpadder = padding.PKCS7(256).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    return data


def block_ip(attacker_ip):
    '''function fork process and block ip-address calling os execl with iptables

    :param pid: new process pid
    :type pid: integer

    :param attacker_ip: ip-address
    :type attacker_ip: string
    '''
    #блокировка IP-адреса в отдельном процессе
    pid = os.fork()
    if pid == 0:
        os.execl("/usr/sbin/iptables", "iptables", "-I", "INPUT", "1", "--src", attacker_ip, "-j", "REJECT")
        #print(f'{attacker_ip} has been blocked by itertools.')
        return 0
    else:
        return -1

    os.wait()


def main():
    '''main function starts server socket, makes Diffie Hellman key exchange and send decrypted ip-address in iptables

    :param sock: socket
    :type sock: socket

    :param server_address: server ip-address and port
    :type server_address: tuple

    :param sock_port: server socket port
    :type sock_port: integer

    :param dh1: private and public keys, other data for Diffie Hellman algorith
    :type sock: diffiehellman object

    :param dh2_public_base02: client socket public key in bytes
    :type dh1_public_base02: bytes string

    :param dh2_public_base64: client socket public key in base64
    :type dh1_public_base64: string in base64

    :param dh1_public_base64: server socket public key in base64
    :type dh2_public_base64: string in base64

    :param dh1_public_base02: server socket public key in bytes
    :type dh2_public_base02: bytes string

    :param dh1_shared_base02: client socket key after exchange in bytes
    :type dh1_shared_base02: bytes string

    :param dh1_shared_base64: client socket key after exchange in bytes
    :type dh1_shared_base64: string in base64

    :param key: for aes256 key must be length 32
    :type key: string

    :param ip_addr: ip-address in bytes
    :type ip_addr: string

    :param ct: ip-address after aes256 encryption
    :type ct: string

    :param sock_port: socket port in constant
    :type sock_port: integer
    '''

    #программа является сокетов-сервером
    sock_port = 10001
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', sock_port)
    sock.bind(server_address)
    sock.listen(1)

    #обмен ключами по Diffie Hellman
    dh2 = DiffieHellman(group=14, key_bits=256)
    dh2_public_base02 = dh2.get_public_key()
    dh2_public_base64 = b64encode(dh2_public_base02)




    while True:
        print('waiting for a connection')
        connection, client_address = sock.accept()
        try:        

            while True:
                dh1_public_base64 = connection.recv(1600)

                if dh1_public_base64:
                    connection.sendall(dh2_public_base64)              
                    
                    #print(f'dh1_public {dh1_public_base64} \n')
                    #print(f'dh2_public  {dh2_public_base64} \n')

                    dh1_public_base02 = b64decode(dh1_public_base64)
                    dh2_shared_base02 = dh2.generate_shared_key(dh1_public_base02)                
                    dh2_shared_base64 = b64encode(dh2_shared_base02)
                    #print('final key:     ', dh2_shared_base64)
                    
                    key = dh2_shared_base64[:32]

                    
                    ct = connection.recv(1600)

                    #print('gett ', ct)

                    ip_addr = aes_decryption(ct, key)
                    ip_addr = ip_addr.decode("utf-8") 
                    #print('get back:  ', ip_addr)
                    block_ip(ip_addr)

                    print(ip_addr, 'have been blocked!')
                    
                else:
                    #print('no data from', client_address)
                    break
                
        finally:
            # Clean up the connection
            connection.close()

if __name__ == "__main__":
    main()