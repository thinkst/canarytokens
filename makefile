SHELL=/bin/bash

.PHONY: switchboard
switchboard:
	cd switchboard; poetry run twistd -noy switchboard.tac --pidfile=switchboard.pid

.PHONY: backend
backend:
	cd backend; poetry run uvicorn app:app --reload

.PHONY: testv3
testv3:
	TEST_HOST=`docker network inspect canarytokensv3_devcontainer_default | jq '.[0].Containers | to_entries[].value | select(.Name == "canarytokensv3_devcontainer-app-1").IPv4Address' | sed -E 's/"//g; s/\/[0-9]+//'` \
	poetry run coverage run --source=./canarytokens -m pytest tests/ --runv3
	poetry run coverage report -m

.PHONY: testv3live
testv3live:
	CANARY_CHANNEL_MYSQL_PORT=3306 TEST_HOST=jingwei.tools LIVE=True poetry run coverage run --source=./tests/integration -m pytest tests/integration --runv3
	poetry run coverage report -m

.PHONY: unitsv3
unitsv3:
	poetry run coverage run --source=./canarytokens -m pytest tests/units/ --runv3
	poetry run coverage report -m

.PHONY: testv2
testv2:
	poetry run pytest tests/integration/ --runv2  --pdb

.PHONY: testv2-s
testv2-s:
	poetry run pytest -s tests/integration/ --runv2  --pdb
