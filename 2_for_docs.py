import time
import psycopg2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from diffiehellman import DiffieHellman
import socket
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding



def Cluster_analyse_prev_day():
    '''Function analyses data from postgres table public.prev_day, find threshold value for good clients.

    :param connection: connetion to postgresql data
    :type connection: connection data

    :param cur: connection cursor
    :type cur: connection cursor

    :param df: dataframe with x and y values
    :type df: dataframe

    :param table: table with the number of entries as an ordered list
    :type table: tuples list

    :param new_row: one tuple from table
    :type new_row: tuple

    :param threshold_distance: critical radius-vector, calculated as median
    :type threshold_distance: float

    :param colors: dictionary with colors: good clients are blue, bad - red
    :type colors: dictionary
    
    :param threshold_distance: critical radius-vector, calculated as median
    :type threshold_distance: float
    '''
    #устанавливается соединение к postgresql и считываются данные
    connection = psycopg2.connect(dbname = 'postgres', host = '127.0.0.1', user = 't', password = '12345', port = '5432')
    cur = connection.cursor()

    cur.execute('SELECT errors_div_all, cnt_requests FROM prev_day')
    table = cur.fetchall()

    df = pd.DataFrame(columns = ["errors_div_all", "cnt_requests"])

    for row in table:
        new_row = pd.DataFrame([[row[0], row[1]]], columns = ["errors_div_all", "cnt_requests"])
        df = pd.concat([df, new_row], ignore_index=True)

    print(df)

    df = df.assign(distance = np.float_power(   (df['cnt_requests']**2).astype(np.float32) + np.float_power(df['errors_div_all'], 2)  , 0.5 )  )
    
    #предельное заначение для легитимного повдения на основании приведённых данных определяюся медианой
    threshold_distance = df['distance'].median() 
    df = df.assign(cluster = np.where(df['distance'] <= threshold_distance, 0, 1))

    colors = {0: 'blue', 1: 'red'}

    for cluster_name, group in df.groupby('cluster'):
        plt.scatter(group['cnt_requests'], group['errors_div_all'], color=colors[cluster_name])


    plt.xlabel('Количество всех запросов')
    plt.ylabel('Процент нелегитимных запросов')
    plt.legend(['good clients','bad clients'])
    plt.show() #закоментируйте эту строку для продожения анализа без графика

    return(threshold_distance)

def aes_encryption(ip_addr, key): 
    '''AES256 encryption with constat vector and key from Diffie Hellman key exchange. Returns encrypted ip-adress.

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

    :param padder: aes256 block
    :type padder: cryptography object

    :param padded_data: ip_addr in block, lenght = 16 * k, k is Natural number
    :type padded_data: cryptography object

    :param ct: encrypted ip_addr
    :type ct: base64 string
    '''  
    #AES256 шифрование строки из IP-адреса
    iv =  b'X\x8f(\xcfx\xd5\x92>\xe6\xd3D\xf1\x02,u\x10'
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(256).padder()
    padded_data = padder.update(ip_addr) + padder.finalize()
    ct = encryptor.update(padded_data) + encryptor.finalize()

    
    return ct



def start_socket(attacker_ip):
    '''start client socket, makes Diffie Hellman key exchange and send encrypted ip-address.

    :param sock: socket
    :type sock: socket

    :param attacker_ip: ip-address
    :type attacker_ip: string

    :param dh1: private and public keys, other data for Diffie Hellman algorith
    :type sock: diffiehellman object

    :param dh1_public_base02: client socket public key in bytes
    :type dh1_public_base02: bytes string

    :param dh1_public_base64: client socket public key in base64
    :type dh1_public_base64: string in base64

    :param dh2_public_base64: server socket public key in base64
    :type dh2_public_base64: string in base64

    :param dh2_public_base02: server socket public key in bytes
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
    #сокет-клиент
    sock_port = 10001

    sock = socket.socket()
    sock.connect(('127.0.0.1', sock_port))

    dh1 = DiffieHellman(group=14, key_bits=256)
    dh1_public_base02 = dh1.get_public_key()
    dh1_public_base64 = b64encode(dh1_public_base02)

    sock.sendall(dh1_public_base64)

    dh2_public_base64 = sock.recv(1600)

    #print(f'dh1_public {dh1_public_base64} \n')
    #print(f'dh2_public  {dh2_public_base64} \n')

    dh2_public_base02 = b64decode(dh2_public_base64)
    dh1_shared_base02 = dh1.generate_shared_key(dh2_public_base02)
    dh1_shared_base64 = b64encode(dh1_shared_base02)
    #print('final key 1:     ', dh1_shared_base64)


    key = dh1_shared_base64[:32]
    ip_addr = attacker_ip.encode("utf-8")        
    ct = aes_encryption(ip_addr, key)
    

    sock.sendall(ct)
    sock.close()
    return 0


def Cluster_analyse_realtime(timestart, timeend, threshold_distance):
    '''start client socket, makes Diffie Hellman key exchange and send encrypted ip-address.

    :param timestart: time when timer starts
    :type timestart: integer
    
    :param timeend: time when timer ends
    :type timeend: integer

    :param threshold_distance: critical radius-vector, calculated as median
    :type threshold_distance: float

    param connection: connetion to postgresql data
    :type connection: connection data

    :param cur: connection cursor
    :type cur: connection cursor

    :param df: dataframe with x and y values
    :type df: dataframe

    :param row: one tuple from table
    :type row: tuple

    :param table: table with the number of entries as an ordered list
    :type table: tuples list

    :param ip_adress: ip-address from postgress sql
    :type ip_adress: string
    '''
    #Delete this 3 strings:
    timestart  = 0
    timeend = 10**10
    threshold_distance = 90
    #
    connection = psycopg2.connect(dbname = 'postgres', host = '127.0.0.1', user = 't', password = '12345', port = '5432')
    cur = connection.cursor()

    cur.execute(f'SELECT ip, errors_div_all, cnt_requests FROM realtime WHERE ({timestart} <= time) AND (time <= {timeend})')
    table = cur.fetchall()

    df = pd.DataFrame(columns = ["errors_div_all", "cnt_requests"])

    for row in table:
        if (row[2]**2 +row[1]**2) ** 0.5 >= threshold_distance:
            ip_adress = row[0]
            print('ip: ', ip_adress)
            start_socket(ip_adress)
   

def main():
    '''main function to start the programm

    :param threshold_distance: critical radius-vector, calculated as median
    :type threshold_distance: float

    :param last_time: time when timer starts
    :type last_time: integer
    '''
    print('Cluster analyse previous day\nstart')
    threshold_distance = Cluster_analyse_prev_day()
    print('finish')
    print('get threshold_distance = ', threshold_distance)






    print('enter TIMER seconds - period of sending data to block by iptables')
    TIMER = int(input())
    last_time = int(time.time())
    #TIMER = 6

    while True:
        if int(time.time()) - last_time >= TIMER:
            Cluster_analyse_realtime(last_time, last_time + TIMER, threshold_distance)
            print('spent ', TIMER, ' seconds')
            last_time = int(time.time())


if __name__ == "__main__":
    main()