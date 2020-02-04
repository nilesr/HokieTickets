#include <eosio/eosio.hpp>

using namespace eosio;

class [[eosio::contract("hokipoki")]] hokipoki : public eosio::contract {
public:
    using contract::contract;

    [[eosio::action]]
    void hello(name user) {
        print("Hello, ", user);
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
