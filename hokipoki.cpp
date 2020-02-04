#include <eosio/eosio.hpp>
#include <algorithm>

using namespace eosio;

class [[eosio::contract("hokipoki")]] hokipoki : public eosio::contract {
public:
    using contract::contract;

    [[eosio::action]]
    void creategame(uint64_t day, uint64_t tickets, uint64_t tickets_for_lotto, uint64_t price) {
        require_auth(get_self());
        games_index games(get_self(), get_first_receiver().value);
        uint64_t new_id = 0;
        if (games.cbegin() != games.cend()) {
            new_id = std::max_element(games.cbegin(), games.cend(), [](const auto& a, const auto& b) { return a.id < b.id; })->id + 1;
        }
        games.emplace(get_self(), [new_id, day, tickets, tickets_for_lotto, price](auto& row) {
            row.id = new_id;
            row.date = day;
            row.number = 0; // TODO
            row.lottery_open = true;
        });
    }

private:
    struct [[eosio::table]] game {
        uint64_t id;
        uint64_t date;
        uint64_t number;
        bool lottery_open;
        uint64_t primary_key() const { return id; }
        uint64_t get_secondary_1() const { return date; }
    };

    struct [[eosio::table]] ticket {
        uint64_t id;
        uint64_t game_id;
        uint64_t face_value; // in HTK
        bool for_lottery;
        uint64_t primary_key() const { return id; }
        uint64_t get_secondary_1() const { return game_id; }
    };

    struct [[eosio::table]] lottery_entry {
        uint64_t id;
        uint64_t user_id;
        uint64_t game_id;
        uint64_t primary_key() const { return id; }
        uint64_t get_secondary_1() const { return user_id; }
        uint64_t get_secondary_2() const { return game_id; }
    };

    typedef eosio::multi_index<
        "games"_n,
        game,
        indexed_by<"bydate"_n, const_mem_fun<game, uint64_t, &game::get_secondary_1>>
    > games_index;

    typedef eosio::multi_index<
        "tickets"_n,
        ticket,
        indexed_by<"bygame"_n, const_mem_fun<ticket, uint64_t, &ticket::get_secondary_1>>
    > tickets_index;

    typedef eosio::multi_index<
        "lottoentries"_n /* exactly 13 chars */,
        lottery_entry,
        indexed_by<"bygame"_n, const_mem_fun<lottery_entry, uint64_t, &lottery_entry::get_secondary_1>>,
        indexed_by<"byuser"_n, const_mem_fun<lottery_entry, uint64_t, &lottery_entry::get_secondary_2>>
    > lottery_entries_index;
};
