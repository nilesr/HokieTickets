creategame() {
	cleos push action hokipoki creategame "["$1", "$2", "$3", "$4"]" -p hokipoki@active
}

buy() {
	cleos push action hokipoki buy "[\""$1"\", "$2"]" -p "$1"@active
}
sell() {
	cleos push action hokipoki sell "[\""$1"\", "$2"]" -p "$1"@active
}

enterlottery() {
	r1=$(head -c 8 /dev/urandom | xxd -p)
	r2=$(head -c 8 /dev/urandom | xxd -p)
	r3=$(head -c 8 /dev/urandom | xxd -p)
	r4=$(head -c 8 /dev/urandom | xxd -p)
	cleos push action hokipoki enterlottery "[\""$1"\", "$2", 0x"$r1", 0x"$r2", 0x"$r3", 0x"$r4"]" -p "$1"@active
}

execute_lottery() {
	cleos push action hokipoki executelotto "["$1"]" -p hokipoki@active
}

reset() {
	cleos push action hokipoki reset '[]' -p hokipoki@active
}

games() {
	cleos get table hokipoki hokipoki games -l -1
}
lottery_entries() {
	cleos get table hokipoki hokipoki lottoentries -l -1
}
tickets() {
	cleos get table hokipoki hokipoki tickets -l -1
}

balance() {
	cleos get currency balance eosio.token $1 HTK
}

transfer() {
	htk=$3
	cleos push action eosio.token transfer "[\""$1"\", \""$2"\", \""$htk\ HTK"\", \""$4"\"]" -p "$1"@active
}
