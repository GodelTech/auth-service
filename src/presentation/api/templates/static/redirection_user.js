const access_token = localStorage.getItem('access_token_godel_oidc');

if (access_token) {
  fetch(`/user/${getSubFromToken(access_token)}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${access_token}`
    }
  })
  .then(response => {
    if (response.ok) {
      return response.text();
    } else {
      throw new Error('Failed to fetch user data');
    }
  })
  .then(html => {
    document.body.innerHTML = html;
  })
  .catch(error => {
    console.error(error);
    window.location.href = '/user/login';
  });
} else {
  window.location.href = '/user/login';
}

function getEmailFromToken(token) {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace('-', '+').replace('_', '/');
  return JSON.parse(atob(base64)).email;
}

function getSubFromToken(token) {
    const tokenParts = token.split('.');
    const payload = JSON.parse(atob(tokenParts[1]));
    return payload.sub;
  }