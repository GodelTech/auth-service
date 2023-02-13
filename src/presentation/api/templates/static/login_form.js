// DOM variables

let username = document.getElementById('user')
let password = document.getElementById('pass')
let log_button = document.getElementById('butt')
let auth_form = document.getElementById('auth_form')
let request_model = document.getElementById('rq_model')
let div_elements = document.getElementsByClassName('model_elem')

let yesButton = document.getElementById('yes_butt')
let noButton = document.getElementById('no_butt')
let tryAgainButt = document.getElementById('try_again_butt')
let overlay = document.querySelector('#overlay_modal')
let modalWindow = document.querySelector('#modal_window')
let credentialsModalWindow = document.querySelector('#credentials_modal_window')



// external services variables

let google = document.getElementById('Google')
let github = document.getElementById('GitHub')
let facebook = document.getElementById('FaceBook')
let linkedin = document.getElementById('LinkedIn')
let twitter = document.getElementById('Twitter')


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

// async function redirect(data){
//     return await fetch("http://127.0.0.1:8000/authorize/", {
//         method: "POST",
//         headers: {'Content-Type': 'application/x-www-form-urlencoded'},
//         body: data
//     })
// }

async function redirect(data){
    await fetch("http://127.0.0.1:8000/authorize/", {
        method: "POST",
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: data
    }).then ((response) => {
        if (!response.ok) {
            throw new Error("Wrong credentials")
        } else {
            let new_location = response.url
            // window.location = "http://127.0.0.1:8000/device/auth/success"
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
    await fetch("http://127.0.0.1:8000/device/auth/cancel", {
        method: "POST",
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: data
    })
    window.location = "http://127.0.0.1:8000/device/auth/cancel"

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

// External service functions

function handleGitHub(){
    window.location.href = 'https://github.com/';
}

function handleGoogle(){
    window.location.href = 'https://www.google.com/';
}

function handleFacebook(){
    window.location.href = 'https://www.facebook.com/';
}

function handleLinkedIn(){
    window.location.href = 'https://www.linkedin.com/';
}

function handleTwitter(){
    window.location.href = 'https://twitter.com/';
}

// EventListeners

auth_form.addEventListener('submit', redirectToPost)

github.addEventListener('click', handleGitHub)
google.addEventListener('click', handleGoogle)
facebook.addEventListener('click', handleFacebook)
linkedin.addEventListener('click', handleLinkedIn)
twitter.addEventListener('click', handleTwitter)
