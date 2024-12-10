import os
import time
import datetime
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from ipaddress import ip_address




def check_the_spelling(item_ip, item_err, item_time):
    #проверка на валидность IP-адреса, ошибки и времени
    try:
        ip_address(item_ip)
        int(item_err)
        item_time = int(item_time)
        if item_time < 0:
            return 1
        return 0
    except:
        return 1


def error_check(error):
    #статус запроса считается ошибкой, если он 302 либо больше или равен 400
    if error >= 400 or error == 302:
        return 1
    return 0


def string_splitter(item):
    try :
        t = item.split()
        b = t[0][1:] + ' ' + t[1]
        a = datetime.datetime.strptime(b, '%d.%m.%Y %H:%M:%S')
        item_time = int(datetime.datetime.timestamp(a))
    except:
        return 1

    if len(t) >= 12:
        if check_the_spelling(t[3], t[11], item_time) == 0:       
            item_ip = t[3]
            item_err = int(t[11])
            return item_ip, item_err, item_time
    return 1


def Analyze_prev_day(FILENAME_PREV_DAY, TIMER):
    last_time = 0 #переменная, в которой хранится значение начала отсчёта времени, после TIMER секунд она обновляется

    grafic_fr = pd.DataFrame(columns = ["ip", "err", "time", "cnt_requests", "cnt_errors","errors_div_all"]) #хранит все значения
    main_data_fr = pd.DataFrame(columns = ["ip", "err", "time", "cnt_requests", "cnt_errors"]) #содержит данные за TIMER секунд

    access_log = open(FILENAME_PREV_DAY, mode='r', encoding= 'utf8', errors='ignore') 

    for item in access_log.readlines():
        
        if string_splitter(item) != 1:
            item_ip, item_err, item_time = string_splitter(item)    
            
            if_error = error_check(item_err) 

            if last_time == 0:
                last_time = item_time

            if item_time - last_time >= TIMER:
                main_data_fr = main_data_fr.assign(errors_div_all = main_data_fr["cnt_errors"] / main_data_fr["cnt_requests"] * 100)
                grafic_fr = pd.concat([grafic_fr, main_data_fr], ignore_index=True)
                main_data_fr = pd.DataFrame(columns = ["ip","err", "time", "cnt_requests", "cnt_errors"])
                last_time = item_time   

            try:
                main_data_fr.at[item_ip, "cnt_requests"] += 1   

                if if_error == 1:                
                    main_data_fr.at[item_ip, "cnt_errors"] += 1

            except:
                temp_data_df =  pd.DataFrame([[item_ip, item_err, item_time, 1, if_error]],columns = ["ip", "err", "time", "cnt_requests", "cnt_errors"], \
                    index=[item_ip])
                main_data_fr = pd.concat([main_data_fr, temp_data_df])

        
    if item_time - last_time >= TIMER:
        grafic_fr = pd.concat([grafic_fr, main_data_fr], ignore_index=True)

      
    #устанавливается соединение с postgresql, удаляются возможные данные и добавляются обработанные
    connection = psycopg2.connect(dbname = 'postgres', host = '127.0.0.1', user = 't', password = '12345', port = '5432')
    cur = connection.cursor()

    cur.execute('truncate table prev_day')

    for index, row in grafic_fr.iterrows():
        cur.execute('insert into prev_day (ip, err, time, cnt_requests, cnt_errors, errors_div_all) values (%s, %s, %s, %s, %s, %s)', \
            (row['ip'], row['err'], row['time'], row['cnt_requests'], row['cnt_errors'], row['errors_div_all']))

    connection.commit()
    connection.close()

    access_log.close()
 

