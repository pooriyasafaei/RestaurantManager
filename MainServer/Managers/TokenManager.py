import jwt
from datetime import datetime
import psycopg2


JWT_SECRET = ""
database_password = ""
database_name = ""
JWT_ALGORITHM = ""
token_version = 1.0


class TokenManager:
    def __init__(self, secret, input_database_name, input_database_password):
        global JWT_ALGORITHM
        global JWT_SECRET
        global database_password
        global database_name

        self.JWT_SECRET = secret
        JWT_SECRET = secret
        self.database_name = input_database_name
        database_name = input_database_name
        self.database_password = input_database_password
        database_password = input_database_password
        self.JWT_SECRET = secret
        JWT_SECRET = secret
        self.JWT_ALGORITHM = 'HS256'
        JWT_ALGORITHM = 'HS256'
        self.JWT_EXP_DELTA_HOURS = 1024

    @staticmethod
    def user_id_to_token(user_id, activation, token_level="User"):
        global JWT_ALGORITHM
        global JWT_SECRET

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        payload = {
            'activation': activation,
            'user_id': user_id,
            'identifier': now_datetime,
            'token_version': token_version,
            'token_creator': "System",
            'token_level': token_level,
            'token_owner': "GavaznHa"
        }
        jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
        token = jwt_token
        return token

    @staticmethod
    def token_to_user_id(token, is_admin=False, can_deactive=False, permission=""):
        global JWT_ALGORITHM
        global JWT_SECRET
        farsi_message = "توکن نامعتبر است."
        english_message = "wrong token"

        if token == "":
            return result_sender(401, farsi_message="توکن نامعتبر است", english_message="Wrong token.")
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except Exception as e:
            farsi_message = str(e)
            english_message = str(e)
            return result_sender(401, farsi_message, english_message)

        if is_admin:
            if TokenManager.check_permission(payload["user_id"], permission):
                if payload["token_level"] == "Admin":
                    return result_sender(0, data=payload)
                else:
                    return result_sender(401, farsi_message, english_message)
            else:
                return result_sender(401, farsi_message, english_message)

        if can_deactive:
            return result_sender(0, data=payload)
        else:
            if payload["activation"]:
                return result_sender(0, data=payload)

        return result_sender(401, farsi_message, english_message)
    
    @staticmethod
    def check_permission(admin_id, permission):
        global database_password
        global database_name

        conn = psycopg2.connect(host="localhost", database=database_name, user='postgres',
                                password=database_password)
        cur = conn.cursor()
        cur.callproc('admins_manager_check_permission', [admin_id, permission])
        result = cur.fetchall()[0][0]
        conn.close()
        if result == 0:
            return True
        else:
            return False


def result_sender(code, farsi_message="", english_message="", data=None):
    if code == 0:
        status = "OK"
    else:
        status = "failure"
    result = {
        "status": status,
        "code": code,
        "farsi_message": farsi_message,
        "english_message": english_message,
        "data": data
    }
    return result
