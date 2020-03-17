// Format ticket values into HTK (i.e. 6000 -> "60.00 HTK")
function formatHTK(value) {
    var val = value.toString();
    document.write(val.slice(0, -2) + "." + val.slice(-2) + " HTK");
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

    console.log("month: " + month);
    console.log("day: " + day);
    console.log("year: " + year);

    document.write(months[month - 1] + " " + day + ", " + year);
}

// Opens a modal window for confirming user actions before making request to server
function openWindow(user, id, action) {
    // Get modal
    var modal = document.getElementById("window");
    modal.style.display = "block";

    // Modal content
    var body = modal.querySelector(".modal-body");
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
        text.children[0].innerHTML = "You are purchasing a ticket for " + ".";
    } else if (action == "enter_lottery") {
        title.innerHTML = "Confirm Lottery Entry";
        text.innerHTML = "You are entering the lottery, please confirm.";
    } else if (action == "leave_lottery") {
        title.innerHTML = "Leaving Lottery";
        text.innerHTML = "You are leaving the lottery, please confirm.";
    } else if (action == "sell") {
        title.innerHTML = "Confirm Ticket Sale";
        text.innerHTML = "You are selling a ticket, please confirm."
    }

    var buttonArea = modal.querySelector(".button-area");
    // Find or create Confirm button
    var confirm = buttonArea.querySelector(".confirmButton");
    if (confirm == null) {
        confirm = buttonArea.appendChild(document.createElement("button"));
        confirm.innerHTML = "Confirm";
        confirm.setAttribute("class", "confirmButton");
    }
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
            location.reload();
        }
    }


    // On clicking confirm button, make request to execute action
    confirm.onclick = function(event) {
        // Send necessary information to backend
        var data = {
            action: action,
            user: user,
        };
        // Set up variable information
        if (action == "buy" || action == "enter_lottery" || action == "leave_lottery") {
            data['game_id'] = id;
        } else if (action == "sell") {
            data['ticket_id'] = id;
        }

        // Send the request JSON
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            url: "/requests.pyhtml",
            error: (error) => {
                console.log(error);
                confirm.style.display = "none";
                text.innerHTML = error.responseText;
            },
        }).then((data) => {
            confirm.style.display = "none";

            console.log(data);
            var resp = JSON.parse(data);
            if (resp.hasOwnProperty("error")) { // Action failed
                text.innerHTML = resp.error;
            } else { // Successful execution
                text.innerHTML = "Success!";
            }
        });
    };
}

function closeWindow() {
    var modal = document.getElementById('window');
    modal.style.display = "none";
}

window.onclick = function(event) {
    // If a modal is open and the user clicks outside of it, close the modal
    if (event.target.attributes.class && event.target.attributes.class.value == "modal") {
        event.target.style.display = "none";
    }
}