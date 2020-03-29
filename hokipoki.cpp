#include <eosio/eosio.hpp>
#include <eosio/asset.hpp>
#include <eosio/transaction.hpp>
#include <eosio/crypto.hpp>
#include <eosio/time.hpp>
#include <eosio/system.hpp>
#include <stdio.h>

extern "C" {
#include "gmtime_r.c"
}

using eosio::contract, eosio::require_auth, eosio::check, eosio::name;

struct random {
    uint64_t state = 0x4017117fdf7c8ee9;
    int n = 0;
    random() {
        auto mixedBlock = eosio::tapos_block_prefix() * eosio::tapos_block_num();
        eosio::checksum256 result = eosio::sha256((char*) &mixedBlock, sizeof(mixedBlock));
        static_assert(sizeof(result) / 8 >= 4, "pls");
        uint64_t* uptr = (uint64_t*) &result;
        update(uptr[0], uptr[1], uptr[2], uptr[3]);
    }
    void update(uint64_t r1, uint64_t r2, uint64_t r3, uint64_t r4) {
        check(n == 0, "already called get().");
        state ^= r1;
        while (r2 == 0 || r3 == 0) { r2++; r3++; }
        state ^= ((r2 % r3) * (r3 % r2) * r2 * r3);
        state ^= (r4 % 11) * r4 * r1;
    }
    // LCG based on glibc implementation
    uint32_t get() {
        n++;
        uint64_t s = state;
        for (int i = 0; i < n; i++) {
            s = (s * 1103515245 + 12345) % (1 << 31);
        }
        return s;
    }
};



class [[eosio::contract("hokipoki")]] hokipoki : public eosio::contract {
public:
    using contract::contract;

    uint64_t current_datetime() {
        time_t now = eosio::current_block_time().to_time_point().elapsed.to_seconds();
        now -= 4 * 3600; // time zone offset
        struct hokipoki_tm cal;
        hokipoki_gmtime_r(&now, &cal);
        return (((uint64_t) cal.tm_year + YEAR_BASE) * 100000000) + (((uint64_t) cal.tm_mon + 1) * 1000000) + ((uint64_t) cal.tm_mday * 10000) + ((uint64_t) cal.tm_hour * 100) + (uint64_t) cal.tm_min;
    }

    [[eosio::action]]
    void creategame(uint64_t day, uint64_t num_tickets, uint64_t tickets_for_lotto, uint64_t price, std::string name, std::string location, uint64_t lottery_opens, uint64_t lottery_closes,uint64_t reward,uint64_t game_type) {
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

        games.emplace(get_self(), [new_id, day, new_number, price, name, location, lottery_opens, lottery_closes,reward,game_type](auto& row) {
            row.id = new_id;
            row.date = day;
            row.number = new_number;
            row.lottery_open = false; // lottery is closed until the admin executes openlottery on the game
            row.initial_face_value = price;
            row.name = name;
            row.location = location;
            row.lottery_opens = lottery_opens;
            row.lottery_closes = lottery_closes;
            row.reward = reward;
            row.game_type = game_type;
        });

        tickets_index tickets(get_self(), get_first_receiver().value);
        uint64_t ticket_base_id = tickets.cbegin() == tickets.cend() ? 0 : tickets.crbegin()->id + 1;
        for (uint64_t i = 0; i < num_tickets; i++) {
            bool lotto = i < tickets_for_lotto;
            tickets.emplace(get_self(), [ticket_base_id, i, new_id, lotto, price,game_type](auto& row) {
                row.id = ticket_base_id + i;
                row.game_id = new_id;
                row.owner = "hokipoki"_n;
                row.face_value = lotto ? 0 : price;
                row.for_lottery = lotto;
                row.attended = false;
                row.game_type = game_type;
            });
        }
    }

