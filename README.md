![](https://www.dictionary.com/e/wp-content/uploads/2018/10/hokie-2-300x300.jpg)
# `hokipoki` is the [EOSIO](https://eos.io) Smart Contract that powers <span style="color: #E87722;">Hokie</span><span style="color: #8B1F41;">Tickets</span>
The `hokipoki` smart contract is defined by the C++ code in `hokipoki.cpp`, and describes tables and actions used to manage studen athletic tickets on the blockchain in a safe, secure, and fair way. 

`hokipoki` should be deployed using `cleos`, to an account of the same name. More information is in the [Using](#using) section

## Tables
`hokipoki`'s core logic depends on four tables, plus one table that is used by higher levels of the HokieTickets application for user management:

- `games`
- `tickets`
- `lottoentries`
- `auctions`
- `users` (supplimentary)

### `games`
Games have the following fields:
- `uint64_t id`
- `uint64_t date` The date of the game in YYYYMMDDHHmm format
- `uint64_t number` The ordinal number of the game on that day, the first game on a particular day is number 1, then 2, and so on. Games can be uniquely identified by their date and number.
- `bool lottery_open` Whether or not the lottery is open
- `uint64_t initial_face_value` The initial face value for new tickets, in 100ths of a hokietoken
- `std::string name` The name of the game
- `std::string location` The location of the game
- `uint64_t lottery_opens` When the lottery opens, in YYYYMMDDHHmm format
- `uint64_t lottery_closes` When the lottery closes, in YYYYMMDDHHmm format
- `uint64_t reward` The reward to give students when their ticket is scanned, in 100ths of a hokietoken
- `uint64_t game_type` The game type. The game types are described below:

	0  FOOTBALL
	1  MENS_BASKETBALL
	2  WOMANS_BASKETBALL
	3  MENS_SOCCER
	4  WOMENS_SOCCER
	5  BASEBALL
	6  CROSS_COUNTRY
	7  MENS_GOLF
	8  WOMENS_GOLF
	9  LACROSSE
	10 SOFTBALL
	11 SWIMMING_AND_DIVING
	12 MENS_TENNIS
	13 WOMENS_TENNIS
	14 TRACK_AND_FIELD
	15 VOLLEYBALL
	16 WRESTLING

`games` has a secondary index on `date`, so you can easily see what games are on a given day, or after or before a certain day

### `tickets`
Tickets have the following fields:

- `uint64_t id`
- `uint64_t game_id` The game that the ticket is for
- `name owner` The current owner of the ticket, or `hokipoki` if it's not owned by any student
- `uint64_t face_value` The face value of the ticket, in 100ths of a hokietoken
- `bool for_lottery` Whether the ticket is reserved for the lottery
- `bool attended` Whether the ticket has been used to attend the game

`tickets` has a secondary index on `owner`, so viewing all tickets owned by a particular user can be a fast and efficient query

### `lottoentries`
Lottery entries have the following fields:

- `uint64_t id`
- `name user` The user entered in the lottery
- `uint64_t game_id` The game the user is entered into
- `uint64_t random_1` Random values, see below
- `uint64_t random_2` 
- `uint64_t random_3`
- `uint64_t random_4`

All four random values from every student entered into the lottery are xored and otherwise combined together, so it's almost impossible for one student to choose their random values in a way that ensures a particular outcome. Even if you were the last student to enter the lottery, the only way you could construct the random values to ensure that you definitely got a ticket requires that you know the block number and block prefix of exactly when the administrator runs `executelotto`. In the future, `executelotto` will also accept a random number from the administrator that will also be used to seed the random number generator.

`lottoentries` has secondary indexes on both `user` and `game`, making executing lotteries, as well as entering and leaving lotteries efficient.

### `auctions`
Auctions have the following fields:
- `uint64_t ticket_id` The ID of the ticket being auctioned - Doubles as the ID of the auction
- `uint64_t game_id` Always equal to the game ID of the ticket
- `name auction_owner` Always equal to the owner of the ticket
- `uint64_t highest_bid` Current highest bid, in hokie tokens, or the initial bid if nobody has made a bid
- `name top_bidder` Current highest bidder, or `auction_owner` if nobody has made a bid
- `uint64_t end_date` The end date of the auction, in YYYYMMDDHHmm format

`auctions` has secondary indexes on `game_id` and `top_bidder`. After an auction has been executed (which must be after its end date), the auction is deleted.

### `users`
Each user has the following field:
- `name user` The user's eosio username

Users is a supplimentary table not used by any actions (except `adduser`) - it exists to store the list of users who have been created using the HokieTickets web application, and is useful to administrators for seeing the current distribution of hokietokens, tickets, lottery entries, and so on.

## Actions

`hokipoki` defines 16 actions, which are documented in `hokipoki.contracts.md`

### Student Actions
#### Ticket Management
- `buy` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#buy)
- `sell` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#sell)
#### Lottery Management
- `enterlottery` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#enterlottery)
- `leavelottery` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#leavelottery)
- `creatauction` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#creatauction)

#### Auction Management
- `bid` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#bid)
- `execauction1` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#execauction1)
- `execauction2` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#execauction2)
- `cancelauctn` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#cancelauctn)

### Administrator Actions
- `creategame` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#creategame)
- `openlottery` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#openlottery)
- `adduser` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#adduser)
- `rewarduser` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#rewarduser)
- `aucexecall` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#aucexecall)
### Debug Actions
- `reset` - [Documentation](https://git.cs.vt.edu/goblins/hokipoki/blob/master/hokipoki.contracts.md#reset)

## Using

To compile `hokipoki`, simply run `make hokipoki.wasm`. This will invoke `eosio-cpp` to build `hokipoki.wasm` and `hokipoki.abi`.

If you're running on a machine or virtual machine with only one or two cores, `eosio-cpp` usually deadlocks and never completes. Prefixing your `make` command with `strace -f` significantly lowers the chance that it deadlocks. 

Once you've built `hokipoki.wasm` and `hokipoki.abi`, you can deploy it to an already-existing `hokipoki` account using `make deploy`, which uses `cleos set contract` to update the code and abi on the blockchian.

`make clean` will remove the `.abi` and `.wasm` files, and `make all` will first clean, then build and deploy.

Once `hokipoki` is deployed, you can start interacting with it by running actions using `cleos push action`, for example, `cleos push action hokipoki buy "['nilesr', 23]" -p nilesr@active` would allow `nilesr` to buy the ticket with id 23. 

You can see the data in the blockchain using `cleos get table`, like `cleos get table hokipoki hokipoki tickets`. You can find entries with a specific Id by passing -U and -L to cleos, for example, `cleos get table -U 23 -L 23 hokipoki hokipoki tickets` will display only ticket 23.

Shortcuts for these actions are described in the [Shortcuts](#shortcuts) section.

## Shortcuts

TODO

