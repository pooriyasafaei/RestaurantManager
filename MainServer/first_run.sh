createdb -h localhost -p 5432 -U postgres RestaurantManager
psql -h localhost -p 5432 -U postgres RestaurantManager < Database.sql
source ../../venv/bin/activate
pip install -r requirements.txt
cd ..
python -m MainServer
