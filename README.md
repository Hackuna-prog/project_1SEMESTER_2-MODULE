# project_1SEMESTER_2-MODULE
 idps with functions: parse apache logs, work with postgres, iptables, socket, Diffie Hellman key exchange and AES256

# Introduction

IDPS is an intrusion detection and prevention system. This idps was created for Unix system. Project was implemented for educational purposes!!!

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

firewalld ...
