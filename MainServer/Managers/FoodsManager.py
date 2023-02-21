# coding=utf-8
import json
import psycopg2
import random
import uuid
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import MainServer.Managers as Managers
from MainServer.Managers.TokenManager import TokenManager


class FoodsManager:
	def __init__(self, db_password, db_name, db_user, is_debug):
		self.PUBLIC_PASSWORD = db_password
		self.PUBLIC_DATABASE = db_name
		self.PUBLIC_USER = db_user
		self.is_debug = is_debug
		self.initial_database_functions()

	def initial_database_functions(self):
		conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
		cur = conn.cursor()

		query = "CREATE OR REPLACE FUNCTION foods_manager_admin_get_all_foods " \
				"(input_category_id uuid, input_food_name varchar(100), input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"food_id uuid, " \
				"category_id_information json, " \
				"category_id uuid, " \
				"food_name varchar(100), " \
				"food_price bigint, " \
				"food_information json, " \
				"is_active int, " \
				"create_date varchar(100)) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT Foods.food_id, row_to_json(categories_manager_admin_get_one_category(Foods.category_id)), Foods.category_id, Foods.food_name, Foods.food_price, Foods.food_information, Foods.is_active, to_char(Foods.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Foods " \
				"WHERE (Foods.category_id=input_category_id OR input_category_id isnull) and (Foods.food_name like '%' || input_food_name || '%' OR input_food_name isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then Foods.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION foods_manager_admin_count_all_foods " \
				"(input_category_id uuid, input_food_name varchar(100)) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM Foods " \
				"WHERE (Foods.category_id=input_category_id OR input_category_id isnull) and (Foods.food_name like '%' || input_food_name || '%' OR input_food_name isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION foods_manager_admin_get_one_food " \
				"(input_food_id uuid) " \
				"RETURNS TABLE ( " \
				"food_id uuid, " \
				"category_id_information json, " \
				"category_id uuid, " \
				"food_name varchar(100), " \
				"food_price bigint, " \
				"food_information json, " \
				"is_active int, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Foods WHERE (Foods.food_id=input_food_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Foods.food_id, row_to_json(categories_manager_admin_get_one_category(Foods.category_id)), Foods.category_id, Foods.food_name, Foods.food_price, Foods.food_information, Foods.is_active, to_char(Foods.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Foods " \
				"WHERE (Foods.food_id=input_food_id OR input_food_id isnull); " \
				"ELSE " \
				"RETURN next; " \
				"END IF; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION foods_manager_admin_edit_food " \
				"(input_food_id uuid, input_category_id uuid, input_food_name varchar(100), input_food_price bigint, input_food_information json, input_is_active int) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"UPDATE Foods SET " \
				"category_id=input_category_id, food_name=input_food_name, food_price=input_food_price, food_information=input_food_information, is_active=input_is_active " \
				"WHERE food_id=input_food_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION foods_manager_admin_delete_food " \
				"(input_food_id uuid) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"DELETE FROM Foods WHERE food_id=input_food_id; " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION foods_manager_admin_create_food " \
				"(input_category_id uuid, input_food_name varchar(100), input_food_price bigint, input_food_information json, input_is_active int) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"INSERT INTO Foods (category_id, food_name, food_price, food_information, is_active) VALUES " \
				"(input_category_id, input_food_name, input_food_price, input_food_information, input_is_active); " \
				"RETURN 0; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION foods_manager_guest_get_all_foods " \
				"(input_category_id uuid, input_food_name varchar(100), input_sort varchar, input_page int, input_count int) " \
				"RETURNS TABLE ( " \
				"food_id uuid, " \
				"category_id_information json, " \
				"category_id uuid, " \
				"food_name varchar(100), " \
				"food_price bigint, " \
				"food_information json, " \
				"is_active int, " \
				"create_date varchar(100)) AS $$ " \
				"BEGIN " \
				"RETURN QUERY SELECT Foods.food_id, row_to_json(categories_manager_admin_get_one_category(Foods.category_id)), Foods.category_id, Foods.food_name, Foods.food_price, Foods.food_information, Foods.is_active, to_char(Foods.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Foods " \
				"WHERE (Foods.category_id=input_category_id OR input_category_id isnull) and (Foods.food_name like '%' || input_food_name || '%' OR input_food_name isnull) " \
				"ORDER BY " \
				"case when input_sort LIKE '%default%' then Foods.create_date END DESC " \
				"LIMIT input_count OFFSET (input_page - 1) * input_count; " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION foods_manager_guest_count_all_foods " \
				"(input_category_id uuid, input_food_name varchar(100)) " \
				"RETURNS INTEGER AS $$ " \
				"BEGIN " \
				"RETURN (SELECT count(*) FROM Foods " \
				"WHERE (Foods.category_id=input_category_id OR input_category_id isnull) and (Foods.food_name like '%' || input_food_name || '%' OR input_food_name isnull)); " \
				"END; " \
				"$$ LANGUAGE plpgsql;"
		cur.execute(query)
		conn.commit()

		query = "CREATE OR REPLACE FUNCTION foods_manager_guest_get_one_food " \
				"(input_food_id uuid) " \
				"RETURNS TABLE ( " \
				"food_id uuid, " \
				"category_id_information json, " \
				"category_id uuid, " \
				"food_name varchar(100), " \
				"food_price bigint, " \
				"food_information json, " \
				"is_active int, " \
				"create_date varchar(100)) AS $$ " \
				"DECLARE " \
				"var_counter integer; " \
				"BEGIN " \
				"SELECT count(*) into var_counter FROM Foods WHERE (Foods.food_id=input_food_id); " \
				"IF var_counter > 0 THEN " \
				"RETURN QUERY SELECT Foods.food_id, row_to_json(categories_manager_admin_get_one_category(Foods.category_id)), Foods.category_id, Foods.food_name, Foods.food_price, Foods.food_information, Foods.is_active, to_char(Foods.create_date, 'YYYY-MM-DD HH24:MI:SS')::VARCHAR(100) FROM Foods " \
				"WHERE (Foods.food_id=input_food_id OR input_food_id isnull); " \
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
			all_inputs = ['food_name', 'category_id', 'token', 'page', 'count']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_all_foods(input_bundle["food_name"], input_bundle["category_id"], input_bundle["token"], input_bundle["page"], input_bundle["count"])
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
			all_inputs = ['food_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_get_one_food(input_bundle["food_id"], input_bundle["token"])
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
			all_inputs = ['food_id', 'category_id', 'food_name', 'food_price', 'food_information', 'is_active', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_edit_food(input_bundle["food_id"], input_bundle["category_id"], input_bundle["food_name"], input_bundle["food_price"], input_bundle["food_information"], input_bundle["is_active"], input_bundle["token"])
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
			all_inputs = ['food_id', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_delete_food(input_bundle["food_id"], input_bundle["token"])
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
			all_inputs = ['category_id', 'food_name', 'food_price', 'food_information', 'is_active', 'token']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.admin_create_food(input_bundle["category_id"], input_bundle["food_name"], input_bundle["food_price"], input_bundle["food_information"], input_bundle["is_active"], input_bundle["token"])
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
			all_inputs = ['food_name', 'category_id', 'page', 'count']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.guest_get_all_foods(input_bundle["food_name"], input_bundle["category_id"], input_bundle["page"], input_bundle["count"])
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
			all_inputs = ['food_id']
			for attribute in all_inputs:
				if attribute not in input_bundle:
					result["code"] = 406
					result["farsi_message"] = f"مقدار {attribute} وارد نشده است."
					result["english_message"] = f"{attribute} is Null."
					return result
		temp_result = self.guest_get_one_food(input_bundle["food_id"])
		if temp_result["status"] == "ok":
			result["data"] = temp_result["data"]
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		else:
			result["code"] = 409
			result["farsi_message"] = temp_result["farsi_message"]
			result["english_message"] = temp_result["english_message"]
		return result

	def admin_get_all_foods(self, food_name, category_id, token, page, count):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Food")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('foods_manager_admin_get_all_foods', 
			[category_id, food_name, 'default', page, count])
			foods = cur.fetchall()
			cur.callproc('foods_manager_admin_count_all_foods', 
			[category_id, food_name])
			all_foods = list(cur.fetchall()[0].values())[0]
			data = {
				"foods": foods,
				"all_foods": all_foods,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_get_one_food(self, food_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Food")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('foods_manager_admin_get_one_food', 
			[food_id])
			food = cur.fetchone()
			data = {
				"food": food,
			}
			return Managers.result_sender(code=200, data=data)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_edit_food(self, food_id, category_id, food_name, food_price, food_information, is_active, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Food")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('foods_manager_admin_edit_food', 
			[food_id, category_id, food_name, food_price, json.dumps(food_information), is_active])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_delete_food(self, food_id, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Food")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('foods_manager_admin_delete_food', 
			[food_id])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def admin_create_food(self, category_id, food_name, food_price, food_information, is_active, token):
		token_result = TokenManager.token_to_user_id(
			token, is_admin=True, can_deactive=False, permission="Food")
		if token_result["status"] == "OK":
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('foods_manager_admin_create_food', 
			[category_id, food_name, food_price, json.dumps(food_information), is_active])
			conn.commit()
			return Managers.result_sender(code=200)
		else:
			return Managers.result_sender(code=token_result["code"], farsi_message=token_result["farsi_message"], english_message=token_result["english_message"])

	def guest_get_all_foods(self, food_name, category_id, page, count):
		if True:
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('foods_manager_guest_get_all_foods', 
			[category_id, food_name, 'default', page, count])
			foods = cur.fetchall()
			cur.callproc('foods_manager_guest_count_all_foods', 
			[category_id, food_name])
			all_foods = list(cur.fetchall()[0].values())[0]
			data = {
				"foods": foods,
				"all_foods": all_foods,
			}
			return Managers.result_sender(code=200, data=data)

	def guest_get_one_food(self, food_id):
		if True:
			conn = psycopg2.connect(host="localhost", database=self.PUBLIC_DATABASE, user=self.PUBLIC_USER, password=self.PUBLIC_PASSWORD)
			cur = conn.cursor(cursor_factory=RealDictCursor)
			cur.callproc('foods_manager_guest_get_one_food', 
			[food_id])
			food = cur.fetchone()
			data = {
				"guest": guest,
			}
			return Managers.result_sender(code=200, data=data)

