document.querySelectorAll('.toggle-password').forEach(icon => {
    icon.addEventListener('click', () => {
      const input = document.getElementById(icon.dataset.target);
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('bi-eye-slash-fill', 'bi-eye-fill');
      } else {
        input.type = 'password';
        icon.classList.replace('bi-eye-fill', 'bi-eye-slash-fill');
      }
    });
  });

function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}

document.addEventListener("DOMContentLoaded", () => {
  // 🛒 Update Cart (increase/decrease buttons)
  document.querySelectorAll(".cart-form").forEach(form => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const url = form.action;
      const formData = new FormData(form);

      try {
        const response = await fetch(url, {
          method: "POST",
          body: formData,
          credentials: "same-origin",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
          },
        });

        const data = await response.json();

        // ✅ Update quantity
        const quantityEl = document.querySelector(
          `.quantity[data-item-id="${data.item_id}"]`
        );
        if (quantityEl) {
          quantityEl.textContent = data.quantity;
        }

        // ✅ Update per-item total
        const itemTotalEl = document.querySelector(
          `.item-total[data-item-id="${data.item_id}"]`
        );
        if (itemTotalEl) {
          itemTotalEl.textContent = `Rs. ${data.item_total}`;
        }

        // ✅ Update summary totals
        document.getElementById("subtotal").textContent = `Rs. ${data.subtotal}`;
        document.getElementById("tax").textContent = `Rs. ${data.tax}`;
        document.getElementById("shipping").textContent = `Rs. ${data.shipping}`;
        document.getElementById("total").textContent = `Rs. ${data.total}`;

      } catch (error) {
        console.error("Error updating cart:", error);
      }
    });
  });

  // 🛒 Add to Cart (product listing buttons)
  document.querySelectorAll(".add-to-cart-btn").forEach(btn => {
    btn.addEventListener("click", async (event) => {
      event.preventDefault(); // stop page reload

      const url = btn.getAttribute("href");

      try {
        const response = await fetch(url, {
          method: "GET", // your add_to_cart view is GET
          credentials: "same-origin",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        });

        const data = await response.json();

        if (data.success) {
          // ✅ Update navbar cart count
          const cartCountEl = document.getElementById("cart-count");
          if (cartCountEl) {
            cartCountEl.textContent = data.cart_count;
          }

          // Optional: small toast/log
          console.log(`${data.product_name} added to cart!`);

        } else if (data.error === "login_required") {
          alert("Please log in to add items to your cart.");
        }

      } catch (error) {
        console.error("Error adding to cart:", error);
      }
    });
  });
});

  // 🗑 Remove from Cart
  document.querySelectorAll(".remove-cart-btn").forEach(btn => {
    btn.addEventListener("click", async (event) => {
      event.preventDefault();

      const url = btn.getAttribute("href");
      const itemId = btn.dataset.itemId;

      try {
        const response = await fetch(url, {
          method: "GET",
          credentials: "same-origin",
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        });

        const data = await response.json();

        if (data.success) {
          // ✅ Remove row from DOM
          const row = btn.closest(".row");
          if (row) row.remove();

          // ✅ Update summary totals
          document.getElementById("subtotal").textContent = `Rs. ${data.subtotal}`;
          document.getElementById("tax").textContent = `Rs. ${data.tax}`;
          document.getElementById("shipping").textContent = `Rs. ${data.shipping}`;
          document.getElementById("total").textContent = `Rs. ${data.total}`;

          // ✅ Update navbar cart count
          const cartCountEl = document.getElementById("cart-count");
          if (cartCountEl) {
            cartCountEl.textContent = data.cart_count;
          }

          // Optional: if cart empty, show empty message
          if (data.cart_count === 0) {
            const container = document.querySelector(".container");
            if (container) {
              container.innerHTML = `<p class="text-muted fw-bold text-center">🛒 Your cart is empty.</p>`;
            }
          }
        }
      } catch (error) {
        console.error("Error removing item:", error);
      }
    });
  });
