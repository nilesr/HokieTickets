<h1 class="contract">creategame</h1>
---
spec-version: 0.1.0
title: Create Game
summary: This action will create a game to be played on the specified day, as well as create the specified number of tickets for the game, all owned by hokipoki. Of those tickets, some will be set aside for the ticket lottery and will not be purchaseable. The number set aside for the lottery is equal to the `tickets_for_lotto` parameter. Tickets set aside for the lottery have a face value of 0.00 HTK, the rest of the tickets have a face value of `price`/100. This action must be invoked with the active permission of hokipoki.
icon:

<h1 class="contract">buy</h1>
---
spec-version: 0.1.0
title: Buy
summary: This action takes a user and a ticket id. It must be invoked with the active permission of the passed user. If the ticket ID exists, is owned by hokipoki, is not reserved for the ticket lottery, and the user has enough available HTK to purchase the ticket, and the user has allowed the `hokipoki` smart contract to execute inline actions on `eosio.token` with the user's active permission, then the face value of the ticket is transfered to hokipoki, and the owner of the ticket is set to the calling user.
icon:

<h1 class="contract">sell</h1>
---
spec-version: 0.1.0
title: Sell
summary: This action takes a user and a ticket id. It must be invoked with the active permission of the passed user. If the ticket ID exists, is owned by the calling user, and the user has allowed the `hokipoki` smart contract to execute inline actions on `eosio.token` with the user's active permission, then the face value of the ticket is transfered from hokipoki to the active user, and the owner of the ticket is set to `hokipoki`.
icon:

<h1 class="contract">enterlottery</h1>
---
spec-version: 0.1.0
title: Enter Lottery
summary: This action takes a user and a game id. It must be invoked with the active permission of the passed user. If the game ID exists, the lottery is still open for that game, and the user has not already entered into the ticket lottery for that game, then the user is entered into the ticket lottery. The four passed random values MUST be randomly generated. 
icon:

<h1 class="contract">leavelottery</h1>
---
spec-version: 0.1.0
title: Leave Lottery
summary: This action takes a user and a game id. It must be invoked with the active permission of the passed user. If the game ID exists, and the user has entered into the ticket lottery for that game, then the user is removed from the ticket lottery.
icon:

<h1 class="contract">executelotto</h1>
---
spec-version: 0.1.0
title: Execute Lottery
summary: This action takes a game id. It must be invoked with the active permission of `hokipoki`. If the game ID exists, and the lottery is still open for that game, each ticket for that game that is reserved for the lottery is assigned to a random student who has entered the lottery for that game, such that no two tickets are assigned to the same student. The face value for these tickets stays at 0. If there are more tickets than students, then for each remaining ticket, the owner stays as `hokipoki`, but their face value is updated to the price that was specified when the game was created. All tickets for the game are no longer reserved for the lottery.
icon:

<h1 class="contract">reset</h1>
---
spec-version: 0.1.0
title: Reset
summary: This action must be invoked with the active permission of `hokipoki`. All games, tickets, and lottery entries are deleted.
icon:


