// Format ticket values into HTK (i.e. 6000 -> "60.00 HTK")
function formatHTK(value) {
    var val = value.toString();
    return val.slice(0, -2) + "." + val.slice(-2) + " HTK";
}

// Format date from YYYYMMDDHHMM to "Month" DD, YYYY
function formatLongDate(date) {
    var months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ];

    date = date.slice(0, 8); // Cut off hours and minutes

    var month = Math.floor(date / 100) % 100;
    var day = date % 100;
    var year = Math.floor(date / 10000);

    return months[month - 1] + " " + day + ", " + year;
}

function formatTime(date) {
    var time = date.slice(8);

    var ampm = "am";
    var hour = parseInt(time.slice(0, 2));
    if (hour >= 12) {
        ampm = "pm"
    }
    hour = hour % 12;
    if (hour == 0) {
        hour = 12;
    }
    var minute = time.slice(2);

    return hour + ":" + minute + " " + ampm;
}

// Opens a modal window for confirming user actions before making request to server
function openWindow(user, id, action, info) {
    // Get modal
    var modal = document.getElementById("window");
    modal.style.display = "block";

    // Modal content
    var body = modal.querySelector(".modal-body");

    // Buttons
    var buttonArea = modal.querySelector(".button-area");
    // Find or create Confirm button
    var confirm = buttonArea.querySelector(".confirmButton");
    if (confirm == null) {
        confirm = buttonArea.appendChild(document.createElement("button"));
    }
    confirm.innerHTML = "Confirm";
    confirm.setAttribute("class", "confirmButton");
    confirm.style.display = "block";

    // Find or create "Go Back" button
    var back = buttonArea.querySelector(".backButton");
    if (back == null) {
        back = buttonArea.appendChild(document.createElement("button"));

        back.innerHTML = "Go Back";
        back.setAttribute("class", "backButton");
        back.onclick = function(event) {
            // Close the modal
            modal.style.display = "none";
            if (action != "bid") {
                location.reload();
            }
        }
    }


    // Find or create title
    var title = body.querySelector("#modalTitle");
    if (title == null) {
        title = body.appendChild(document.createElement("h1"));
        title.setAttribute("id", "modalTitle");
    }
    // Find or create inner text
    var text = body.querySelector("#modalText");
    if (text == null) {
        text = body.appendChild(document.createElement("div"));
        text.setAttribute("id", "modalText");
        // Use three lines of info in the block
        text.appendChild(document.createElement("p"));
        text.appendChild(document.createElement("p"));
        text.appendChild(document.createElement("p"));
    }

    // Set the text inside
    if (action == "buy") {
        title.innerHTML = "Confirm Ticket Purchase";
        text.children[0].innerHTML = "You are purchasing a ticket for <b>" + info['event_name'] + "</b>.";
        text.children[1].innerHTML = "Your current balance is <b>" + info['current_balance'] + " HTK</b>.";
        text.children[2].innerHTML = "Click <b>Confirm</b> to continue."
    } else if (action == "enter_lottery") {
        title.innerHTML = "Confirm Lottery Entry";
        text.children[0].innerHTML = "You are entering the lottery for <b>" + info['event_name'] + "</b>.";
        text.children[1].innerHTML = "Click <b>Confirm</b> to continue."
    } else if (action == "leave_lottery") {
        title.innerHTML = "Leaving Lottery";
        text.children[0].innerHTML = "You are leaving the lottery for <b>" + info['event_name'] + "</b>.";
        text.children[1].innerHTML = "Click <b>Confirm</b> to continue."
    } else if (action == "sell") {
        title.innerHTML = "Confirm Ticket Sale";
        text.children[0].innerHTML = "You are selling your ticket for <b>" + info['event_name'] + "</b>.";
        text.children[1].innerHTML = "Your current balance is <b>" + info['current_balance'] + " HTK</b>.";
        text.children[2].innerHTML = "Click <b>Confirm</b> to continue.";
    } else if (action == "create_auction") {
        title.innerHTML = "Confirm Ticket Auction";
        text.children[0].innerHTML = "You are auctioning your ticket for <b>" + info['event_name'] + "</b>.";
        text.children[1].innerHTML = "The ticket will start at a price of <b>" + formatHTK(info['ticket_value']) + "</b>.";
        text.children[2].innerHTML = "Click <b>Confirm</b> to continue.";
    } else if (action == "view_auction") {
        title.innerHTML = "Auction Details";
        text.children[0].innerHTML = "Highest bid: <b>" + formatHTK(info['highest_bid']) + "</b>.";;
        text.children[1].innerHTML = "Auction end date: <b>" + formatLongDate(info['end_date']) + " " + formatTime(info['end_date']) + "</b>.";
        if (info['highest_bid'] == info['ticket_value']) { // Nobody has bid
            text.children[2].innerHTML = "Nobody has bid in this auction. Click <b>Cancel Auction</b> to reclaim your ticket.";
            confirm.innerHTML = "Cancel Auction";
            confirm.setAttribute("style", "background-color: #BB0000;"); // Make button red for dangerous action
        } else {
            confirm.style.display = "none";
            text.children[2].innerHTML = "";
        }
    } else if (action == "bid") {
        title.innerHTML = "Add Bid";
        text.children[0].innerHTML = "You are adding a bid on a ticket <b>" + info['event_name'] + "</b>.";
        text.children[1].innerHTML = "The current highest bid is <b>" + formatHTK(info['highest_bid']) + "</b>.";
        text.children[2].innerHTML = "Input how much you would like to bid, and press <b>Continue</b> to submit.";

        var inputArea = body.querySelector("#inputArea");
        if (inputArea == null) {
            // Set up span to make it look nicer
            inputArea = text.appendChild(document.createElement('span'));
            inputArea.setAttribute("class", "input-area");
            inputArea.setAttribute("id", "inputArea");
        }
        // Reset inside because we need to reset values for the input
        inputArea.innerHTML = "";

        // Actual input object
        var input = inputArea.appendChild(document.createElement('input'));
        input.setAttribute("id", "bidAmount");
        input.setAttribute("type", "number");
        input.setAttribute("min", (parseInt(info['highest_bid']) / 100 + 1)); // Minimum is highest bid
        input.setAttribute("max", (parseInt(info['user_balance']))); // Maximum is user's balance
        input.setAttribute("step", 0.01);
        input.setAttribute("placeholder", (parseInt(info['highest_bid']) / 100 + 1));

        // Disable confirm button until user inputs a value
        // confirm.setAttribute("disabled", true);

        // function setEnabled() {
        //     console.log("triggered");
        //     confirm.removeAttribute("disabled");
        // }
        // input.addEventListener("input", setEnabled);

        // Show HTK at the end of input area
        inputArea.innerHTML += " HTK";
    }


    // On clicking confirm button, make request to execute action
    confirm.onclick = function(event) {
        // Send necessary information to backend
        if (action == "view_auction") { // Can only click "confirm" button if they are cancelling auction
            action = "cancel_auction";
        }
        var data = {
            action: action,
            user: user,
        };
        // Set up variable information
        if (action == "buy" || action == "enter_lottery" || action == "leave_lottery") {
            data['game_id'] = id;
        } else if (action == "sell" || action == "cancel_auction") {
            data['ticket_id'] = id;
        } else if (action == "create_auction") {
            data['ticket_id'] = id;
            data['initial_bid'] = parseInt(info['ticket_value']);
            data['end_date'] = parseInt(info['auction_date']);
        } else if (action == "bid") {
            data['ticket_id'] = id;
            data['bid_amount'] = body.querySelector("#bidAmount").value + "00";
        }
        console.log(data);

        // Send the request JSON
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            url: "/requests.pyhtml",
            error: (error) => {
                console.log(error);
                confirm.style.display = "none";
                body.innerHTML = error.responseText;
            },
        }).then((response) => {
            confirm.style.display = "none";

            console.log(response);
            var resp = JSON.parse(response);
            if (resp.hasOwnProperty("error")) { // Action failed
                text.innerHTML = resp.error;
            } else { // Other kind of success
                text.children[0].innerHTML = "Success!";
                if (action == "buy") {
                    text.children[0].innerHTML += " You have bought a ticket for <b>" + info['event_name'] + "</b>.";
                    text.children[1].innerHTML = "Your new balance is <b>" + resp['balance'] + " HTK</b>."
                    text.children[2].innerHTML = "Click <b>Go Back</b> to close this window.";
                } else if (action == "sell") {
                    text.children[0].innerHTML += " You have sold your ticket for <b>" + info['event_name'] + "</b>.";
                    text.children[1].innerHTML = "Your new balance is <b>" + resp['balance'] + " HTK</b>."
                    text.children[2].innerHTML = "Click <b>Go Back</b> to close this window.";
                } else if (action == "enter_lottery") {
                    text.children[0].innerHTML += " You have entered the lottery for <b>" + info['event_name'] + "</b>.";
                    text.children[1].innerHTML = "Check your tickets after the lottery has been executed to see if you won.";
                    text.children[2].innerHTML = "Click <b>Go Back</b> to close this window.";
                } else if (action == "leave_lottery") {
                    text.children[0].innerHTML += " You have left the lottery for <b>" + info['event_name'] + "</b>.";
                    text.children[1].innerHTML = "You will no longer be considered for lottery tickets in this game.";
                    text.children[2].innerHTML = "Click <b>Go Back</b> to close this window.";
                } else if (action == "create_auction") {
                    text.children[0].innerHTML += " Your ticket for <b>" + info['event_name'] + "</b> is now up for auction.";
                    text.children[1].innerHTML = "The auction will end automatically at <b>" + formatLongDate(info['auction_date']) + " " + formatTime(info['auction_date'])
                    "</b>.";
                    text.children[2].innerHTML = "Click <b>Go Back</b> to close this window.";
                } else if (action == "cancel_auction") {
                    text.children[0].innerHTML += " Your ticket for <b>" + info['event_name'] + "</b> is no longer up for auction.";
                    text.children[1].innerHTML = "";
                    text.children[2].innerHTML = "Click <b>Go Back</b> to close this window.";
                } else if (action == "bid") {
                    text.children[0].innerHTML += " You have added a bid for <b>" + info['event_name'] + "</b>.";
                    text.children[1].innerHTML = "The new highest bid is <b>" + formatHTK(data['bid_amount']) + "</b>.";
                    text.children[2].innerHTML = "Click <b>Go Back</b> to close this window.";
                    text.removeChild(text.children[3]);
                }
            }
            if (action != "bid") {
                location.reload();
            } else {
                populateListings(user);
            }
        });
    };
}

