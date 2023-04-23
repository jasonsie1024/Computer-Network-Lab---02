#! /usr/bin/env python3

from radius_admin import *
import pymysql
from datetime import datetime

def task():
    print(f"\n\nRunning Cronjob at: {datetime.now()}")

    conn = pymysql.connect(host='localhost', user='group8', password='group8', database='radius')
    cursor = conn.cursor()
    query = f"""
        SELECT username, SUM(acctsessiontime), SUM(acctinputoctets), SUM(acctoutputoctets) FROM radacct 
        WHERE acctstarttime >= now() - INTERVAL 1 DAY GROUP BY username
    """

    cursor.execute(query)
    conn.commit()

    usage = {}
    
    for username, time, volume_in, volume_out in cursor:
        usage[username] = {
                'time': time,
                'volume': volume_in + volume_out
        }

    query = f"""
        SELECT username, attribute, value from radcheck
    """
    cursor.execute(query)
    conn.commit()

    for username, attribute, value in cursor:
        if username not in usage:
            continue
        if attribute == 'Max-Daily-Session' and usage[username]['time'] >= int(value):
            kick_user(username)
            print(f'kicked {username} for exceeding daily session time')
        if attribute == 'Max-Daily-Volume' and usage[username]['volume'] >= int(value):
            kick_user(username)
            print(f'kicked {username} for exceeding daily volume')

task()
