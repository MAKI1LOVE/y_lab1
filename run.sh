cp .env app/.env
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -k 'with_db'
uvicorn src.main:app --host 127.0.0.1 --port 8000
