#include <eosio/eosio.hpp>

using namespace eosio;

class [[eosio::contract]] hokipoki : public contract {
public:
    using contract::contract;

    [[eosio::action]]
    void hello(name user) {
        print("Hello, ", user);
    }
};
