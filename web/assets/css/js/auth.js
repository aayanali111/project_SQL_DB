// auth.js
document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const response = await fetch("http://192.168.137.1:5000/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await response.json();
  if (data.token) {
    localStorage.setItem("token", data.token);
    alert("Login successful");
    window.location.href = "dashboard.html";
  } else {
    alert("Login failed: " + data.message);
  }
});
