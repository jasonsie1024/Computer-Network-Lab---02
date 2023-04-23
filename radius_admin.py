import logging
import pymysql
from pyrad.client import Client
from pyrad.dictionary import Dictionary
from pyrad.packet import * #  AccessRequest, AccountingRequest

# 設置日誌紀錄
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)-8s] %(message)s')

# RADIUS 服務器配置
server = "192.168.1.1"
secret = b"testing123"

# 創建 RADIUS 客戶端
# d.attributes = {"User-Name": "username", 'Acct-Session-Id': "aid", 'Acct-Termination_Cause': "atc"}
client = Client(server=server, secret=secret, dict=Dictionary("dictionary"))

def get_user_stats(username, password="howhow"):
    # 創建 AccessRequest 包
    request = client.CreateAuthPacket(code=AccessRequest, User_Name=username)
   # request["User-Password"] = request.PwCrypt(password)

    # 發送 AccessRequest，並等待回應
    try:
        response = client.SendPacket(request)
    except Exception as e:
        print("Error: ", e)
        return None

    # 解析回應
    if response.code == AccessRequest:
        session_time = response.get("Acct-Session-Time")
        input_octets = response.get("Acct-Input-Octets")
        output_octets = response.get("Acct-Output-Octets")

        return {
            "username": username,
            "session_time": session_time,
            "input_octets": input_octets,
            "output_octets": output_octets
        }
    else:
        print("Error: Authentication failed.")
        return None

import time
def kick_user(username):
    conn = pymysql.connect(host='localhost', user='group8', password='group8', database='radius')
    cursor = conn.cursor()
    query = f"SELECT acctsessionid FROM radacct WHERE username='{username}' ORDER BY acctstarttime DESC limit 5"
    client.timeout = 30 
    cursor.execute(query)
    conn.commit()
    for sid in cursor:
        print(sid)
        pkt = client.CreateCoAPacket(code=DisconnectRequest, User_Name=username)
        # print(pkt.dict.attributes)
        # pkt['User-Name'] = username
        # pkt['Acct-Session-Id'] = sid
        # pkt['Acct-Terminate-Cause'] = 'User-Request'
        # pkt['NAS-Identifier'] ="localhost"
        # pkt['Event-Timestamp'] = int(time.time())
        response = client.SendPacket(pkt)
    return True


def get_admin_account():
    # get the account and password of radius admin
    admin_username = 'dd'
    admin_password = 'dd'
    return admin_username, admin_password
if __name__ == "__main__":
    # 測試
    username = "group8"
    password = "group8"
    kick_user('howhow')
    '''
    user_stats = get_user_stats(username, password)
    if user_stats:
        print("User stats:")
        print("Username: ", user_stats["username"])
        print("Session time: ", user_stats["session_time"])
        print("Input octets: ", user_stats["input_octets"])
        print("Output octets: ", user_stats["output_octets"])
    '''
