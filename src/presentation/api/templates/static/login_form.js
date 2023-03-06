// DOM variables

let username = document.getElementById('user')
let password = document.getElementById('pass')
let log_button = document.getElementById('butt')
let auth_form = document.getElementById('auth_form')
let request_model = document.getElementById('rq_model')
let div_elements = document.getElementsByClassName('model_elem')
let base_url = document.getElementById('base_url').innerText

let yesButton = document.getElementById('yes_butt')
let noButton = document.getElementById('no_butt')
let tryAgainButt = document.getElementById('try_again_butt')
let overlay = document.querySelector('#overlay_modal')
let modalWindow = document.querySelector('#modal_window')
let credentialsModalWindow = document.querySelector('#credentials_modal_window')



// external services variables

let deviceButtons = document.getElementsByClassName('device_button')
let deviceButtonsArray = [...deviceButtons]


function formRequestModel(){
    let model = {}
    for (let i=0; i < div_elements.length; ++i) {
        model[div_elements[i].id] = div_elements[i].innerHTML
    }

    return model
}

function updateScope() {
    let user_name = username.value
    let user_password = password.value
    return "&username="+user_name+"&password="+user_password
}

function formBody(){
    let bodyData = new URLSearchParams()
    let scope_update = updateScope()
    let details = formRequestModel()
    if (details.scope == "None") {
        details.scope = scope_update.slice(1,)
    } else {
        details.scope += scope_update
    }
    for (let property in details) {
        if (details[property] == "None") {
            bodyData.append(property, '')
        } else {
            bodyData.append(property, details[property])
        }
      }

    return bodyData
}


async function redirect(data){
    await fetch(`http://${base_url}/authorize/`, {
        method: "POST",
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: data
    }).then ((response) => {
        if (!response.ok) {
            throw new Error("Wrong credentials")
        } else {
            let new_location = response.url
            window.location = new_location
        }
    }).catch((err) => {
        if (data.get("response_type") == "urn:ietf:params:oauth:grant-type:device_code") {
            credentialsModalWindow.classList.add('active');
            overlay.classList.add('active');
            tryAgainButt.addEventListener("click", async () => {
                credentialsModalWindow.classList.remove('active');
                overlay.classList.remove('active');
                window.location.reload()
            })
        }
        console.log(err)
    })
}
async function clearDeviceData(data){
    response = await fetch(`http://${base_url}/device/auth/cancel`, {
        method: "DELETE",
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: data
    })
    let new_location = response.url
    window.location = new_location
}

async function redirectToPost(event) {
    event.preventDefault();
    let data = formBody();

    if (data.get("response_type") == "urn:ietf:params:oauth:grant-type:device_code") {
        modalWindow.classList.add('active');
        overlay.classList.add('active');
        yesButton.addEventListener("click", async () => {
            modalWindow.classList.remove('active');
            overlay.classList.remove('active');
            return await redirect(data)
        })
        noButton.addEventListener("click", async () => {
            modalWindow.classList.remove('active');
            overlay.classList.remove('active');
            return await clearDeviceData(data)
        })

    } else {
        return await redirect(data)
    }
}

function parseLink(link){
    arr_data = link.split("&")
    console.log(arr_data)
    let bodyData = new URLSearchParams()
    data = {}
    arr_data.forEach(function(item, index, array){
        console.log(item)

        small_arr = item.split("=")
        data[small_arr[0]] = small_arr[1]
    })
    bodyData.append("state", data["state"])
    return bodyData
}


// External service functions

deviceButtonsArray.forEach((item) => {
    item.addEventListener('click', async function() {
        let device_link = item.name
        state = parseLink(device_link)
        await fetch(`http://${base_url}/authorize/oidc/state`, {
            method: "POST",
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: state
        })
        window.location.href = device_link;
    })
})

function handleDeviceButton(butt){
    let device_link = butt.name
    window.location.href = device_link;
}


// EventListeners

auth_form.addEventListener('submit', redirectToPost)
