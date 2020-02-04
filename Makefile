all: hokipoki.wasm deploy

hokipoki.wasm:
	eosio-cpp -abigen -o hokipoki.wasm hokipoki.cpp

deploy:
	cleos set contract hokipoki . -p hokipoki@active

.PHONY: deploy all
