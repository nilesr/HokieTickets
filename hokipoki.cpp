#include <eosio/eosio.hpp>
#include <eosio/asset.hpp>
#include <algorithm>

using eosio::contract, eosio::require_auth, eosio::check, eosio::name;

class [[eosio::contract("hokipoki")]] hokipoki : public eosio::contract {
public:
    using contract::contract;

    [[eosio::action]]
    void creategame(uint64_t day, uint64_t num_tickets, uint64_t tickets_for_lotto, uint64_t price) {
        require_auth(get_self());
        games_index games(get_self(), get_first_receiver().value);
        uint64_t new_id = 0;
        if (games.cbegin() != games.cend()) {
            new_id = games.crbegin()->id + 1;
        }
        uint64_t new_number = 0;
        auto dayindex = games.get_index<"bydate"_n>();
        auto dayiter = dayindex.lower_bound(day);
        while (dayiter != dayindex.end() && dayiter->date == day) {
            new_number = std::max(new_number, dayiter->number);
            dayiter++;
        }
        new_number += 1;

        games.emplace(get_self(), [new_id, day, new_number, price](auto& row) {
            row.id = new_id;
            row.date = day;
            row.number = new_number;
            row.lottery_open = true;
            row.initial_face_value = price;
        });

        tickets_index tickets(get_self(), get_first_receiver().value);
        uint64_t ticket_base_id = tickets.cbegin() == tickets.cend() ? 0 : tickets.crbegin()->id + 1;
        for (uint64_t i = 0; i < num_tickets; i++) {
            bool lotto = i < tickets_for_lotto;
            tickets.emplace(get_self(), [ticket_base_id, i, new_id, lotto, price](auto& row) {
                row.id = ticket_base_id + i;
                row.game_id = new_id;
                row.owner = "hokipoki"_n;
                row.face_value = lotto ? 0 : price;
                row.for_lottery = lotto;
            });
        }
    }

    [[eosio::action]]
    void buy(name user, uint64_t id) {
        require_auth(user);
        check(user != get_self(), "Only students may purchase tickets");
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(id);
        check(tptr != tickets.end(), "Ticket does not exist");
        check(tptr->owner == "hokipoki"_n, "Ticket is already owned");
        check(!tptr->for_lottery, "Ticket is not available for sale - it is reserved for the lottery");
        //eosio::transaction txn{};
        //txn.actions.emplace_back()
        check(tptr->face_value <= std::numeric_limits<int64_t>::max(), "Face value would integer overflow if converted to an int64_t");
        const eosio::asset ass{(int64_t) tptr->face_value, eosio::symbol{"HTK", 2}};
        eosio::action{
            eosio::permission_level{user, "active"_n},
            "eosio.token"_n,
            "transfer"_n,
            std::make_tuple(user, get_self(), ass, std::string{"Ticket Purchase"})
        }.send();
        tickets.modify(tptr, user, [user](auto& row) {
            row.owner = user;
        });
    }

    [[eosio::action]]
    void sell(name user, uint64_t id) {
        require_auth(user);
        check(user != get_self(), "Only students may sell tickets");
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(id);
        check(tptr != tickets.end(), "Ticket does not exist");
        check(tptr->owner == user, "You don't own this ticket!");
        check(tptr->face_value <= std::numeric_limits<int64_t>::max(), "Face value would integer overflow if converted to an int64_t");
        int new_face_value = tptr->face_value;
        if (new_face_value == 0) {
            games_index games(get_self(), get_first_receiver().value);
            auto gptr = games.find(tptr->game_id);
            check(gptr != games.end(), "Ticket is for a game that does not exist.");
            new_face_value = gptr->initial_face_value;
        } else {
            const eosio::asset ass{(int64_t) tptr->face_value, eosio::symbol{"HTK", 2}};
            eosio::action{
                eosio::permission_level{get_self(), "active"_n},
                "eosio.token"_n,
                "transfer"_n,
                std::make_tuple(get_self(), user, ass, std::string{"Ticket Sold"})
            }.send();
        }
        tickets.modify(tptr, user, [new_face_value](auto& row) {
            row.owner = "hokipoki"_n;
            row.face_value = new_face_value;
        });
    }

    [[eosio::action]]
    void enterlottery(name user, uint64_t game_id) {
        require_auth(user);
        games_index games(get_self(), get_first_receiver().value);
        auto gptr = games.find(game_id);
        check(gptr != games.end(), "That game does not exist.");
        check(gptr->lottery_open, "The lottery for that game has already ended.");
        lottery_entries_index lottery_entries(get_self(), get_first_receiver().value);
        auto userindex = lottery_entries.get_index<"byuser"_n>();
        auto eptr = userindex.lower_bound(user.value);
        while (eptr != userindex.end() && eptr->user == user) {
            check(eptr->game_id != game_id, "You are already in the lottery for that game.");
        }
        // TODO later - check if they already have a ticket for that game?
        uint64_t id = lottery_entries.cbegin() == lottery_entries.cend() ? 0 : lottery_entries.crbegin()->id + 1;
        lottery_entries.emplace(user, [id, user, game_id](auto& row) {
            row.id = id;
            row.user = user;
            row.game_id = game_id;
        });
    }

    [[eosio::action]]
    void reset() {
        require_auth(get_self());
        lottery_entries_index lottery_entries(get_self(), get_first_receiver().value);
        for (auto iter = lottery_entries.begin(); iter != lottery_entries.end(); iter = lottery_entries.erase(iter));
        tickets_index tickets(get_self(), get_first_receiver().value);
        for (auto iter = tickets.begin(); iter != tickets.end(); iter = tickets.erase(iter));
        games_index games(get_self(), get_first_receiver().value);
        for (auto iter = games.begin(); iter != games.end(); iter = games.erase(iter));
    }
private:
    struct [[eosio::table]] game {
        uint64_t id;
        uint64_t date;
        uint64_t number;
        bool lottery_open;
        uint64_t initial_face_value;
        uint64_t primary_key() const { return id; }
        uint64_t get_secondary_1() const { return date; }
    };

    struct [[eosio::table]] ticket {
        uint64_t id;
        uint64_t game_id;
        name owner;
        uint64_t face_value; // in HTK
        bool for_lottery;
        uint64_t primary_key() const { return id; }
        uint64_t get_secondary_1() const { return game_id; }
    };

    struct [[eosio::table]] lottery_entry {
        uint64_t id;
        name user;
        uint64_t game_id;
        uint64_t primary_key() const { return id; }
        uint64_t get_secondary_1() const { return user.value; }
        uint64_t get_secondary_2() const { return game_id; }
    };

    typedef eosio::multi_index<
        "games"_n,
        game,
        eosio::indexed_by<"bydate"_n, eosio::const_mem_fun<game, uint64_t, &game::get_secondary_1>>
    > games_index;

    typedef eosio::multi_index<
        "tickets"_n,
        ticket,
        eosio::indexed_by<"bygame"_n, eosio::const_mem_fun<ticket, uint64_t, &ticket::get_secondary_1>>
    > tickets_index;

    typedef eosio::multi_index<
        "lottoentries"_n /* exactly 13 chars */,
        lottery_entry,
        eosio::indexed_by<"bygame"_n, eosio::const_mem_fun<lottery_entry, uint64_t, &lottery_entry::get_secondary_1>>,
        eosio::indexed_by<"byuser"_n, eosio::const_mem_fun<lottery_entry, uint64_t, &lottery_entry::get_secondary_2>>
    > lottery_entries_index;
};
