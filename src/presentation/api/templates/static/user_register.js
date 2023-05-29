const password = document.getElementById("password");
const confirm_password = document.getElementById("confirm-password");

function validatePassword() {
  if (password.value !== confirm_password.value) {
    confirm_password.setCustomValidity("try enter the password again");
  } else {
    confirm_password.setCustomValidity("");
  }
}

password.onchange = validatePassword;
confirm_password.onkeyup = validatePassword;

const form = document.querySelector('form');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const response = await fetch('/user/register', {
    method: 'POST',
    body: formData,
  });
  if (response.status !== 200) {
    alert('Произошла ошибка при отправке формы. Попробуйте еще раз позже.');
  }
});