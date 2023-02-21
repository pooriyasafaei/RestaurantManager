# coding=utf-8
import json
import psycopg2
import random
import uuid
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import MainServer.Managers as Managers
from MainServer.Managers.TokenManager import TokenManager


class SettingsManager:
	def __init__(self, db_password, db_name, db_user, is_debug):
		self.PUBLIC_PASSWORD = db_password
		self.PUBLIC_DATABASE = db_name
		self.PUBLIC_USER = db_user
		self.is_debug = is_debug
		self.initial_database_functions()

	def initial_database_functions(self):
		conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
		cur = conn.cursor()

		query = "CREATE OR REPLACE FUNCTION settings_manager_admin_get_all_settings " \
				"(input_setting_title varchar(2000), input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"setting_id uuid, " \
				"setting_title varchar(2000), " \
				"setting_information json, " \
				"create_date varchar(100)) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT Settings.setting_id, Settings.setting_title, Settings.setting_information, to_char(Settings.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Settings " \
				"WHERE (Settings.setting_title like '%' || input_setting_title || '%' OR input_setting_title isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then Settings.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION settings_manager_admin_count_all_settings " \
				"(input_setting_title varchar(2000)) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM Settings " \
				"WHERE (Settings.setting_title like '%' || input_setting_title || '%' OR input_setting_title isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION settings_manager_admin_get_one_setting " \
				"(input_setting_id uuid) " \
				"RETURNS TABLE ( " \
				"setting_id uuid, " \
				"setting_title varchar(2000), " \
				"setting_information json, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Settings WHERE (Settings.setting_id=input_setting_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Settings.setting_id, Settings.setting_title, Settings.setting_information, to_char(Settings.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Settings " \
				"WHERE (Settings.setting_id=input_setting_id OR input_setting_id isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION settings_manager_admin_edit_setting " \
				"(input_setting_id uuid, input_setting_title varchar(2000), input_setting_information json) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"UPDATE Settings SET " \
				"setting_title=input_setting_title, setting_information=input_setting_information " \
				"WHERE setting_id=input_setting_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION settings_manager_admin_delete_setting " \
				"(input_setting_id uuid) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"DELETE FROM Settings WHERE setting_id=input_setting_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION settings_manager_admin_setting_creator " \
				"(input_setting_title varchar(2000), input_setting_information json) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"INSERT INTO Settings (setting_title, setting_information) VALUES " \
				"(input_setting_title, input_setting_information); " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION settings_manager_guest_get_all_settings " \
				"(input_setting_title varchar(2000), input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"setting_id uuid, " \
				"setting_title varchar(2000), " \
				"setting_information json, " \
				"create_date varchar(100)) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT Settings.setting_id, Settings.setting_title, Settings.setting_information, to_char(Settings.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Settings " \
				"WHERE (Settings.setting_title like '%' || input_setting_title || '%' OR input_setting_title isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then Settings.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION settings_manager_guest_count_all_settings " \
				"(input_setting_title varchar(2000)) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM Settings " \
				"WHERE (Settings.setting_title like '%' || input_setting_title || '%' OR input_setting_title isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION settings_manager_guest_get_one_setting " \
				"(input_setting_id uuid) " \
				"RETURNS TABLE ( " \
				"setting_id uuid, " \
				"setting_title varchar(2000), " \
				"setting_information json, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Settings WHERE (Settings.setting_id=input_setting_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Settings.setting_id, Settings.setting_title, Settings.setting_information, to_char(Settings.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Settings " \
				"WHERE (Settings.setting_id=input_setting_id OR input_setting_id isnull); " \
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

	def admin_getAll(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['setting_title', 'page', 'count', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_all_settings(input_bundle["setting_title"], input_bundle["page"], input_bundle["count"], input_bundle["token"])
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
			all_inputs = ['setting_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_one_setting(input_bundle["setting_id"], input_bundle["token"])
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
			all_inputs = ['setting_id', 'setting_title', 'setting_information', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_edit_setting(input_bundle["setting_id"], input_bundle["setting_title"], input_bundle["setting_information"], input_bundle["token"])
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
			all_inputs = ['setting_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_delete_setting(input_bundle["setting_id"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def admin_create(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['setting_title', 'setting_information', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_setting_creator(input_bundle["setting_title"], input_bundle["setting_information"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def guest_getAll(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['setting_title', 'page', 'count']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.guest_get_all_settings(input_bundle["setting_title"], input_bundle["page"], input_bundle["count"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def guest_getOne(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['setting_id']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.guest_get_one_setting(input_bundle["setting_id"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def admin_get_all_settings(self, setting_title, page, count, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Setting")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('settings_manager_admin_get_all_settings', 
			[setting_title, 'default', page, count])
			settings = cur.fetchall()
			cur.callproc('settings_manager_admin_count_all_settings', 
			[setting_title])
			all_settings = list(cur.fetchall()[0].values())[0]
			data = {
				"settings": settings,
				"all_settings": all_settings,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_get_one_setting(self, setting_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Setting")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('settings_manager_admin_get_one_setting', 
			[setting_id])
			setting = cur.fetchone()
			data = {
				"setting": setting,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_edit_setting(self, setting_id, setting_title, setting_information, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Setting")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('settings_manager_admin_edit_setting', 
			[setting_id, setting_title, json.dumps(setting_information)])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_delete_setting(self, setting_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Setting")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('settings_manager_admin_delete_setting', 
			[setting_id])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_setting_creator(self, setting_title, setting_information, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Setting")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('settings_manager_admin_setting_creator', 
			[setting_title, json.dumps(setting_information)])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def guest_get_all_settings(self, setting_title, page, count):
		if True:
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('settings_manager_guest_get_all_settings', 
			[setting_title, 'default', page, count])
			settings = cur.fetchall()
			cur.callproc('settings_manager_guest_count_all_settings', 
			[setting_title])
			all_settings = list(cur.fetchall()[0].values())[0]
			data = {
				"settings": settings,
				"all_settings": all_settings,
			}
			return Managers.result_sender(code=200, data=data)

	def guest_get_one_setting(self, setting_id):
		if True:
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('settings_manager_guest_get_one_setting', 
			[setting_id])
			setting = cur.fetchone()
			data = {
				"setting": setting,
			}
			return Managers.result_sender(code=200, data=data)