// Close modal
function closeWindow() {
    var modal = document.getElementById('window');
    modal.style.display = "none";
}

// If a modal is open and the user clicks outside of it, close the modal
window.onclick = function(event) {
    if (event.target.attributes.class && event.target.attributes.class.value == "modal") {
        event.target.style.display = "none";
        location.reload();
    }
}

function populateListings(user) {
    var selected = document.getElementById("gameSelect").options[gameSelect.selectedIndex].value;
    var selectedName = document.getElementById("gameSelect").options[gameSelect.selectedIndex].innerHTML;

    var data = {
        'user': true,
        'action': 'auction_listings',
        'game_id': parseInt(selected),
    };

    // Request the list of auctions from the backend
    $.ajax({
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(data),
        url: "/requests.pyhtml",
        error: (error) => {
            console.log(error);
            document.write(error.responseText);
        },
    }).then((data) => {
        // Get the list of auctions from the JSON
        var resp = JSON.parse(data);

        // Clear existing data rather than trying to overwrite
        var table = document.getElementById("auctionListings");
        table.innerHTML = "";

        if (resp.hasOwnProperty("Success")) { // && resp.hasOwnProperty("user_balance")) { // Retrieved a list of auctions
            // Need to make a function wrapper to pass in "Add Bid" button function
            function passArguments(user, auction_id, action, info) {
                return function() {
                    openWindow(user, auction_id, action, info);
                };
            }

            for (i in resp['Success']) {
                var auction = resp['Success'][i];
                if (auction[5] != user) { // Don't add a row for this user's auction
                    var row = table.appendChild(document.createElement('tr'));

                    var owner = row.appendChild(document.createElement('td')).appendChild(document.createElement('p'));
                    owner.innerHTML = auction[5];

                    var date = row.appendChild(document.createElement('td'));
                    date.appendChild(document.createElement('p')).innerHTML = formatLongDate(auction[0]);
                    date.appendChild(document.createElement('p')).innerHTML = formatTime(auction[0]);

                    var highestBid = row.appendChild(document.createElement('td')).appendChild(document.createElement('p'));
                    highestBid.innerHTML = formatHTK(auction[1]);
                    if (auction[4] == user) { // This user is the top bidder
                        highestBid.style.color = "#13CE66";
                    }
                    var bidButton = row.appendChild(document.createElement('td')).appendChild(document.createElement('button'));
                    bidButton.setAttribute("class", "actionButton");
                    bidButton.setAttribute("id", "bid" + auction[2]);
                    bidButton.innerHTML = "Add Bid";
                    bidButton.onclick = passArguments(user, auction[2], 'bid', { 'event_name': selectedName, 'highest_bid': auction[1], }); // 'user_balance': resp['user_balance'] });
                }
            }
        }
        if (table.innerHTML == "") {
            // Empty table
            var emptyRow = table.appendChild(document.createElement('tr'));
            emptyRow.appendChild(document.createElement('td')).appendChild(document.createElement('p')).innerHTML = "No auctions available.";
            emptyRow.appendChild(document.createElement('td'));
            emptyRow.appendChild(document.createElement('td'));
            emptyRow.appendChild(document.createElement('td'));
        }
    });
}