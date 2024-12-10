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





sock_port = 10001

def Cluster_analyse_prev_day():
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
    #AES256 шифрование строки из IP-адреса
    iv =  b'X\x8f(\xcfx\xd5\x92>\xe6\xd3D\xf1\x02,u\x10'
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(256).padder()
    padded_data = padder.update(ip_addr) + padder.finalize()
    ct = encryptor.update(padded_data) + encryptor.finalize()

    
    return ct



def start_socket(attacker_ip):
    #сокет-клиент
    
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