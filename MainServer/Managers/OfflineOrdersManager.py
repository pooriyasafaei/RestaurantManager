# coding=utf-8
import json
import psycopg2
import random
import uuid
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import MainServer.Managers as Managers
from MainServer.Managers.TokenManager import TokenManager


class OfflineOrdersManager:
	def __init__(self, db_password, db_name, db_user, is_debug):
		self.PUBLIC_PASSWORD = db_password
		self.PUBLIC_DATABASE = db_name
		self.PUBLIC_USER = db_user
		self.is_debug = is_debug
		self.initial_database_functions()

	def initial_database_functions(self):
		conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
		cur = conn.cursor()

		query = "CREATE OR REPLACE FUNCTION offlineorders_manager_admin_get_all_offline_orders " \
				"(input_table_id uuid, input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"order_id uuid, " \
				"table_id_information json, " \
				"table_id uuid, " \
				"foods_list json, " \
				"order_price bigint, " \
				"order_information json, " \
				"create_date varchar(100)) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT OfflineOrders.order_id, row_to_json(tables_manager_admin_get_one_table(OfflineOrders.table_id)), OfflineOrders.table_id, OfflineOrders.foods_list, OfflineOrders.order_price, OfflineOrders.order_information, to_char(OfflineOrders.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM OfflineOrders " \
				"WHERE (OfflineOrders.table_id=input_table_id OR input_table_id isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then OfflineOrders.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION offlineorders_manager_admin_count_all_offline_orders " \
				"(input_table_id uuid) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM OfflineOrders " \
				"WHERE (OfflineOrders.table_id=input_table_id OR input_table_id isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION offlineorders_manager_admin_get_one_offline_order " \
				"(input_order_id uuid) " \
				"RETURNS TABLE ( " \
				"order_id uuid, " \
				"table_id_information json, " \
				"table_id uuid, " \
				"foods_list json, " \
				"order_price bigint, " \
				"order_information json, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM OfflineOrders WHERE (OfflineOrders.order_id=input_order_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT OfflineOrders.order_id, row_to_json(tables_manager_admin_get_one_table(OfflineOrders.table_id)), OfflineOrders.table_id, OfflineOrders.foods_list, OfflineOrders.order_price, OfflineOrders.order_information, to_char(OfflineOrders.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM OfflineOrders " \
				"WHERE (OfflineOrders.order_id=input_order_id OR input_order_id isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION offlineorders_manager_admin_edit_offline_order " \
				"(input_order_id uuid, input_table_id uuid, input_foods_list json, input_order_price bigint, input_order_information json) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"UPDATE OfflineOrders SET " \
				"table_id=input_table_id, foods_list=input_foods_list, order_price=input_order_price, order_information=input_order_information " \
				"WHERE order_id=input_order_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION offlineorders_manager_admin_delete_offline_order " \
				"(input_order_id uuid) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"DELETE FROM OfflineOrders WHERE order_id=input_order_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION offlineorders_manager_admin_create_offline_order " \
				"(input_table_id uuid, input_foods_list json, input_order_price bigint, input_order_information json) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"INSERT INTO OfflineOrders (table_id, foods_list, order_price, order_information) VALUES " \
				"(input_table_id, input_foods_list, input_order_price, input_order_information); " \
				"RETURN 0; " \
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
			all_inputs = ['table_id', 'token', 'page', 'count']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_all_offline_orders(input_bundle["table_id"], input_bundle["token"], input_bundle["page"], input_bundle["count"])
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
			all_inputs = ['order_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_one_offline_order(input_bundle["order_id"], input_bundle["token"])
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
			all_inputs = ['order_id', 'table_id', 'foods_list', 'order_price', 'order_information', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_edit_offline_order(input_bundle["order_id"], input_bundle["table_id"], input_bundle["foods_list"], input_bundle["order_price"], input_bundle["order_information"], input_bundle["token"])
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
			all_inputs = ['order_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_delete_offline_order(input_bundle["order_id"], input_bundle["token"])
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
			all_inputs = ['table_id', 'foods_list', 'order_price', 'order_information', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_create_offline_order(input_bundle["table_id"], input_bundle["foods_list"], input_bundle["order_price"], input_bundle["order_information"], input_bundle["token"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def admin_get_all_offline_orders(self, table_id, token, page, count):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="OfflineOrder")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('offlineorders_manager_admin_get_all_offline_orders', 
			[table_id, 'default', page, count])
			offline_orders = cur.fetchall()
			cur.callproc('offlineorders_manager_admin_count_all_offline_orders', 
			[table_id])
			all_offline_orders = list(cur.fetchall()[0].values())[0]
			data = {
				"offline_orders": offline_orders,
				"all_offline_orders": all_offline_orders,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_get_one_offline_order(self, order_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="OfflineOrder")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('offlineorders_manager_admin_get_one_offline_order', 
			[order_id])
			offline_order = cur.fetchone()
			data = {
				"offline_order": offline_order,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_edit_offline_order(self, order_id, table_id, foods_list, order_price, order_information, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="OfflineOrder")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('offlineorders_manager_admin_edit_offline_order', 
			[order_id, table_id, json.dumps(foods_list), order_price, json.dumps(order_information)])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_delete_offline_order(self, order_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="OfflineOrder")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('offlineorders_manager_admin_delete_offline_order', 
			[order_id])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_create_offline_order(self, table_id, foods_list, order_price, order_information, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="OfflineOrder")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('offlineorders_manager_admin_create_offline_order', 
			[table_id, json.dumps(foods_list), order_price, json.dumps(order_information)])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

