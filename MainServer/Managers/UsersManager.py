# coding=utf-8
import json
import psycopg2
import random
import uuid
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import MainServer.Managers as Managers
from MainServer.Managers.TokenManager import TokenManager


class UsersManager:
	def __init__(self, db_password, db_name, db_user, is_debug):
		self.PUBLIC_PASSWORD = db_password
		self.PUBLIC_DATABASE = db_name
		self.PUBLIC_USER = db_user
		self.is_debug = is_debug
		self.initial_database_functions()

	def initial_database_functions(self):
		conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
		cur = conn.cursor()

		query = "CREATE OR REPLACE FUNCTION users_manager_guest_create_user " \
				"(input_phone_number varchar(20), input_username varchar(200), input_password varchar(200), input_sms_code varchar(10), input_is_active int, input_wallet_amount double precision) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"INSERT INTO Users (phone_number, username, password, sms_code, is_active, wallet_amount) VALUES " \
				"(input_phone_number, input_username, input_password, input_sms_code, input_is_active, input_wallet_amount); " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_guest_login_user " \
				"(input_username varchar(200), input_password varchar(200)) " \
				"RETURNS TABLE ( " \
				"user_id uuid, " \
				"phone_number varchar(20), " \
				"username varchar(200), " \
				"is_active int, " \
				"wallet_amount double precision, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Users WHERE (Users.username=input_username) and (Users.password=input_password); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Users.user_id, Users.phone_number, Users.username, Users.is_active, Users.wallet_amount, to_char(Users.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Users " \
				"WHERE (Users.username=input_username OR input_username isnull) and (Users.password=input_password OR input_password isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_user_validate_phone_number " \
				"(input_user_id uuid, input_sms_code varchar(10)) " \
				"RETURNS TABLE ( " \
				"user_id uuid, " \
				"phone_number varchar(20), " \
				"username varchar(200), " \
				"is_active int, " \
				"wallet_amount double precision, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Users WHERE (Users.user_id=input_user_id) and (Users.sms_code=input_sms_code); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Users.user_id, Users.phone_number, Users.username, Users.is_active, Users.wallet_amount, to_char(Users.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Users " \
				"WHERE (Users.user_id=input_user_id OR input_user_id isnull) and (Users.sms_code=input_sms_code OR input_sms_code isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_user_resend_sms_code " \
				"(input_user_id uuid, input_sms_code varchar(10)) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"UPDATE Users SET " \
				"sms_code=input_sms_code " \
				"WHERE user_id=input_user_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_system_check_sms_code " \
				"(input_user_id uuid, input_sms_code varchar(10)) " \
				"RETURNS TABLE ( " \
				"user_id uuid, " \
				"phone_number varchar(20), " \
				"username varchar(200), " \
				"is_active int, " \
				"wallet_amount double precision, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Users WHERE (Users.user_id=input_user_id) and (Users.sms_code=input_sms_code); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Users.user_id, Users.phone_number, Users.username, Users.is_active, Users.wallet_amount, to_char(Users.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Users " \
				"WHERE (Users.user_id=input_user_id OR input_user_id isnull) and (Users.sms_code=input_sms_code OR input_sms_code isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_system_check_phone_number " \
				"(input_phone_number varchar(20)) " \
				"RETURNS TABLE ( " \
				"user_id uuid, " \
				"phone_number varchar(20), " \
				"username varchar(200), " \
				"is_active int, " \
				"wallet_amount double precision, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Users WHERE (Users.phone_number=input_phone_number); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Users.user_id, Users.phone_number, Users.username, Users.is_active, Users.wallet_amount, to_char(Users.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Users " \
				"WHERE (Users.phone_number=input_phone_number OR input_phone_number isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_user_get_profile " \
				"(input_user_id uuid) " \
				"RETURNS TABLE ( " \
				"user_id uuid, " \
				"phone_number varchar(20), " \
				"username varchar(200), " \
				"is_active int, " \
				"wallet_amount double precision, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Users WHERE (Users.user_id=input_user_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Users.user_id, Users.phone_number, Users.username, Users.is_active, Users.wallet_amount, to_char(Users.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Users " \
				"WHERE (Users.user_id=input_user_id OR input_user_id isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_user_set_password " \
				"(input_user_id uuid, input_password varchar(200)) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"UPDATE Users SET " \
				"password=input_password " \
				"WHERE user_id=input_user_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_admin_get_all_users " \
				"(input_phone_number varchar(20), input_username varchar(200), input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"user_id uuid, " \
				"phone_number varchar(20), " \
				"username varchar(200), " \
				"is_active int, " \
				"wallet_amount double precision, " \
				"create_date varchar(100)) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT Users.user_id, Users.phone_number, Users.username, Users.is_active, Users.wallet_amount, to_char(Users.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Users " \
				"WHERE (Users.phone_number=input_phone_number OR input_phone_number isnull) and (Users.username=input_username OR input_username isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then Users.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_admin_count_all_users " \
				"(input_phone_number varchar(20), input_username varchar(200)) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM Users " \
				"WHERE (Users.phone_number=input_phone_number OR input_phone_number isnull) and (Users.username=input_username OR input_username isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION users_manager_admin_get_one_user " \
				"(input_user_id uuid) " \
				"RETURNS TABLE ( " \
				"user_id uuid, " \
				"phone_number varchar(20), " \
				"username varchar(200), " \
				"is_active int, " \
				"wallet_amount double precision, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Users WHERE (Users.user_id=input_user_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Users.user_id, Users.phone_number, Users.username, Users.is_active, Users.wallet_amount, to_char(Users.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Users " \
				"WHERE (Users.user_id=input_user_id OR input_user_id isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

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
			output["status"] = "ok"
		except:
			output["data"] = {
				"input_bundle": input_bundle
			}
		return output

	def guest_register(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['phone_number', 'username', 'password']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.guest_create_user(input_bundle["phone_number"], input_bundle["username"], input_bundle["password"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def guest_login(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['username', 'password']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.guest_login_user(input_bundle["username"], input_bundle["password"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def user_verify(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['sms_code', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.user_validate_phone_number(input_bundle["sms_code"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def user_resend(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['phone_number']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.user_resend_sms_code(input_bundle["phone_number"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def user_getProfile(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.user_get_profile(input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def user_setPassword(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['password', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.user_set_password(input_bundle["password"], input_bundle["token"])
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
			all_inputs = ['phone_number', 'username', 'page', 'count', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_all_users(input_bundle["phone_number"], input_bundle["username"], input_bundle["page"], input_bundle["count"], input_bundle["token"])
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
			all_inputs = ['user_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_one_user(input_bundle["user_id"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def guest_create_user(self, phone_number, username, password):
		if True:
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			is_active = 0
			wallet_amount = 0
			sms_code = str(random.randint(10000, 99999))
			cur.callproc('users_manager_admin_count_all_users', [phone_number, None])
			all_users = list(cur.fetchall()[0].values())[0]
			if int(all_users) > 0:
				return Managers.result_sender(code=409, farsi_message='شماره موبایل وارد شده تکراریست، لطفا با شماره موبایل دیگری ثبت نام نمایید.', english_message='This phone number was registered before, please enter a new phone number.')
			cur.callproc('users_manager_guest_create_user', 
			[phone_number, username, password, sms_code, is_active, wallet_amount])
			conn.commit()
			cur.callproc('users_manager_admin_get_all_users', [phone_number, username, 'default', 1, 1])
			user = cur.fetchall()[0]
			token = TokenManager.user_id_to_token(user['user_id'], False)
			data = {
				"token": token,
				"sms_code": sms_code,
			}
			return Managers.result_sender(code=200, data=data)

	def guest_login_user(self, username, password):
		if True:
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('users_manager_guest_login_user', 
			[username, password])
			user = cur.fetchone()
			if user['user_id'] == None:
				return Managers.result_sender(code=409, farsi_message='شماره موبایل یا رمز عبور وارد شده صحیح نیست.', english_message='Wrong phone number or password.')
			token = TokenManager.user_id_to_token(user['user_id'], True)
			if int(user['is_active']) == 0:
				return Managers.result_sender(code=409, farsi_message='شماره موبایل شما تایید نشده است، ابتدا موبایل خود را فعال کنید.', english_message='Your phone number is not verified yet, please verify your phone number.')
			data = {
				"token": token,
			}
			return Managers.result_sender(code=200, data=data)

	def user_validate_phone_number(self, sms_code, token):
		token_result = TokenManager.token_to_user_id(token, is_admin=False, can_deactive=False)
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			user_id = token_result["data"]["user_id"]
			cur.callproc('users_manager_system_check_sms_code', [user_id, sms_code])
			user = cur.fetchone()
			if user['user_id'] is None:
				return Managers.result_sender(code=409, farsi_message='کد وارد شده صحیح نیست.', english_message='Wrong sms code.')
			is_active = 1
			cur.callproc('users_manager_user_validate_phone_number', 
			[user_id, sms_code])
			token = TokenManager.user_id_to_token(user['user_id'], True)
			data = {
				"token": token,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def user_resend_sms_code(self, phone_number):
		if True:
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('users_manager_system_check_phone_number', [phone_number])
			user = cur.fetchone()
			if user['user_id'] is None:
				return Managers.result_sender(code=409, farsi_message='این شماره موبایل در سیستم وجود ندارد.', english_message='This phone number is not registered.')
			sms_code = str(random.randint(10000, 99999))
			user_id = user['user_id']
			cur.callproc('users_manager_user_resend_sms_code', 
			[user_id, sms_code])
			conn.commit()
			token = TokenManager.user_id_to_token(user['user_id'], False)
			data = {
				"token": token,
				"sms_code": sms_code,
			}
			return Managers.result_sender(code=200, data=data)

	def user_get_profile(self, token):
		token_result = TokenManager.token_to_user_id(token, is_admin=False, can_deactive=False)
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			user_id = token_result["data"]["user_id"]
			cur.callproc('users_manager_user_get_profile', 
			[user_id])
			user = cur.fetchone()
			data = {
				"user": user,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def user_set_password(self, password, token):
		token_result = TokenManager.token_to_user_id(token, is_admin=False, can_deactive=False)
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			user_id = token_result["data"]["user_id"]
			cur.callproc('users_manager_user_set_password', 
			[user_id, password])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_get_all_users(self, phone_number, username, page, count, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="User")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('users_manager_admin_get_all_users', 
			[phone_number, username, 'default', page, count])
			users = cur.fetchall()
			cur.callproc('users_manager_admin_count_all_users', 
			[phone_number, username])
			all_users = list(cur.fetchall()[0].values())[0]
			data = {
				"users": users,
				"all_users": all_users,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_get_one_user(self, user_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="User")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('users_manager_admin_get_one_user', 
			[user_id])
			user = cur.fetchone()
			data = {
				"user": user,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

