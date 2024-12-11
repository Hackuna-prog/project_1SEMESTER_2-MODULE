# project_1SEMESTER_2-MODULE
 idps with functions: parse apache logs, work with postgres, iptables, socket, Diffie Hellman key exchange and AES256

# Introduction

IDPS is an intrusion detection and prevention system. This idps was created for Unix system. Project was implemented for educational purposes!!!

Apache log file parsing, PostgreSQL database usage, tcp server and client, Diffie Hellman key exchange and AES256 encryption-decryption have been realised. Be caruful, all these functions imply deep understanding and reqire patience during setting idps programme. Hope you can use it for fun or other projects.

To watch how it works click on mp4 video. Also thre is a screenshot of wireshark trafic with base64 key in Diffie Hellman key exchange by tcp server.

Shortly how it works: 1 module makes parsing of Apache log file and send data to PostgreSQL, 2 one analyses previous day (or other day logs, which has representative sample of server activity, including both good clients and long-term attacks), then tcp server-client connection makes Diffie Hellman key exchange between 2 and 3 modules. In 2 module bad client ipaddress is encrypted by AES256 and sended to 3 module by established connection. 3 module calls iptables to reject access to server for attacker. All modules are autonomous and nonstop.

If you want to try this programm, start by installing apache server and configure httpd.conf file:

```bash
LogFormat  "%{[%d.%m.%Y %H:%M:%S MSK]}t %h \"%u\" \"%{Host}i\"  \"%r\" %>s"  combined
```

Then install PostgreSQL database. Create public.prev_day and public.realtime tables. And provide rights to user "t" with password "12345"

```bash
su - postgres
```

```bash
psql
```

```bash
create role t with password '12345';
```

```bash
create table prev_day (ip text, err integer, time integer, cnt_requests integer, cnt_errors integer, errors_div_all real);
```

```bash
grant insert, select, update, delete on prev_day to t;
```

```bash
create table realtime (ip text, err integer, time integer, cnt_requests integer, cnt_errors integer, errors_div_all real);
```

```bash
grant insert, select, update, delete on realtime to t;
```

To empty table:
```bash
truncate table public.prev_day ;
```
Don't forget about using ";" symbol! Save your nerves!


## Installation requirements

Use [pip](https://pypi.org/project/py-diffie-hellman/) to install Python implementation of the Diffie-Hellman key exchange protocol:
```bash
pip install py-diffie-hellman
```

Use [pip](https://pypi.org/project/cryptography/41.0.7/) to install Python module implementation of AES256:
```bash
pip install crypto
```

Use [pip](https://pypi.org/project/numpy/) to install scientific computing with Python:
```bash
pip install numpy
```

Use [pip](https://pypi.org/project/pandas/) to install dataframe support:
```bash
pip install pandas
```

Use [pip](https://pypi.org/project/psycopg2-binary/) to install PostgreSQL database adapter for the Python:
```bash
pip install psycopg2-binary
```


## About contribution and possible problems during usage

By default, some built-in Linux firewall blocks apache traffic. To allow access use the following commands firewall-cmd:
```bash
firewall-cmd --zone=public --permanent --add-service=http
```

```bash
firewall-cmd --zone=public --permanent --add-service=https
```

```bash
firewall-cmd - -reload
```

To look at the iptables rules:
```bash
iptables -L
```

To delete all iptables rules:
```bash
iptables -F
```

To make your possible debug process easer, I recommend you using Wireshark, because all ntp server-client functions here: key exchange, sending and receiving ip-addresses are in base64.



Again: Project was implemented for educational purposes!!! 
