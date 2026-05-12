SHELL=/bin/bash

.PHONY: switchboard
switchboard:
	cd switchboard; uv run twistd -noy switchboard.tac --pidfile=switchboard.pid

.PHONY: switchboard-debug
switchboard-debug:
	cd switchboard; uv run twistd --debug -noy switchboard.tac --pidfile=switchboard.pid

.PHONY: frontend
frontend:
	cd frontend; uv run uvicorn app:app --reload  --reload-dir="./" --reload-dir="../canarytokens" --host 0.0.0.0 --port 8082


.PHONY: test
test:
	cd tests; \
	TEST_HOST=`docker network inspect canarytokens_devcontainer_default | jq '.[0].Containers | to_entries[].value | select(.Name == "canarytokens_devcontainer-app-1").IPv4Address' | sed -E 's/"//g; s/\/[0-9]+//'` \
	uv run coverage run --source=../canarytokens -m pytest . -v; \
	uv run coverage report -m

.PHONY: testlive
testlive:
	cd tests; \
	CANARY_CHANNEL_MYSQL_PORT=3306 TEST_HOST=jingwei.tools LIVE=True uv run coverage run --source=integration -m pytest integration; \
	uv run coverage report -m; \

.PHONY: units
units:
	cd tests; \
	uv run coverage run --source=../canarytokens -m pytest units -v; \
	uv run coverage report -m
