const password = document.getElementById("password");
const confirm_password = document.getElementById("confirm-password");

function validatePassword() {
  if (password.value !== confirm_password.value) {
    confirm_password.setCustomValidity("Пароли не совпадают");
  } else {
    confirm_password.setCustomValidity("");
  }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;