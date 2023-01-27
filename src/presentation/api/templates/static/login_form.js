let username = document.getElementById('user')
let password = document.getElementById('pass')
let log_button = document.getElementById('butt')
let auth_form = document.getElementById('auth_form')
let request_model = document.getElementById('rq_model')
let div_elements = document.getElementsByClassName('model_elem')


function formRequestModel(){
    let model = {}
    for (i=0; i < div_elements.length; ++i) {
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

async function redirectToPost(event) {
    event.preventDefault();
    let data = formBody()

    return await fetch("http://127.0.0.1:8000/authorize/", {
        method: "POST",
        headers: headers={'Content-Type': 'application/x-www-form-urlencoded'},
        body: data
    })
}

auth_form.addEventListener('submit', redirectToPost)
