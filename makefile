SHELL=/bin/bash

.PHONY: switchboard
switchboard:
	cd switchboard; poetry run twistd -noy switchboard.tac --pidfile=switchboard.pid

.PHONY: switchboard-debug
switchboard-debug:
	cd switchboard; poetry run twistd --debug -noy switchboard.tac --pidfile=switchboard.pid

.PHONY: frontend
frontend:
	cd frontend; poetry run uvicorn app:app --reload  --reload-dir="./" --reload-dir="../canarytokens" --host 0.0.0.0 --port 8082


.PHONY: test
test:
	cd tests; \
	TEST_HOST=`docker network inspect canarytokens_devcontainer_default | jq '.[0].Containers | to_entries[].value | select(.Name == "canarytokens_devcontainer-app-1").IPv4Address' | sed -E 's/"//g; s/\/[0-9]+//'` \
	poetry run coverage run --source=../canarytokens -m pytest . -v; \
	poetry run coverage report -m

.PHONY: testlive
testlive:
	cd tests; \
	CANARY_CHANNEL_MYSQL_PORT=3306 TEST_HOST=jingwei.tools LIVE=True poetry run coverage run --source=integration -m pytest integration; \
	poetry run coverage report -m; \

.PHONY: units
units:
	cd tests; \
	poetry run coverage run --source=../canarytokens -m pytest units -v; \
	poetry run coverage report -m
