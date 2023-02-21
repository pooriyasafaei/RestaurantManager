# coding=utf-8
import json
import psycopg2
import random
import uuid
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import MainServer.Managers as Managers
from MainServer.Managers.TokenManager import TokenManager


class TablesManager:
	def __init__(self, db_password, db_name, db_user, is_debug):
		self.PUBLIC_PASSWORD = db_password
		self.PUBLIC_DATABASE = db_name
		self.PUBLIC_USER = db_user
		self.is_debug = is_debug
		self.initial_database_functions()

	def initial_database_functions(self):
		conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
		cur = conn.cursor()

		query = "CREATE OR REPLACE FUNCTION tables_manager_admin_get_all_tables " \
				"(input_table_name varchar(100), input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"table_id uuid, " \
				"table_name varchar(100), " \
				"table_information json) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT Tables.table_id, Tables.table_name, Tables.table_information FROM Tables " \
				"WHERE (Tables.table_name like '%' || input_table_name || '%' OR input_table_name isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then Tables.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION tables_manager_admin_count_all_tables " \
				"(input_table_name varchar(100)) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM Tables " \
				"WHERE (Tables.table_name like '%' || input_table_name || '%' OR input_table_name isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION tables_manager_admin_get_one_table " \
				"(input_table_id uuid) " \
				"RETURNS TABLE ( " \
				"table_id uuid, " \
				"table_name varchar(100), " \
				"table_information json) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Tables WHERE (Tables.table_id=input_table_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Tables.table_id, Tables.table_name, Tables.table_information FROM Tables " \
				"WHERE (Tables.table_id=input_table_id OR input_table_id isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION tables_manager_admin_edit_table " \
				"(input_table_id uuid, input_table_name varchar(100), input_table_information json) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"UPDATE Tables SET " \
				"table_name=input_table_name, table_information=input_table_information " \
				"WHERE table_id=input_table_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION tables_manager_admin_delete_table " \
				"(input_table_id uuid) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"DELETE FROM Tables WHERE table_id=input_table_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION tables_manager_admin_create_table " \
				"(input_table_name varchar(100), input_table_information json) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"INSERT INTO Tables (table_name, table_information) VALUES " \
				"(input_table_name, input_table_information); " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION tables_manager_guest_get_all_tables " \
				"(input_table_name varchar(100), input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"table_id uuid, " \
				"table_name varchar(100), " \
				"table_information json) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT Tables.table_id, Tables.table_name, Tables.table_information FROM Tables " \
				"WHERE (Tables.table_name like '%' || input_table_name || '%' OR input_table_name isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then Tables.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION tables_manager_guest_count_all_tables " \
				"(input_table_name varchar(100)) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM Tables " \
				"WHERE (Tables.table_name like '%' || input_table_name || '%' OR input_table_name isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION tables_manager_guest_get_one_table " \
				"(input_table_id uuid) " \
				"RETURNS TABLE ( " \
				"table_id uuid, " \
				"table_name varchar(100), " \
				"table_information json) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Tables WHERE (Tables.table_id=input_table_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Tables.table_id, Tables.table_name, Tables.table_information FROM Tables " \
				"WHERE (Tables.table_id=input_table_id OR input_table_id isnull); " \
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
			all_inputs = ['table_name', 'token', 'page', 'count']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_all_tables(input_bundle["table_name"], input_bundle["token"], input_bundle["page"], input_bundle["count"])
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
			all_inputs = ['table_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_one_table(input_bundle["table_id"], input_bundle["token"])
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
			all_inputs = ['table_id', 'table_name', 'table_information', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_edit_table(input_bundle["table_id"], input_bundle["table_name"], input_bundle["table_information"], input_bundle["token"])
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
			all_inputs = ['table_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_delete_table(input_bundle["table_id"], input_bundle["token"])
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
			all_inputs = ['table_name', 'table_information', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_create_table(input_bundle["table_name"], input_bundle["table_information"], input_bundle["token"])
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
			all_inputs = ['table_name', 'page', 'count']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.guest_get_all_tables(input_bundle["table_name"], input_bundle["page"], input_bundle["count"])
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
			all_inputs = ['table_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.guest_get_one_table(input_bundle["table_id"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def admin_get_all_tables(self, table_name, token, page, count):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Table")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('tables_manager_admin_get_all_tables', 
			[table_name, 'default', page, count])
			tables = cur.fetchall()
			cur.callproc('tables_manager_admin_count_all_tables', 
			[table_name])
			all_tables = list(cur.fetchall()[0].values())[0]
			data = {
				"tables": tables,
				"all_tables": all_tables,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_get_one_table(self, table_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Table")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('tables_manager_admin_get_one_table', 
			[table_id])
			table = cur.fetchone()
			data = {
				"table": table,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_edit_table(self, table_id, table_name, table_information, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Table")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('tables_manager_admin_edit_table', 
			[table_id, table_name, json.dumps(table_information)])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_delete_table(self, table_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Table")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('tables_manager_admin_delete_table', 
			[table_id])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_create_table(self, table_name, table_information, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Table")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('tables_manager_admin_create_table', 
			[table_name, json.dumps(table_information)])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def guest_get_all_tables(self, table_name, page, count):
		if True:
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('tables_manager_guest_get_all_tables', 
			[table_name, 'default', page, count])
			tables = cur.fetchall()
			cur.callproc('tables_manager_guest_count_all_tables', 
			[table_name])
			all_tables = list(cur.fetchall()[0].values())[0]
			data = {
				"tables": tables,
				"all_tables": all_tables,
			}
			return Managers.result_sender(code=200, data=data)

	def guest_get_one_table(self, table_id, token):
		token_result = TokenManager.token_to_user_id(token, is_admin=False, can_deactive=False)
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('tables_manager_guest_get_one_table', 
			[table_id])
			table = cur.fetchone()
			data = {
				"table": table,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

