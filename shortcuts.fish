function create_game 
	cleos push action hokipoki creategame "["$argv[1]", "$argv[2]", "$argv[3]", "$argv[4]", \""$argv[5]"\", \""$argv[6]"\", "$argv[7]", "$argv[8]"]" -p hokipoki@active
end

function buy 
	cleos push action hokipoki buy "[\""$argv[1]"\", "$argv[2]"]" -p "$argv[1]"@active
end
function sell 
	cleos push action hokipoki sell "[\""$argv[1]"\", "$argv[2]"]" -p "$argv[1]"@active
end

function enter_lottery
	set r1 (head -c 8 /dev/urandom | xxd -p)
	set r2 (head -c 8 /dev/urandom | xxd -p)
	set r3 (head -c 8 /dev/urandom | xxd -p)
	set r4 (head -c 8 /dev/urandom | xxd -p)
	cleos push action hokipoki enterlottery "[\""$argv[1]"\", "$argv[2]", 0x"$r1", 0x"$r2", 0x"$r3", 0x"$r4"]" -p "$argv[1]"@active
end

function leave_lottery
	cleos push action hokipoki leavelottery "[\""$argv[1]"\", "$argv[2]"]" -p "$argv[1]"@active
end

function execute_lottery
	cleos push action hokipoki executelotto "["$argv[1]"]" -p hokipoki@active
end

function open_lottery
	cleos push action hokipoki openlottery "["$argv[1]"]" -p hokipoki@active
end

function reset
	cleos push action hokipoki reset '[]' -p hokipoki@active
end

function games
	cleos get table hokipoki hokipoki games -l -1
end
function lottery_entries
	cleos get table hokipoki hokipoki lottoentries -l -1
end
function tickets
	cleos get table hokipoki hokipoki tickets -l -1
end

function balance
	cleos get currency balance eosio.token $argv[1] HTK
end

function transfer
	set htk $argv[3]
	cleos push action eosio.token transfer "[\""$argv[1]"\", \""$argv[2]"\", \""$htk\ HTK"\", \""$argv[4]"\"]" -p "$argv[1]"@active
end
