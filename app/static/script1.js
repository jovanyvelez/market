// Estado del carrito
let cart = [];

// Cargar el carrito desde localStorage al iniciar
function loadCart() {
    const savedCart = localStorage.getItem('shoppingCart');
    if (savedCart) {
        cart = JSON.parse(savedCart);
        updateCartDisplay();
    }
}

// Guardar el carrito en localStorage
function saveCart() {
    localStorage.setItem('shoppingCart', JSON.stringify(cart));
}

// Actualizar el contador del carrito
function updateCartCount() {
    const countElement = document.getElementById('cart-count');
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    countElement.textContent = totalItems;
}

// Añadir producto al carrito
function addToCart(id, name, price) {
    const existingItem = cart.find(item => item.id === id);

    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({
            id,
            name,
            price,
            quantity: 1
        });
    }

    saveCart();
    updateCartDisplay();
    showNotification('Producto añadido al carrito');
}

// Eliminar producto del carrito
function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    saveCart();
    updateCartDisplay();
    showNotification('Producto eliminado del carrito');
}

// Actualizar la visualización del carrito
function updateCartDisplay() {
    const cartItems = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');

    updateCartCount();

    if (cart.length === 0) {
        cartItems.innerHTML = '<div class="empty-cart">Tu carrito está vacío</div>';
        cartTotal.textContent = '0.00';
        return;
    }

    let itemsHTML = '';
    let total = 0;

    cart.forEach(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;

        itemsHTML += `
                    <div class="cart-item">
                        <div>
                            <strong>${item.name}</strong> - $${item.price.toFixed(2)} x ${item.quantity}
                        </div>
                        <button class="remove-btn" onclick="removeFromCart(${item.id})">Eliminar</button>
                    </div>
                `;
    });

    cartItems.innerHTML = itemsHTML;
    cartTotal.textContent = total.toFixed(2);
}

// Finalizar compra
function checkout() {
    if (cart.length === 0) {
        alert('Tu carrito está vacío');
        return;
    }

    alert('¡Compra realizada con éxito! Total: $' +
        cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2));

    // Vaciar carrito después de la compra
    cart = [];
    saveCart();
    updateCartDisplay();
}

// Mostrar notificación
function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 2000);
}

// Navegación entre páginas
function showPage(pageId) {
    // Ocultar todas las páginas
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Mostrar la página seleccionada
    document.getElementById(pageId).classList.add('active');
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadCart();
    /*showPage('home'); veremos luego si usamos esta línea*/
});