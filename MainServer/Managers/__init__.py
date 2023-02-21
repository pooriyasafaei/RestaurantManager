import requests
import json

from MainServer.Managers import TokenManager
from MainServer.Managers import AdminsManager
from MainServer.Managers import UsersManager
from MainServer.Managers import TablesManager
from MainServer.Managers import CategoriesManager
from MainServer.Managers import SettingsManager
from MainServer.Managers import FoodsManager
from MainServer.Managers import AddressesManager
from MainServer.Managers import OfflineOrdersManager


def result_sender(code, farsi_message="با موفقیت انجام شد.", english_message="Successfully done.", data=None): 
	status = "failure"
	if code == 200:
		status = "ok"
	result = {
		"status": status,
		"code": code,
		"data": data,
		"farsi_message": farsi_message,
		"english_message": english_message
	}
	return result


class DB:
	def __init__(self):
		self.password = "2515263"
		self.database = "RestaurantManager"
		self.user = "postgres"


class JInfo:
	def __init__(self):
		self.secret = "Didi ey del ke ghame eshgh degarbar che kard ..."


class MainManager:
	def __init__(self):
		self.is_debug = True
		self.db_info = DB()
		self.jwt_info = JInfo()

		self.token_manager = TokenManager.TokenManager(self.jwt_info.secret, self.db_info.database, self.db_info.password)
		self.admins_manager = AdminsManager.AdminsManager(db_name=self.db_info.database, db_user=self.db_info.user, db_password=self.db_info.password, is_debug=self.is_debug)
		self.users_manager = UsersManager.UsersManager(db_name=self.db_info.database, db_user=self.db_info.user, db_password=self.db_info.password, is_debug=self.is_debug)
		self.tables_manager = TablesManager.TablesManager(db_name=self.db_info.database, db_user=self.db_info.user, db_password=self.db_info.password, is_debug=self.is_debug)
		self.categories_manager = CategoriesManager.CategoriesManager(db_name=self.db_info.database, db_user=self.db_info.user, db_password=self.db_info.password, is_debug=self.is_debug)
		self.settings_manager = SettingsManager.SettingsManager(db_name=self.db_info.database, db_user=self.db_info.user, db_password=self.db_info.password, is_debug=self.is_debug)
		self.foods_manager = FoodsManager.FoodsManager(db_name=self.db_info.database, db_user=self.db_info.user, db_password=self.db_info.password, is_debug=self.is_debug)
		self.addresses_manager = AddressesManager.AddressesManager(db_name=self.db_info.database, db_user=self.db_info.user, db_password=self.db_info.password, is_debug=self.is_debug)
		self.offlineorders_manager = OfflineOrdersManager.OfflineOrdersManager(db_name=self.db_info.database, db_user=self.db_info.user, db_password=self.db_info.password, is_debug=self.is_debug)


