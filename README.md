![](https://www.dictionary.com/e/wp-content/uploads/2018/10/hokie-2-300x300.jpg)
# `libgoblin` is the [EOSIO](https://eos.io) blockchain integration library that powers HokieTickets
`libgoblin` provides an interface for python code to execute actions on the blockchain, as well as retrieve information such as user balances, ABI information, and data stored in tables. 

`libgoblin` also includes another module, `goblin_auth`, that provides support for logging students in to HokieTickets and keeping them logged in using a session cookie.

## `libgoblin` quirks

TODO - write about `_try_symbolize_names`

## `libgoblin`'s responsibilities

### Retrieving information from EOSIO

`libgoblin`'s primary method of retrieving information from the blockchain is the output of `cleos`. `libgoblin` offers the following functions to aid in getting general information out of the blockchain:

- `get_info` Retrieves general information about the running eosio instance, such as version number and last block number
- `get_user_info` Retrieves general information about a particular user
- `get_currency_stats` Retrieves general information about the hokietoken currency, such as the current currency supply
- `get_balance` Gets a user's balance of HTK
- `get_raw_table` Gets a full table from the blockchain
- `get_declared_tables` Retrieves some ABI information
- `get_history` Retrieves transaction history for a given user
- `get_active_public_keys` Gets public keys currently in use for a particular user

`libgoblin` also provides the following functions for retrieving information from of the `hokipoki` smart contract, with logic specifically set up for HokieTickets:

- `user_tickets`
- `filtered_date_games` Returns all games after a given day
- `get_game`
- `get_ticket`
- `get_auction`
- `get_tickets_for_game`
- `is_ticket_available`
- `is_lottery_available`
- `user_has_ticket`
- `get_lottery_entries_by_user`
- `get_lottery_entries_by_game`
- `user_in_lottery`
- `get_num_of_lottery` Returns the number of tickets reserved for the lottery for a specific game
- `lottery_entries_by_game`
- `get_past_tickets` Gets a user's tickets for games that were in the past, or have been attended
- `active_tickets` Inverse of `get_past_tickets`
- `auction_for_ticket_id`
- `get_ticket_by_id`
- `get_auction_by_ticket_id`
- `auction_ended`
- `get_auctions_by_name`
- `get_auctions_by_game`
- `get_auctions_user_bid`
- `get_auction_groups` Returns auctions grouped by game

### Modifying information on the blockchain and executing actions

The following functions are also defined, and run actions on the blockchain to update the state of the application. Since all of the HokieTickets information is stored on the blockchain, these are necessary

Functions for `keosd`:
- `import_key` Imports a given private key into the system wallet. Used in account creation, described in the [User Account Management](#user-account-management) section

Functions for `eosio.token`:
- `transfer` Gives money to a student from `hokipoki`
- `transfer_from` A more general transfer function that takes both a sender and a recipient

Functions for `hokipoki`:
- `buy`
- `sell`
- `enter_lottery`
- `leave_lottery`
- `create_auction`
- `bid`
- `execute_auction_winner`
- `execute_auction_owner`
- `cancel_auction`
- `execute_lottery`
- `open_lottery`
- `create_game`
- `execute_all_auctions`
- `reset`
- `penalize_users`
- `reward_user`

The functions for `hokipoki` map directly onto the actions on the blockchain smart contract, which are documented in [`hokipoki`'s documentation](https://git.cs.vt.edu/goblins/hokipoki#readme)

### Helper functions for HokieTickets

- `format_htk` 
- `debug_format` Pretty printing function for the specific type of objects that `libgoblin` uses, described in the [Quirks](#libgoblin-quirks) section
- `get_game_type` Given an integer game type like 4, returns a human-readable game type like "Women's Soccer"
- `format_date`
- `format_datetime`
- `to_json` Serializes a special libgoblin object (described in [Quirks](#libgoblin-quirks)) into json, since `json.dumps()` treats them as arrays
- `s` Used for plurals, for example, called in places that might need to print "1 ticket" or "3 tickets"
- `get_logo` Gets the logo to be displayed on the frontend for a particular game

### QR code management functionality

- `get_qr_code_key_byte`
- `get_qr_code_data` Returns the data to be encoded into a QR code for a specific ticket
- `get_qr_code` Returns a PNG image of a QR code for a ticket
- `get_qr_code_data_uri`
- `scan_qr_code` Given the deserialized stream from a qr code, calls `reward_user` to mark the ticket as being used and give the user their reward of hokietokens. Fails if the ticket is invalid, has been transferred to another user, or has already been used to attend.
 
### User Account Management
User account creation is handled by `libgoblin`, which entails creating accounts and checking the permissions of existing accounts. These functions are

- `create_account`
- `check_permissions_grant`

Creating an account involves:

1. Creating a new keypair for the user, and importing that private key into the system wallet
2. Creating an account on the blockchain with the owner key set to the eosio system key
3. Updating the `active` permission on the account to require either the private key generated in step 1, or the `eosio.code` permission of `hokipoki`, to allow the `hokipoki` smart contract to execute inline actions on the user's behalf.
4. Running the `adduser` action on `hokipoki`, ensuring that the new user is added to the table of all users
5. Returning the public and private keypair that was generated to the administrator, so they can be delivered to the user.
