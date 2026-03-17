OQEE :: Python 3 TEST
=====================

The main goal of this tiny test project is to fetch
the tv program guide from a remote server, parse it,
and store it in a database.

Once indexed in the database, we'll create several
function to extract data from the database with SQL.

ps: Don't use an ORM.
pps: It should not take more than 2, 3 hours to complete: keep it simple



Writing the ingest.py script
----------------------------

ingest.py should be an executable file that fetch 
the epg.xml file from https://testepg.r0ro.fr/epg.xml,
parse it and store in an `epg.sqlite` file.

Fetching the xml file
---------------------

The server uses a custom Certification Authority:

```
-----BEGIN CERTIFICATE-----
MIIDbzCCAlegAwIBAgIUTHilMcrZees/uRY+LuVa+2MegrAwDQYJKoZIhvcNAQEL
BQAwRzELMAkGA1UEBhMCRlIxFzAVBgNVBAgMDlNvbWV3aGVyZSBuaWNlMQ0wCwYD
VQQKDARUUkFYMRAwDgYDVQQDDAdUcmF4IENBMB4XDTE5MDYxMzIzMzY1OFoXDTI5
MDYxMDIzMzY1OFowRzELMAkGA1UEBhMCRlIxFzAVBgNVBAgMDlNvbWV3aGVyZSBu
aWNlMQ0wCwYDVQQKDARUUkFYMRAwDgYDVQQDDAdUcmF4IENBMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEAookji0vL8/+ok3J/pj59ckGYSHxDWzlDCaP4
Qo18f4TINzbqmIguOZxneicEKV7A+goPJJZSVsFwF58SckmHX4bK1yDoio/bUnSl
TD89M9GmvXs7EaTPSwW9vo21Dn31yrM1ZvFSNoca+RNCJj0/AODYN96TCZSYBWIv
o54XEUuxxVzaguHfqLuCFGlUxgVgzVaQICJXWaXRf+sSW3xtp2S7/Uo6DAaRDngJ
4h+bgvg357fQqIA291k1WbabCmpobrpWMmWA6lHh1Wss7yUfeoO26yr8qu6/tEpu
xbCnIoUHDO1C6y87v9nP4A29PCf69vK+lX+Ck94+T7udNCSkawIDAQABo1MwUTAd
BgNVHQ4EFgQUuhC6ZP0sImTHV1l5jtPQ6JbPpkUwHwYDVR0jBBgwFoAUuhC6ZP0s
ImTHV1l5jtPQ6JbPpkUwDwYDVR0TAQH/BAUwAwEB/zANBgkqhkiG9w0BAQsFAAOC
AQEAKtpOcMF+nXzWm1r9GXxLGfLw04oHtFnHgXPjv/62LRxYacI/z4dVJ0sDBDjl
ZWZx5UqrAObsWdPOBygE6JHp2RaOe/Ai/34FkKj7UYu75teuEasfnwW/AyPgiYlc
yHEmIcI0IjCJKzFlA3HKCG+crc02JggLAnHWenDYKgFsbcHZzRaANPCSkSzeuG90
091rHKpqqjASNtq/6w1B/zecwY8DcNs7X94FTqDKuKIwykByz7aADB4N2Gbd6EAK
l8RKV8JdbDdBZ++REng6YMrwvAkKkqMEnLy+5pcxeXQDHC0pciz+/+0DlBdCjT/Z
WUBYiZg0IgbbV8SqxOaQYK6lhw==
-----END CERTIFICATE-----
```

you should make sure ssl is properly configured when fetching the epg.

Parsing the xml file
--------------------

The xml file structure is self-explanatory, it basically consists
in a list of <program> with some attributes and sub elements.

You should insert it in a sqlite3 database with 3 tables looking like:

```sqlite
program(
    start_time datetime,
    title text,
    subtitle text,
    duration int,
    type text,
    description text
)

person(
    firstname text,
    lastname text
)

casting(
    personid int,
    programid int,
    function text
)
```

Writing the stats.py script
----------------------------

This script should open the generated `epg.sqlite` file and output:

1. the number of programs with a duration >= 10 minutes
2. the start time and the title of the program with the biggest duration on 2019-05-18
3. the first and lastname and number of programs for the 5 "Présentateur" with the most programs
4. the list of programs with 'Manuel Blanc'



How to use
-----------

1. Launch "python3 ingest.py"
2. Launch "python3 stats.py"
3. For unit test, launch "python3 -m unittest tests.py"

