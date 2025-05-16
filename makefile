SHELL=/bin/bash

.PHONY: switchboard
switchboard:
	cd switchboard; poetry run twistd -noy switchboard.tac --pidfile=switchboard.pid

.PHONY: switchboard-debug
switchboard-debug:
	cd switchboard; poetry run twistd --debug -noy switchboard.tac --pidfile=switchboard.pid

.PHONY: frontend
frontend:
	cd frontend; poetry run uvicorn app:app --reload --reload-dir ../canarytokens --reload-dir ./ --log-config log.ini --host 0.0.0.0 --port 8082

.PHONY: testv3
testv3:
	cd tests; \
	TEST_HOST=`docker network inspect canarytokens_devcontainer_default | jq '.[0].Containers | to_entries[].value | select(.Name == "canarytokens_devcontainer-app-1").IPv4Address' | sed -E 's/"//g; s/\/[0-9]+//'` \
	poetry run coverage run --source=../canarytokens -m pytest . --runv3 -v; \
	poetry run coverage report -m

.PHONY: testv3live
testv3live:
	cd tests; \
	CANARY_CHANNEL_MYSQL_PORT=3306 TEST_HOST=jingwei.tools LIVE=True poetry run coverage run --source=integration -m pytest integration --runv3; \
	poetry run coverage report -m; \

.PHONY: unitsv3
unitsv3:
	cd tests; \
	poetry run coverage run --source=../canarytokens -m pytest units --runv3 -v; \
	poetry run coverage report -m

.PHONY: testv2
testv2:
	cd tests; \
	poetry run pytest integration --runv2  --pdb

.PHONY: testv2-s
testv2-s:
	cd tests; \
	poetry run pytest -s integration --runv2  --pdb
