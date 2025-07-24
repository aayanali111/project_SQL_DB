// cart.js
window.onload = async () => {
  const token = localStorage.getItem("token");

  const response = await fetch("http://192.168.137.1:5000/cart/show", {
    headers: { Authorization: `Bearer ${token}` }
  });

  const data = await response.json();
  const container = document.getElementById("cartItems");
  container.innerHTML = data.items.map(item =>
    `<p>${item.name} - ${item.quantity} x $${item.price}</p>`
  ).join('');
};