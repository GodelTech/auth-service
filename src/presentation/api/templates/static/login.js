const form = document.querySelector('form');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(form);
  const email = formData.get('email');
  const password = formData.get('password');

  const response = await fetch('login', {
    method: 'POST',
    body: new URLSearchParams({
      'email': email,
      'password': password
    }),
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });

  if (response.ok) {
    const { access_token } = await response.json();
    localStorage.setItem('access_token_godel_oidc', access_token);
    window.location.href = "/user/";
  } else {
    console.log('Login failed');
  }
});
