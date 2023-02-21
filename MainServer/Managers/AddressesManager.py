# coding=utf-8
import json
import psycopg2
import random
import uuid
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import MainServer.Managers as Managers
from MainServer.Managers.TokenManager import TokenManager


class AddressesManager:
	def __init__(self, db_password, db_name, db_user, is_debug):
		self.PUBLIC_PASSWORD = db_password
		self.PUBLIC_DATABASE = db_name
		self.PUBLIC_USER = db_user
		self.is_debug = is_debug
		self.initial_database_functions()

	def initial_database_functions(self):
		conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
		cur = conn.cursor()

		query = "CREATE OR REPLACE FUNCTION addresses_manager_user_add_address " \
				"(input_user_id uuid, input_address_name varchar(100), input_address_description json) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"INSERT INTO Addresses (user_id, address_name, address_description) VALUES " \
				"(input_user_id, input_address_name, input_address_description); " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION addresses_manager_user_edit_address " \
				"(input_address_id uuid, input_user_id uuid, input_address_name varchar(100), input_address_description json) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"UPDATE Addresses SET " \
				"user_id=input_user_id, address_name=input_address_name, address_description=input_address_description " \
				"WHERE address_id=input_address_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION addresses_manager_user_delete_address " \
				"(input_address_id uuid) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"DELETE FROM Addresses WHERE address_id=input_address_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION addresses_manager_user_get_all_addresses " \
				"(input_user_id uuid, input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"address_id uuid, " \
				"user_id_information json, " \
				"user_id uuid, " \
				"address_name varchar(100), " \
				"address_description json, " \
				"create_date varchar(100)) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT Addresses.address_id, row_to_json(users_manager_admin_get_one_user(Addresses.user_id)), Addresses.user_id, Addresses.address_name, Addresses.address_description, to_char(Addresses.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Addresses " \
				"WHERE (Addresses.user_id=input_user_id OR input_user_id isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then Addresses.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION addresses_manager_user_count_all_addresses " \
				"(input_user_id uuid) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM Addresses " \
				"WHERE (Addresses.user_id=input_user_id OR input_user_id isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION addresses_manager_user_get_one_address " \
				"(input_address_id uuid) " \
				"RETURNS TABLE ( " \
				"address_id uuid, " \
				"user_id_information json, " \
				"user_id uuid, " \
				"address_name varchar(100), " \
				"address_description json, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Addresses WHERE (Addresses.address_id=input_address_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Addresses.address_id, row_to_json(users_manager_admin_get_one_user(Addresses.user_id)), Addresses.user_id, Addresses.address_name, Addresses.address_description, to_char(Addresses.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Addresses " \
				"WHERE (Addresses.address_id=input_address_id OR input_address_id isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION addresses_manager_admin_get_all_addresses " \
				"(input_user_id uuid, input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"address_id uuid, " \
				"user_id_information json, " \
				"user_id uuid, " \
				"address_name varchar(100), " \
				"address_description json, " \
				"create_date varchar(100)) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT Addresses.address_id, row_to_json(users_manager_admin_get_one_user(Addresses.user_id)), Addresses.user_id, Addresses.address_name, Addresses.address_description, to_char(Addresses.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Addresses " \
				"WHERE (Addresses.user_id=input_user_id OR input_user_id isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then Addresses.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION addresses_manager_admin_count_all_addresses " \
				"(input_user_id uuid) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM Addresses " \
				"WHERE (Addresses.user_id=input_user_id OR input_user_id isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION addresses_manager_admin_get_one_address " \
				"(input_address_id uuid) " \
				"RETURNS TABLE ( " \
				"address_id uuid, " \
				"user_id_information json, " \
				"user_id uuid, " \
				"address_name varchar(100), " \
				"address_description json, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Addresses WHERE (Addresses.address_id=input_address_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Addresses.address_id, row_to_json(users_manager_admin_get_one_user(Addresses.user_id)), Addresses.user_id, Addresses.address_name, Addresses.address_description, to_char(Addresses.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Addresses " \
				"WHERE (Addresses.address_id=input_address_id OR input_address_id isnull); " \
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

	def user_create(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['address_name', 'address_description', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.user_add_address(input_bundle["address_name"], input_bundle["address_description"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def user_edit(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['address_id', 'address_name', 'address_description', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.user_edit_address(input_bundle["address_id"], input_bundle["address_name"], input_bundle["address_description"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def user_delete(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['address_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.user_delete_address(input_bundle["address_id"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def user_getAll(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['page', 'count', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.user_get_all_addresses(input_bundle["page"], input_bundle["count"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def user_getOne(self, input_bundle):
		result = {
			"code": 200,
			"data": None
		}
		if input_bundle is None:
			result["code"] = 406
			return result
		else:
			all_inputs = ['address_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.user_get_one_address(input_bundle["address_id"], input_bundle["token"])
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
			all_inputs = ['user_id', 'page', 'count', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_all_addresses(input_bundle["user_id"], input_bundle["page"], input_bundle["count"], input_bundle["token"])
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
			all_inputs = ['address_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_one_address(input_bundle["address_id"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def user_add_address(self, address_name, address_description, token):
		token_result = TokenManager.token_to_user_id(token, is_admin=False, can_deactive=False)
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			user_id = token_result["data"]["user_id"]
			cur.callproc('addresses_manager_user_add_address', 
			[user_id, address_name, json.dumps(address_description)])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def user_edit_address(self, address_id, address_name, address_description, token):
		token_result = TokenManager.token_to_user_id(token, is_admin=False, can_deactive=False)
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			user_id = token_result["data"]["user_id"]
			cur.callproc('addresses_manager_user_edit_address', 
			[address_id, user_id, address_name, json.dumps(address_description)])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def user_delete_address(self, address_id, token):
		token_result = TokenManager.token_to_user_id(token, is_admin=False, can_deactive=False)
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			user_id = token_result["data"]["user_id"]
			cur.callproc('addresses_manager_user_delete_address', 
			[address_id])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def user_get_all_addresses(self, page, count, token):
		token_result = TokenManager.token_to_user_id(token, is_admin=False, can_deactive=False)
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			user_id = token_result["data"]["user_id"]
			cur.callproc('addresses_manager_user_get_all_addresses', 
			[user_id, 'default', page, count])
			addresses = cur.fetchall()
			cur.callproc('addresses_manager_user_count_all_addresses', 
			[user_id])
			all_addresses = list(cur.fetchall()[0].values())[0]
			data = {
				"addresses": addresses,
				"all_addresses": all_addresses,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def user_get_one_address(self, address_id, token):
		token_result = TokenManager.token_to_user_id(token, is_admin=False, can_deactive=False)
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			user_id = token_result["data"]["user_id"]
			cur.callproc('addresses_manager_user_get_one_address', 
			[address_id])
			address = cur.fetchall()
			data = {
				"address": address,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_get_all_addresses(self, user_id, page, count, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="User")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('addresses_manager_admin_get_all_addresses', 
			[user_id, 'default', page, count])
			addresses = cur.fetchall()
			cur.callproc('addresses_manager_admin_count_all_addresses', 
			[user_id])
			all_addresses = list(cur.fetchall()[0].values())[0]
			data = {
				"addresses": addresses,
				"all_addresses": all_addresses,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_get_one_address(self, address_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="User")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('addresses_manager_admin_get_one_address', 
			[address_id])
			address = cur.fetchall()
			data = {
				"address": address,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