def Analyze_realtime(FILENAME_REALTIME, TIMER):
    fd = -1 
    last_time = 0
    
            

    grafic_fr = pd.DataFrame(columns = ["ip", "err", "time", "cnt_requests", "cnt_errors","errors_div_all"])
    main_data_fr = pd.DataFrame(columns = ["ip", "err", "time", "cnt_requests", "cnt_errors"])

    while True:
        #открываем файл, и запоминаем его дескриптор и инод
        if (fd < 0): 
            while(fd < 0):
                access_log = open(FILENAME_REALTIME, mode='r', encoding= 'utf8', errors='ignore')
                fd = access_log.fileno()
                inode = os.stat(fd).st_ino

        line = access_log.read().split('\n')  
        
        #если данные для прочтения пустые, вероятно файл был удалён или apache создал новый файл для логов после перезаполения памяти в текущем
        if line == ['']:
            new_fd = access_log.fileno()
            if os.stat(new_fd).st_ino != inode:
                access_log.close()
                os.close(fd)
        #если данные есть, начинаем парсинг
        else:
            for item in line:           
                #при закрытии файл, иногда каретка переноса строки \r переносится на строку с EOF, и при следующей дозаписи, последняя и новая строки сливаются
                if item == '':
                    continue
                if string_splitter(item) != 1:
                    item_ip, item_err, item_time = string_splitter(item)
                    
                    if last_time == 0:
                        last_time = item_time

                    if_error = error_check(item_err) 
                    
                    try:
                        main_data_fr.at[item_ip, "cnt_requests"] += 1   

                        if if_error == 1:                
                            main_data_fr.at[item_ip, "cnt_errors"] += 1

                    except:
                        temp_data_df =  pd.DataFrame([[item_ip, item_err, item_time, 1, if_error]],columns = ["ip", "err", "time", "cnt_requests", "cnt_errors"], index=[item_ip])
                        main_data_fr = pd.concat([main_data_fr, temp_data_df])
        

        if int(time.time()) - last_time >= TIMER:
            main_data_fr = main_data_fr.assign(errors_div_all = main_data_fr["cnt_errors"] / main_data_fr["cnt_requests"] * 100)
            grafic_fr = pd.concat([grafic_fr, main_data_fr], ignore_index=True)
            print('TIMER seconds spent. add new data to postgres')
            

            connection = psycopg2.connect(dbname = 'postgres', host = '127.0.0.1', user = 't', password = '12345', port = '5432')

            cur = connection.cursor()
    
            for index, row in grafic_fr.iterrows():
                cur.execute('insert into realtime (ip, err, time, cnt_requests, cnt_errors, errors_div_all) values (%s, %s, %s, %s, %s, %s)', \
                    (row['ip'], row['err'], row['time'], row['cnt_requests'], row['cnt_errors'], row['errors_div_all']))


            connection.commit()
            connection.close()
          

            main_data_fr = pd.DataFrame(columns = ["ip","err", "time", "cnt_requests", "cnt_errors"])
            grafic_fr = pd.DataFrame(columns = ["ip", "err", "time", "cnt_requests", "cnt_errors","errors_div_all"])
            last_time = int(time.time())





def main():

    print("Parse previous day log file\n")
    print("Enter file name with previous day logs or press 1, if path is /etc/httpd/logs/www.f.ru_access.log\n")

    FILENAME_PREV_DAY = input()
    if FILENAME_PREV_DAY == "1":
        FILENAME_PREV_DAY = "/etc/httpd/logs/www.f.ru_access.log"


    TIMER = 600
    Analyze_prev_day(FILENAME_PREV_DAY, TIMER)
    print('\nparsing finish with success\n')




    print("\nAnalyze realtime logs\n")
    print("Enter file name with current day logs or press 1, if path is /var/log/httpd/access_log\n")

    FILENAME_REALTIME = input()
    if FILENAME_REALTIME == "1":
        FILENAME_REALTIME = "/var/log/httpd/access_log"


    print("Enter pereiod of seconds\n")
    #TIMER = 11
    TIMER = int(input())
    Analyze_realtime(FILENAME_REALTIME, TIMER)


if __name__ == "__main__":
    main()