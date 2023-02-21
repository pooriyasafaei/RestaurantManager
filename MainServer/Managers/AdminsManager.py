# coding=utf-8

import json
import psycopg2
from psycopg2.extras import RealDictCursor
import MainServer.Managers as Managers
from MainServer.Managers.TokenManager import TokenManager


class AdminsManager:
    def __init__(self, db_password, db_name, db_user, is_debug):
        self.PUBLIC_PASSWORD = db_password
        self.PUBLIC_DATABASE = db_name
        self.PUBLIC_USER = db_user
        self.is_debug = is_debug
        self.initial_database_functions()

    def initial_database_functions(self):
        conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                password=self.PUBLIC_PASSWORD)
        cur = conn.cursor()

        query = "CREATE OR REPLACE FUNCTION admins_manager_add(input_username VARCHAR(100), " \
                "input_password VARCHAR(100), input_permissions VARCHAR(100)[100]) " \
                "RETURNS INTEGER AS $$ " \
                "BEGIN " \
                "INSERT INTO admins (username, password, permissions) VALUES " \
                "(input_username, input_password, input_permissions);" \
                "RETURN 0; " \
                "END; " \
                "$$ LANGUAGE plpgsql;"
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_edit(input_username VARCHAR(100), " \
                "input_permissions VARCHAR(100)[100], " \
                "input_admin_id UUID) " \
                "RETURNS INTEGER AS $$ " \
                "BEGIN " \
                "UPDATE admins SET username=input_username, permissions=input_permissions " \
                "WHERE admin_id=input_admin_id; " \
                "RETURN 0; " \
                "END; " \
                "$$ LANGUAGE plpgsql;"
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_delete(input_admin_id UUID) " \
                "RETURNS INTEGER AS $$ " \
                "BEGIN " \
                "DELETE FROM admins WHERE admin_id=input_admin_id; " \
                "RETURN 0; " \
                "END; " \
                "$$ LANGUAGE plpgsql;"
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_get_all() " \
                "RETURNS TABLE ( " \
                "admin_id UUID, " \
                "username VARCHAR(100), " \
                "permissions VARCHAR(100)[] " \
                ") AS $$ " \
                "BEGIN " \
                "RETURN QUERY SELECT admins.admin_id, admins.username, " \
                "admins.permissions " \
                "FROM admins; " \
                "END; " \
                "$$ LANGUAGE plpgsql; "
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_get_one(input_admin_id UUID) " \
                "RETURNS TABLE ( " \
                "admin_id UUID, " \
                "username VARCHAR(100), " \
                "permissions VARCHAR(100)[] " \
                ") AS $$ " \
                "BEGIN " \
                "RETURN QUERY SELECT admins.admin_id, admins.username, " \
                "admins.permissions " \
                "FROM admins WHERE admins.admin_id=input_admin_id; " \
                "END; " \
                "$$ LANGUAGE plpgsql; "
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_check_login(input_username VARCHAR(100), " \
                "input_password VARCHAR(100)) " \
                "RETURNS UUID AS $$ " \
                "DECLARE " \
                "var_counter INT; " \
                "BEGIN " \
                "SELECT count(*) INTO var_counter FROM Admins WHERE username=input_username AND password=input_password;" \
                "IF var_counter > 0 THEN " \
                "RETURN (SELECT Admins.admin_id FROM Admins WHERE username=input_username); " \
                "END IF; " \
                "RETURN NULL;" \
                "END; " \
                "$$ LANGUAGE plpgsql;"
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_change_password(input_admin_id UUID, " \
                "input_password VARCHAR(100), input_new_password VARCHAR(100)) " \
                "RETURNS INTEGER AS $$ " \
                "DECLARE " \
                "var_counter INT; " \
                "BEGIN " \
                "SELECT count(*) INTO var_counter FROM Admins WHERE admin_id=input_admin_id AND password=input_password;" \
                "IF var_counter > 0 THEN " \
                "UPDATE Admins SET password=input_new_password WHERE admin_id=input_admin_id; " \
                "RETURN 0; " \
                "END IF; " \
                "RETURN 1;" \
                "END; " \
                "$$ LANGUAGE plpgsql;"
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_change_other_password(input_admin_id UUID, " \
                "input_password VARCHAR(100)) " \
                "RETURNS INTEGER AS $$ " \
                "DECLARE " \
                "var_counter INT; " \
                "BEGIN " \
                "UPDATE Admins SET password=input_password WHERE admin_id=input_admin_id; " \
                "RETURN 0; " \
                "END; " \
                "$$ LANGUAGE plpgsql;"
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_check_permission(input_admin_id UUID, " \
                "input_permission VARCHAR(100)) " \
                "RETURNS INTEGER AS $$ " \
                "DECLARE " \
                "var_counter INT; " \
                "BEGIN " \
                "SELECT count(*) INTO var_counter FROM Admins WHERE admin_id=input_admin_id AND input_permission=ANY(permissions);" \
                "IF var_counter > 0 THEN " \
                "RETURN 0; " \
                "END IF; " \
                "RETURN 1;" \
                "END; " \
                "$$ LANGUAGE plpgsql;"
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_set_settings(input_settings_information json) " \
                "RETURNS INTEGER AS $$ " \
                "DECLARE " \
                "var_counter INT; " \
                "BEGIN " \
                "SELECT count(*) INTO var_counter FROM Settings; " \
                "IF var_counter < 1 THEN " \
                "INSERT INTO Settings (settings_information) VALUES (input_settings_information);" \
                "RETURN 0; " \
                "END IF; " \
                "UPDATE Settings SET settings_information=input_settings_information;" \
                "RETURN 0;" \
                "END; " \
                "$$ LANGUAGE plpgsql;"
        cur.execute(query)
        conn.commit()

        query = "CREATE OR REPLACE FUNCTION admins_manager_get_settings() " \
                "RETURNS TABLE ( " \
                "settings_information json " \
                ") AS $$ " \
                "BEGIN " \
                "RETURN QUERY SELECT settings.settings_information " \
                "FROM settings; " \
                "END; " \
                "$$ LANGUAGE plpgsql; "
        cur.execute(query)
        conn.commit()

        conn.close()

    # Done
    def gateway(self, input_bundle, destination):
        if self.is_debug:
            method_to_call = getattr(self, destination)
            result = method_to_call(input_bundle)
        else:
            try:
                method_to_call = getattr(self, destination)
                result = method_to_call(input_bundle)
            except Exception as e:
                output = {
                    "farsi_message": "متد مورد نظر پیدا نشد",
                    "english_message": "Method not found",
                    "status": "failure",
                    "code": 404
                }
                return output

        output = {
            "status": "failure",
            "code": result["code"],
            "farsi_message": result["farsi_message"],
            "english_message": result["english_message"],
            "data": None
        }
        if result["code"] == 200:
            output["status"] = "ok"
            output["data"] = result["data"]
            try:
                output["data"]["input_bundle"] = input_bundle
            except:
                output["data"] = {
                    "input_bundle": input_bundle
                }
        return output

    # region Listeners

    def admin_login(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "username" in input_bundle:
                username = input_bundle["username"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار username وارد نشده است."
                result["english_message"] = "username is Null."
                return result
            if "password" in input_bundle:
                password = input_bundle["password"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار password وارد نشده است."
                result["english_message"] = "password is Null."
                return result
        temp_result = self.check_login(username, password)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def admin_add(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "username" in input_bundle:
                username = input_bundle["username"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار username وارد نشده است."
                result["english_message"] = "username is Null."
                return result
            if "password" in input_bundle:
                password = input_bundle["password"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار password وارد نشده است."
                result["english_message"] = "password is Null."
                return result
            if "permissions" in input_bundle:
                permissions = input_bundle["permissions"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار permissions وارد نشده است."
                result["english_message"] = "permissions is Null."
                return result
            if "token" in input_bundle:
                token = input_bundle["token"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار token وارد نشده است."
                result["english_message"] = "token is Null."
                return result
        temp_result = self.add_admin(username, password, permissions, token)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def admin_edit(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "username" in input_bundle:
                username = input_bundle["username"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار username وارد نشده است."
                result["english_message"] = "username is Null."
                return result
            if "permissions" in input_bundle:
                permissions = input_bundle["permissions"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار permissions وارد نشده است."
                result["english_message"] = "permissions is Null."
                return result
            if "admin_id" in input_bundle:
                admin_id = input_bundle["admin_id"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار admin_id وارد است."
                result["english_message"] = "admin_id is Null."
                return result
            if "token" in input_bundle:
                token = input_bundle["token"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار token وارد نشده است."
                result["english_message"] = "token is Null."
                return result
        temp_result = self.edit_admin(
            username, permissions, admin_id, token)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def admin_delete(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "admin_id" in input_bundle:
                admin_id = input_bundle["admin_id"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار admin_id وارد نشده است."
                result["english_message"] = "admin_id is Null."
                return result
            if "token" in input_bundle:
                token = input_bundle["token"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار token وارد نشده است."
                result["english_message"] = "token is Null."
                return result

        temp_result = self.delete_admin(admin_id, token)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def admin_getAll(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "token" in input_bundle:
                token = input_bundle["token"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار token وارد نشده است."
                result["english_message"] = "token is Null."
                return result
        temp_result = self.get_all_admins(token)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def admin_getOne(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "admin_id" in input_bundle:
                admin_id = input_bundle["admin_id"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار admin_id وارد نشده است."
                result["english_message"] = "admin_id is Null."
                return result
            if "token" in input_bundle:
                token = input_bundle["token"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار token وارد نشده است."
                result["english_message"] = "token is Null."
                return result
        temp_result = self.get_one_admin(admin_id, token)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def admin_changePassword(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "new_password" in input_bundle:
                new_password = input_bundle["new_password"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار new_passowrd وارد نشده است."
                result["english_message"] = "new_passowrd is Null."
                return result
            if "password" in input_bundle:
                password = input_bundle["password"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار password وارد نشده است."
                result["english_message"] = "password is Null."
                return result
            if "token" in input_bundle:
                token = input_bundle["token"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار token وارد نشده است."
                result["english_message"] = "token is Null."
                return result
        temp_result = self.change_password(password, new_password, token)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def admin_setPassword(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "admin_id" in input_bundle:
                admin_id = input_bundle["admin_id"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار admin_id وارد نشده است."
                result["english_message"] = "admin_id is Null."
                return result
            if "password" in input_bundle:
                password = input_bundle["password"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار password وارد نشده است."
                result["english_message"] = "password is Null."
                return result
            if "token" in input_bundle:
                token = input_bundle["token"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار token وارد نشده است."
                result["english_message"] = "token is Null."
                return result
        temp_result = self.change_others_password(password, admin_id, token)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def admin_check(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "permission" in input_bundle:
                permission = input_bundle["permission"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار permission وارد نشده است."
                result["english_message"] = "permission is Null."
                return result
            if "token" in input_bundle:
                token = input_bundle["token"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار token وارد نشده است."
                result["english_message"] = "token is Null."
                return result
        temp_result = self.check_token(permission, token)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def admin_setSettings(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        if input_bundle is None:
            result["code"] = 406
            return result
        else:
            if "settings_information" in input_bundle:
                settings_information = input_bundle["settings_information"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار settings_information وارد نشده است."
                result["english_message"] = "settings_information is Null."
                return result
            if "token" in input_bundle:
                token = input_bundle["token"]
            else:
                result["code"] = 406
                result["farsi_message"] = "مقدار token وارد نشده است."
                result["english_message"] = "token is Null."
                return result
        temp_result = self.set_settings_information(token, settings_information)
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    def guest_getSettings(self, input_bundle):
        result = {
            "code": 200,
            "data": None
        }
        temp_result = self.get_settings_information()
        if temp_result["status"] == "ok":
            result["data"] = temp_result["data"]
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        else:
            result["code"] = 409
            result["farsi_message"] = temp_result["farsi_message"]
            result["english_message"] = temp_result["english_message"]
        return result

    # endregion

    # region Handlers

    def check_login(self, username, password):
        conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                password=self.PUBLIC_PASSWORD)
        cur = conn.cursor()
        cur.callproc('admins_manager_check_login', [username, password])
        admin_id = cur.fetchall()[0][0]
        if admin_id is None:
            return Managers.result_sender(code=403, farsi_message="رمز عبور و نام کاربری مطابقت ندارند.",
                                          english_message="Wrong password of username.")

        token = TokenManager.user_id_to_token(admin_id, True, "Admin")

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.callproc('admins_manager_get_one', [admin_id])
        admin = cur.fetchall()[0]
        conn.close()
        data = {
            "token": token,
            "profile": admin
        }

        return Managers.result_sender(code=200, data=data)

    def add_admin(self, username, password, permissions, token):
        token_result = TokenManager.token_to_user_id(
            token, is_admin=True, can_deactive=False, permission="Admin")
        if token_result["status"] == "OK":
            conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                    password=self.PUBLIC_PASSWORD)
            cur = conn.cursor()
            cur.callproc('admins_manager_add', [
                username, password, permissions])
            conn.commit()
            return Managers.result_sender(code=200)
        else:
            return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"],
                                          english_message=token_result["english_message"])

    def edit_admin(self, username, permissions, admin_id, token):
        token_result = TokenManager.token_to_user_id(
            token, is_admin=True, can_deactive=False, permission="Admin")
        if token_result["status"] == "OK":
            conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                    password=self.PUBLIC_PASSWORD)
            cur = conn.cursor()
            cur.callproc('admins_manager_edit', [
                username, permissions, admin_id])
            conn.commit()
            return Managers.result_sender(code=200)
        else:
            return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"],
                                          english_message=token_result["english_message"])

    def delete_admin(self, admin_id, token):
        token_result = TokenManager.token_to_user_id(
            token, is_admin=True, can_deactive=False, permission="Admin")
        if token_result["status"] == "OK":

            conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                    password=self.PUBLIC_PASSWORD)
            cur = conn.cursor()
            cur.callproc('admins_manager_delete', [admin_id])
            conn.commit()
            return Managers.result_sender(code=200)
        else:
            return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"],
                                          english_message=token_result["english_message"])

    def get_all_admins(self, token):
        token_result = TokenManager.token_to_user_id(
            token, is_admin=True, can_deactive=False, permission="Admin")
        if token_result["status"] == "OK":
            conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                    password=self.PUBLIC_PASSWORD)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.callproc('admins_manager_get_all', [])
            admins = cur.fetchall()
            data = {
                "admins": admins
            }
            conn.close()
            return Managers.result_sender(code=200, data=data)
        else:
            return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"],
                                          english_message=token_result["english_message"])

    def get_one_admin(self, admin_id, token):
        token_result = TokenManager.token_to_user_id(
            token, is_admin=True, can_deactive=False, permission="Admin")
        if token_result["status"] == "OK":
            conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                    password=self.PUBLIC_PASSWORD)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.callproc('admins_manager_get_one', [admin_id])
            admins = cur.fetchall()
            data = {
                "admin": admins[0]
            }
            conn.close()
            return Managers.result_sender(code=200, data=data)
        else:
            return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"],
                                          english_message=token_result["english_message"])

    def change_password(self, password, new_passowrd, token):
        token_result = TokenManager.token_to_user_id(
            token, is_admin=True, can_deactive=False, permission="Self")
        if token_result["status"] == "OK":
            conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                    password=self.PUBLIC_PASSWORD)
            cur = conn.cursor()
            cur.callproc('admins_manager_change_password', [
                token_result["data"]["user_id"], password, new_passowrd])
            conn.commit()
            result = cur.fetchall()[0][0]
            conn.close()
            if result == 0:
                return Managers.result_sender(code=200)
            else:
                return Managers.result_sender(code=403, farsi_message="رمز عبور فعلی درست وارد نشده است.",
                                              english_message="Wrong current password.")
        else:
            return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"],
                                          english_message=token_result["english_message"])

    def change_others_password(self, password, admin_id, token):
        token_result = TokenManager.token_to_user_id(
            token, is_admin=True, can_deactive=False, permission="Self")
        if token_result["status"] == "OK":
            conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                    password=self.PUBLIC_PASSWORD)
            cur = conn.cursor()
            cur.callproc('admins_manager_change_other_password', [admin_id, password])
            conn.commit()
            conn.close()
            return Managers.result_sender(code=200)
        else:
            return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"],
                                          english_message=token_result["english_message"])

    def set_settings_information(self, token, settings_information):
        token_result = TokenManager.token_to_user_id(
            token, is_admin=True, can_deactive=False, permission="Admin")
        if token_result["status"] == "OK":
            conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                    password=self.PUBLIC_PASSWORD)
            cur = conn.cursor()
            cur.callproc('admins_manager_set_settings', [json.dumps(settings_information)])
            conn.commit()
            return Managers.result_sender(code=200)
        else:
            return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"],
                                          english_message=token_result["english_message"])

    def get_settings_information(self):
        conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER,
                                password=self.PUBLIC_PASSWORD)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.callproc('admins_manager_get_settings', [])
        if cur.rowcount > 0:
            settings_information = cur.fetchall()[0]["settings_information"]
        else:
            settings_information = None
        data = {
            "settings_information": settings_information
        }
        return Managers.result_sender(code=200, data=data)

    def check_token(self, permission, token):
        print(permission)
        token_result = TokenManager.token_to_user_id(token, is_admin=True, can_deactive=False, permission=permission)

        if token_result["status"] == "OK":
            return Managers.result_sender(code=200)
        else:
            return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"],
                                          english_message=token_result["english_message"])

    # endregion

    # region Statics

    @staticmethod
    def check_permission(admin_id, permission):
        conn = psycopg2.connect(host="localhost", database='RTR', user='postgres',
                                password='2515263')
        cur = conn.cursor()
        cur.callproc('admins_manager_check_permission', [admin_id, permission])
        result = cur.fetchall()[0][0]
        conn.close()
        if result == 0:
            return True
        else:
            return False

    # endregion
