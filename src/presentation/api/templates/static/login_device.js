// DOM variables

let userCode = document.getElementById('user_code')
let deviceLogButton = document.getElementById('device_butt')
let deviceAuthForm = document.getElementById('device_auth_form')

// Functions

function formBody(){
    code = userCode.value
    details = {
        "user_code": code
    }
    let bodyData = new URLSearchParams()
    for (let property in details) {
        if (details[property] == "None") {
            bodyData.append(property, '')
        } else {
            bodyData.append(property, details[property])
        }
      }

    return bodyData
}

async function redirectToDevicePost(event) {
    event.preventDefault();
    let data = formBody()
    console.log(data)
    resp = await fetch("http://127.0.0.1:8000/device/auth", {
        method: "POST",
        headers: headers={'Content-Type': 'application/x-www-form-urlencoded'},
        body: data
    })
    let new_location = resp.url
    window.location = new_location
}

// EventListeners

deviceAuthForm.addEventListener('submit', redirectToDevicePost)
