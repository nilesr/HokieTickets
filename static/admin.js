// Opens a modal window for confirming user actions before making request to server
function openWindow(id, action) {
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
    if (action == "execute_lottery") {
        title.innerHTML = "Confirm Execute Lottery";
        text.children[0].innerHTML = "You are executing the lottery for Game " + id;
    } else if (action == "open_lottery") {
        title.innerHTML = "Confirm Open Lottery";
        text.children[0].innerHTML = "You are opening the lottery for Game " + id;
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
            admin: true,
            action: action,
            game_id: id,
        };

        // Send the request JSON
        $.ajax({
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(data),
            url: "/requests.pyhtml",
            error: (error) => {
                console.log(error);
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
    location.reload();
}

window.onclick = function(event) {
    // If a modal is open and the user clicks outside of it, close the modal
    if (event.target.attributes.class && event.target.attributes.class.value == "modal") {
        event.target.style.display = "none";
        location.reload();
    }
}

function selectedUserBalance() {
    var userSelect = document.getElementById("userSelect");
    return userSelect.options[userSelect.selectedIndex].value;
}