    [[eosio::action]]
    void buy(name user, uint64_t id) {
        require_auth(user);
        check(user != get_self(), "Only students may purchase tickets.");
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(id);

        check(tptr != tickets.end(), "Ticket does not exist.");
        check(tptr->owner == "hokipoki"_n, "Ticket is already owned.");
        check(!tptr->for_lottery, "Ticket is not available for sale - it is reserved for the lottery.");
        
        uint64_t game_id = tptr->game_id;
        lottery_entries_index lottery_entries(get_self(), get_first_receiver().value);
        auto userindex = lottery_entries.get_index<"byuser"_n>();
        auto eptr = userindex.lower_bound(user.value);
        while (eptr != userindex.end() && eptr->user == user) {
            check(eptr->game_id != game_id, "You are already in the lottery for that game.");
            // if(eptr->game_id == game_id){
            //     printf("YOU FUCKING ALREADY HAVE TICKET\n");
            //     return;
            // }
            eptr++;
        }  

        // auto gameindex = tickets.get_index<"bygame"_n>();
        // auto tptr_2 = gameindex.lower_bound(game_id);
        // while(tptr_2 != gameindex.end() && tptr_2->game_id == game_id){
        //     check(tptr_2->owner != user, "You already own a ticket for that game.");
        //     tptr++;
        // }



        //eosio::transaction txn{};
        //txn.actions.emplace_back()
        check(tptr->face_value <= std::numeric_limits<int64_t>::max(), "Face value would integer overflow if converted to an int64_t.");
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
        check(user != get_self(), "Only students may sell tickets.");
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(id);
        check(tptr != tickets.end(), "Ticket does not exist.");
        check(tptr->owner == user, "You don't own this ticket.");
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
    void enterlottery(name user, uint64_t game_id, uint64_t r1, uint64_t r2, uint64_t r3, uint64_t r4) {
        require_auth(user);
        games_index games(get_self(), get_first_receiver().value);
        auto gptr = games.find(game_id);
        check(gptr != games.end(), "That game does not exist.");
        check(gptr->lottery_open, "The lottery for that game is not open.");
        
        lottery_entries_index lottery_entries(get_self(), get_first_receiver().value);
        auto userindex = lottery_entries.get_index<"byuser"_n>();
        auto eptr = userindex.lower_bound(user.value);
        while (eptr != userindex.end() && eptr->user == user) {
            check(eptr->game_id != game_id, "You are already in the lottery for that game.");
            eptr++;
        }


        tickets_index tickets{get_self(),get_first_receiver().value};
        auto gameindex = tickets.get_index<"bygame"_n>();
        auto tptr = gameindex.lower_bound(game_id);
        while(tptr != gameindex.end() && tptr->game_id == game_id){
            check(tptr->owner != user, "You already own a ticket for that game.");
            tptr++;
        }

        uint64_t id = lottery_entries.cbegin() == lottery_entries.cend() ? 0 : lottery_entries.crbegin()->id + 1;
        lottery_entries.emplace(user, [id, user, game_id, r1, r2, r3, r4](auto& row) {
            row.id = id;
            row.user = user;
            row.game_id = game_id;
            row.random_1 = r1;
            row.random_2 = r2;
            row.random_3 = r3;
            row.random_4 = r4;
        });
    }

    [[eosio::action]]
    void leavelottery(name user, uint64_t game_id) {
        require_auth(user);
        games_index games(get_self(), get_first_receiver().value);
        auto gptr = games.find(game_id);
        check(gptr != games.end(), "That game does not exist.");
        check(gptr->lottery_open, "The lottery for that game has already ended.");
        lottery_entries_index lottery_entries(get_self(), get_first_receiver().value);
        auto userindex = lottery_entries.get_index<"byuser"_n>();
        auto eptr = userindex.lower_bound(user.value);
        while (eptr != userindex.end() && eptr->user == user) {
            if (eptr->game_id == game_id) {
                userindex.erase(eptr);
                return;
            }
            eptr++;
        }
        check(false, "You are not in the lottery for that game.");
    }

    [[eosio::action]]
    void executelotto(uint64_t game_id) {
        require_auth(get_self());
        games_index games(get_self(), get_first_receiver().value);
        auto gptr = games.find(game_id);
        check(gptr != games.end(), "Game does not exist.");
        check(gptr->lottery_open, "Lottery is not open for that game.");
        random r{};
        uint64_t price = gptr->initial_face_value;

        // First, make a list of all of the students who entered the lottery, and remove all the entries for this game while we're at it
        std::vector<uint64_t> students{};
        lottery_entries_index lottery_entries(get_self(), get_first_receiver().value);
        auto entries_by_game = lottery_entries.get_index<"bygame"_n>();
        auto eptr = entries_by_game.lower_bound(game_id);
        while (eptr != entries_by_game.end() && eptr->game_id == game_id) {
            students.emplace_back(eptr->user.value);
            r.update(eptr->random_1, eptr->random_2, eptr->random_3, eptr->random_4);
            eptr = entries_by_game.erase(eptr);
        }

        // Now for each ticket, pick a random student, give the ticket to them, and remove them from the set
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto bygame = tickets.get_index<"bygame"_n>();
        for (auto tptr = bygame.lower_bound(game_id); tptr != bygame.end() && tptr->game_id == game_id; tptr++) {
            if (!tptr->for_lottery) continue;
            bygame.modify(tptr, get_self(), [](auto& row) {
                row.for_lottery = false;
            });
            if (students.size() > 0) {
                uint64_t idx = r.get() % students.size();
                auto owner = eosio::name{students.at(idx)};
                bygame.modify(tptr, get_self(), [owner](auto& row) {
                    row.owner = owner;
                });
                require_recipient(owner); // ensures that it appears in the action history for that user, so they will see that they got a ticket on their account page
                students.erase(students.begin() + idx);
            } else {
                bygame.modify(tptr, get_self(), [price](auto& row) {
                    row.face_value = price;
                });
            }
        }

        // Mark lottery as no longer open
        games.modify(gptr, get_self(), [](auto& row) {
            row.lottery_open = false;
        });
    }

    [[eosio::action]]
    void openlottery(uint64_t game_id) {
        require_auth(get_self());
        games_index games(get_self(), get_first_receiver().value);
        auto gptr = games.find(game_id);
        check(gptr != games.end(), "That game does not exist.");
        check(!gptr->lottery_open, "The lottery for that game is already open.");
        games.modify(gptr, get_self(), [](auto& row) {
            row.lottery_open = true;
        });
    }

    [[eosio::action]]
    void adduser(name user) {
        require_auth(get_self());
        users_index users(get_self(), get_first_receiver().value);
        users.emplace(get_self(), [user](auto& row) {
            row.user = user;
        });
    }

    [[eosio::action]]
    void rewarduser(uint64_t ticket_id) {
        require_auth(get_self());
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(ticket_id);
        check(tptr != tickets.end(), "Ticket does not exist");
        check(!tptr->attended, "Ticket is already used");
        tickets.modify(tptr, tptr->owner, [](auto& row) {
            row.attended = true;
        });
        games_index games(get_self(), get_first_receiver().value);
        auto gptr = games.find(tptr->game_id);
        check(gptr != games.end(), "Game does not exist");
        const eosio::asset ass{(int64_t) gptr->reward, eosio::symbol{"HTK", 2}};
        eosio::action{
            eosio::permission_level{get_self(), "active"_n},
            "eosio.token"_n,
            "transfer"_n,
            std::make_tuple(get_self(), tptr->owner, ass, std::string{"Reward"})
        }.send();
    }

    [[eosio::action]]
    void creatauction(uint64_t ticket_id, uint64_t initial_bid, uint64_t end_date) {
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(ticket_id);
        check(tptr != tickets.end(), "Ticket does not exist");
        auto owner = tptr->owner;
        require_auth(owner);
        auctions_index auctions(get_self(), get_first_receiver().value);
        auto game_id = tptr->game_id;
        auto aptr = auctions.find(ticket_id);
        check(aptr == auctions.end(), "There is already an auction in progress for that ticket");
        games_index games(get_self(), get_first_receiver().value);
        auto gptr = games.find(game_id);
        check(gptr != games.end(), "Game does not exist");
        check(initial_bid >= tptr->face_value, "Initial bid must be greater than or equal to the face value of the ticket!");
        check(initial_bid >= gptr->initial_face_value, "Initial bid must be greater than or equal to the face value of the ticket!");
        uint64_t now = current_datetime();
        check(now < end_date, "End date is in the past!");
        check((end_date/10000) < (gptr->date/10000), "End date is on or after the day of the game! Auctions must end before the day of the game.");
        auctions.emplace(get_self(), [ticket_id, game_id, initial_bid, end_date, owner](auto& row) {
            row.ticket_id = ticket_id;
            row.game_id = game_id;
            row.highest_bid = initial_bid;
            row.top_bidder = owner;
            row.auction_owner = owner;
            row.end_date = end_date;
        });
    }

    [[eosio::action]]
    void bid(uint64_t ticket_id, name user, uint64_t bid) {
        require_auth(user);
        // TODO check that the user is not the current top bidder on the ticket
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(ticket_id);
        check(tptr != tickets.end(), "That ticket does not exist");
        check(tptr->owner != user, "You cannot bid in your own auction!");
        auctions_index auctions(get_self(), get_first_receiver().value);
        auto aptr = auctions.find(ticket_id);
        check(aptr != auctions.end(), "There is no ongoing auction for that ticket");
        check(aptr->end_date >= current_datetime(), "That auction has already ended");
        check(aptr->highest_bid + 100 <= bid, "You must bid at least 1.00 HTK greater than the previous highest bid");
        if (aptr->top_bidder != tptr->owner) {
            const eosio::asset ass{(int64_t) aptr->highest_bid, eosio::symbol{"HTK", 2}};
            eosio::action{
                eosio::permission_level{get_self(), "active"_n},
                "eosio.token"_n,
                "transfer"_n,
                std::make_tuple(get_self(), aptr->top_bidder, ass, std::string{"Outbid in an auction - bid money returned"})
            }.send();
        }
        const eosio::asset ass{(int64_t) bid, eosio::symbol{"HTK", 2}};
        eosio::action{
            eosio::permission_level{user, "active"_n},
            "eosio.token"_n,
            "transfer"_n,
            std::make_tuple(user, get_self(), ass, std::string{"Bid on an auction"})
        }.send();
        auctions.modify(aptr, get_self(), [user, bid](auto& row) {
            row.top_bidder = user;
            row.highest_bid = bid;
        });
    }

    auto find_auction_for_exec(uint64_t auction_id) {
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(auction_id);
        check(tptr != tickets.end(), "Ticket does not exist");
        auctions_index auctions(get_self(), get_first_receiver().value);
        auto aptr = auctions.find(auction_id);
        check(aptr != auctions.end(), "There is no auction in progress for that ticket.");
        check(aptr->end_date < current_datetime(), "The auction cannot be executed, it is still active!");
        return std::pair<decltype(aptr), decltype(tptr)>{aptr, tptr};
    }

    [[eosio::action]]
    void execauction1(uint64_t ticket_id) {
        auto aptr = find_auction_for_exec(ticket_id).first;
        require_auth(aptr->top_bidder);
        exec_auction(ticket_id);
    }

    [[eosio::action]]
    void execauction2(uint64_t ticket_id) {
        auto [aptr, tptr] = find_auction_for_exec(ticket_id);
        require_auth(tptr->owner);
        exec_auction(ticket_id);
    }

    void exec_auction(uint64_t ticket_id) {
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(ticket_id);
        auctions_index auctions(get_self(), get_first_receiver().value);
        auto aptr = auctions.find(ticket_id);
        check(tptr != tickets.end() && aptr != auctions.end(), "Should have been already verified before calling this function");
        if (aptr->top_bidder == tptr->owner) {
            auctions.erase(aptr);
            return;
        }
        require_recipient(aptr->top_bidder); // not sure what I'm gonna do with this just yet
        const eosio::asset ass{(int64_t) aptr->highest_bid, eosio::symbol{"HTK", 2}};
        eosio::action{
            eosio::permission_level{get_self(), "active"_n},
            "eosio.token"_n,
            "transfer"_n,
            std::make_tuple(get_self(), tptr->owner, ass, std::string{"Auction finished"})
        }.send();
        auto new_owner = aptr->top_bidder;
        tickets.modify(tptr, get_self(), [new_owner](auto& row) {
            row.owner = new_owner;
        });
        auctions.erase(aptr);
    }

    [[eosio::action]]
    void aucexecall(uint64_t game_id) {
        require_auth(get_self());
        games_index games(get_self(), get_first_receiver().value);
        auto gptr = games.find(game_id);
        check(gptr != games.end(), "Game does not exist");
        check((current_datetime()/10000) >= (gptr->date/10000), "It is not yet the day of the game");
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto bygame = tickets.get_index<"bygame"_n>();
        auctions_index auctions(get_self(), get_first_receiver().value);
        for (auto tptr = bygame.lower_bound(game_id); tptr != bygame.end() && tptr->game_id == game_id; tptr++) {
            auto aptr = auctions.find(tptr->id);
            if (aptr != auctions.end()) {
                exec_auction(tptr->id);
            }
        }
    }

    [[eosio::action]]
    void cancelauctn(uint64_t auction_id) {
        tickets_index tickets(get_self(), get_first_receiver().value);
        auto tptr = tickets.find(auction_id);
        check(tptr != tickets.end(), "That ticket does not exist");
        require_auth(tptr->owner);
        auctions_index auctions(get_self(), get_first_receiver().value);
        auto aptr = auctions.find(auction_id);
        check(aptr != auctions.end(), "There is no active auction on that ticket");
        check(aptr->top_bidder == tptr->owner, "The auction can't be cancelled, there are already active bids on it.");
        auctions.erase(aptr);
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
        std::string name;
        std::string location;
        uint64_t lottery_opens;
        uint64_t lottery_closes;
        uint64_t reward;
        uint64_t game_type;
        uint64_t primary_key() const { return id; }
        uint64_t get_secondary_1() const { return date; }
    };

    struct [[eosio::table]] ticket {
        uint64_t id;
        uint64_t game_id;
        name owner;
        uint64_t face_value; // in HTK
        bool for_lottery;
        bool attended;
        uint64_t game_type;
        uint64_t primary_key() const { return id; }
        uint64_t get_secondary_1() const { return game_id; }
    };

    struct [[eosio::table]] lottery_entry {
        uint64_t id;
        name user;
        uint64_t game_id;
        uint64_t random_1;
        uint64_t random_2;
        uint64_t random_3;
        uint64_t random_4;
        uint64_t primary_key() const { return id; }
        uint64_t get_secondary_1() const { return user.value; }
        uint64_t get_secondary_2() const { return game_id; }
    };

    struct [[eosio::table]] user {
        name user;
        uint64_t primary_key() const { return user.value; }
    };

    struct [[eosio::table]] auction {
        uint64_t ticket_id;
        uint64_t game_id;
        name auction_owner; // should always be equal to the owner of the ticket
        uint64_t highest_bid;
        name top_bidder;
        uint64_t end_date;
        uint64_t primary_key() const { return ticket_id; }
        uint64_t get_secondary_1() const { return game_id; }
        uint64_t get_secondary_2() const { return top_bidder.value; }
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
        eosio::indexed_by<"byuser"_n, eosio::const_mem_fun<lottery_entry, uint64_t, &lottery_entry::get_secondary_1>>,
        eosio::indexed_by<"bygame"_n, eosio::const_mem_fun<lottery_entry, uint64_t, &lottery_entry::get_secondary_2>>
    > lottery_entries_index;

    typedef eosio::multi_index<
        "users"_n,
        user
    > users_index;

    typedef eosio::multi_index<
        "auctions"_n,
        auction,
        eosio::indexed_by<"bygame"_n, eosio::const_mem_fun<auction, uint64_t, &auction::get_secondary_1>>,
        eosio::indexed_by<"bytop"_n, eosio::const_mem_fun<auction, uint64_t, &auction::get_secondary_2>>
    > auctions_index;
};
