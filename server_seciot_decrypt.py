import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from paho.mqtt import client as mqtt_client
import random
from Crypto.Random import get_random_bytes
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


# AES key
key = b'\x02\x01\x05\x02\x00\x04\x08\x05' * 4
cred = credentials.Certificate("appdacn-1b69f-firebase-adminsdk-1z5tx-3ff1703965.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
iv = get_random_bytes(AES.block_size)
# ========================Init=======================================

# list_account=[]
# list_id=[]

list_account=['3@gmail.com', '12@gmail.com', '21520485@gm.uit.edu.vn', 'lory265265@gmail.com', '1a@gmail.com', '123@gmail.com']
list_id=['Fy6MXVmrtfY99UtKfeoFCqIuMbL2', 'H09YI4a47DW1FqseIUYtWtdbNOh2', 'Y4G2Fkx4VKaTpxv7xkwvlTTArsF3', 'gTt4CW1WkAVfIWxVcTJEyQ1Akwi2', 'm4cwB9K3olRW5hFEHfDp2sNkVcr1', 'vbxPo6oZbbUiEmVBkLG987raLJE2']
print(list_account)


mqtt_username = "nt535o21_nhom1"
mqtt_password = "123456"
# ====================lấy id từ firebase=========================
# docs_ref = db.collection("users").stream()
# for doc in docs_ref:
#     list_account.append(doc._data.get('gmail'))
#     list_id.append(doc.id)
# print(list_account)
# print(list_id)
# ===============================================================
def on_connect(client, userdata, flags, rc,version):
    print("Connected with result code "+str(rc))
    for email in list_account:
        topic = f"{email}"
        print(f"Subscribing to topic: {topic}")
        client.subscribe(topic)
    print("========================================")

def on_message(client, userdata, msg):
    # print(f"Received message on topic {msg.topic}: {msg.payload}")
    #
    # cipher_data = msg.payload
    # print("Encrypted data:", cipher_data.hex())
    #
    # print(type(cipher_data))
    # decrypted_data = decrypt(cipher_data)
    # print("Decrypted data:", decrypted_data.hex())
    # print("Decrypted data:", decrypted_data.decode())
    try:
        start_time = time.time()
        print(f"Received message on topic {msg.topic}: {msg.payload}")
        cipher_data = msg.payload
        print("Encrypted data:", cipher_data.hex())
        print(type(cipher_data))
        decrypted_data = decrypt(cipher_data)
        print("Decrypted data(hex):", decrypted_data.hex())
        print("Decrypted data(decode):", decrypted_data.decode())
        s= decrypted_data.decode()
        arr=s.split("/")
        arr[1]=arr[1].replace(" ","")
        alert='0'
        if((int(arr[0])<60 or int(arr[0])>100)and arr[1]=="0"):
            alert='1'
        print(arr)
        if(int(arr[0])<300 and int(arr[0])>0):
            data = {
                "data": int(arr[0]),
                "status": str(arr[1]),
                "alert":alert
            }
            index=0
            for i in range(len(list_account)):
                if(list_account[i]==msg.topic):
                   index=i
                   break
            doc_ref = db.collection("Iot").document(list_id[index])
            doc_ref.update(data)
            print("Update dữ liệu lên id: "+list_id[index] )
            time.sleep(1)

            end_time = time.time()
            # Tính thời gian thực thi
            execution_time = end_time - start_time
            print("Thời gian thực thi:", execution_time, "giây")
            print("=========================================================")
    except Exception as e:
        print("lỗi "+ e)

def decrypt(ciphertext):
    cipher = AES.new(key, AES.MODE_ECB)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

# ====================================================================================

client_id = f'python-mqtt-{random.randint(0, 1000)}'
client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2,client_id)
client.username_pw_set(mqtt_username, mqtt_password)
client.connect("192.168.45.90", 1883)
client.on_message = on_message
client.on_connect = on_connect
client.loop_forever()
