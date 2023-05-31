// DOM variables

let username = document.getElementById('user');
let password = document.getElementById('pass');
let log_button = document.getElementById('butt');
let auth_form = document.getElementById('auth_form');
let request_model = document.getElementById('rq_model');
let div_elements = document.getElementsByClassName('model_elem');
let base_url = document.getElementById('base_url').innerText;

let yesButton = document.getElementById('yes_butt');
let noButton = document.getElementById('no_butt');
let tryAgainButt = document.getElementById('try_again_butt');
let overlay = document.querySelector('#overlay_modal');
let modalWindow = document.querySelector('#modal_window');
let credentialsModalWindow = document.querySelector(
    '#credentials_modal_window'
);

// external services variables

let deviceButtons = document.getElementsByClassName('device_button');
let deviceButtonsArray = [...deviceButtons];

localStorage.removeItem('oidc_auth');
localStorage.setItem('oidc_auth', window.location.href);

function formRequestModel() {
    let model = {};
    for (let i = 0; i < div_elements.length; ++i) {
        model[div_elements[i].id] = div_elements[i].innerHTML;
    }

    return model;
}

function formBody() {
    let bodyData = new URLSearchParams();
    let details = formRequestModel();

    // Add the username and password as separate fields
    bodyData.append('username', username.value);
    bodyData.append('password', password.value);

    // Iterate through the request model and append fields to bodyData
    for (let property in details) {
        if (details[property] == 'None') {
            bodyData.append(property, '');
        } else {
            bodyData.append(property, details[property]);
        }
    }

    return bodyData;
}

async function redirect(data) {
    await fetch(`http://${base_url}/authorize/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: data,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Wrong credentials');
            } else {
                return response.json();
            }
        })
        .then((data) => {
            showConfirmationModal(text = data.some_text, redirect_url = data.redirect_url);
        })
        .catch((err) => {
            if (
                data.get('response_type') ==
                'urn:ietf:params:oauth:grant-type:device_code'
            ) {
                credentialsModalWindow.classList.add('active');
                overlay.classList.add('active');
                tryAgainButt.addEventListener('click', async () => {
                    credentialsModalWindow.classList.remove('active');
                    overlay.classList.remove('active');
                    window.location.reload();
                });
            }
            console.log(err);
        });
}
async function clearDeviceData(data) {
    response = await fetch(`http://${base_url}/device/auth/cancel`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: data,
    });
    let new_location = response.url;
    window.location = new_location;
}

async function redirectToPost(event) {
    event.preventDefault();
    let data = formBody();

    if (
        data.get('response_type') ==
        'urn:ietf:params:oauth:grant-type:device_code'
    ) {
        modalWindow.classList.add('active');
        overlay.classList.add('active');
        yesButton.addEventListener('click', async () => {
            modalWindow.classList.remove('active');
            overlay.classList.remove('active');
            return await redirect(data);
        });
        noButton.addEventListener('click', async () => {
            modalWindow.classList.remove('active');
            overlay.classList.remove('active');
            return await clearDeviceData(data);
        });
    } else {
        return await redirect(data);
    }
}

function parseLink(link) {
    arr_data = link.split('&');
    console.log(arr_data);
    let bodyData = new URLSearchParams();
    data = {};
    arr_data.forEach(function (item, index, array) {
        console.log(item);

        small_arr = item.split('=');
        data[small_arr[0]] = small_arr[1];
    });
    bodyData.append('state', data['state']);
    return bodyData;
}

// External service functions

deviceButtonsArray.forEach((item) => {
    item.addEventListener('click', async function () {
        let device_link = item.name;
        state = parseLink(device_link);
        await fetch(`http://${base_url}/authorize/oidc/state`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: state,
        });
        window.location.href = device_link;
    });
});

function handleDeviceButton(butt) {
    let device_link = butt.name;
    window.location.href = device_link;
}

function showConfirmationModal(text, redirect_url) {
    let confirmationText = document.querySelector('#modal_window .form_auth_block_head_text');
    let modalOverlay = document.querySelector('#overlay_modal');
    let modalWindow = document.querySelector('#modal_window');
    let submitButton = document.querySelector('#yes_butt');
    let declineButton = document.querySelector('#no_butt');
  
    let modalTitle = document.createElement("p");
    modalTitle.classList.add("modal_title");
    modalTitle.textContent = "The service wants to get access to:";
    modalTitle.style.fontFamily = "Arial, sans-serif";
    modalTitle.style.textAlign = "left";
    modalTitle.style.fontWeight = "bold";
    confirmationText.parentNode.insertBefore(modalTitle, confirmationText);

    confirmationText.innerText = text;
    confirmationText.style.textAlign = "left";
  
    modalOverlay.classList.add('active');
    modalWindow.classList.add('active');
    
    submitButton.addEventListener('click', async () => {
      modalOverlay.classList.remove('active');
      modalWindow.classList.remove('active');
      console.log(redirect_url);
      console.log(text);
      window.location.href = redirect_url;
    });
    
    declineButton.addEventListener('click', async () => {
      modalOverlay.classList.remove('active');
      modalWindow.classList.remove('active');
      let updated_url = redirect_url.replace(/code=.*$/, "code=user_refused_to_give_permission");
      window.location.href = updated_url;
    });
  }

// EventListeners

auth_form.addEventListener('submit', redirectToPost);
