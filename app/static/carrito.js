// Estado del carrito
let cart = [];

// Objeto para mantener las cantidades de cada producto
let quantities = {};

// Cargar el carrito desde localStorage al iniciar
function loadCart() {
    const savedCart = localStorage.getItem('shoppingCart');
    if (savedCart) {
        cart = JSON.parse(savedCart);
        // Actualizar la interfaz basada en el carrito guardado
        updateProductsInterface();
    }
}

// Actualizar la interfaz de todos los productos basado en el carrito
function updateProductsInterface() {
    console.log('Updating products interface. Cart items:', cart.length);
    
    if (cart.length === 0) {
        console.log('Cart is empty, no interface updates needed');
        return;
    }
    
    cart.forEach(item => {
        const productExists = document.getElementById(`addButton_${item.id}`);
        console.log(`Checking product ${item.id}:`, productExists ? 'Found' : 'Not found on page');
        
        if (productExists) {
            console.log(`Syncing product ${item.id} with quantity ${item.quantity}`);
            // Si el producto está en el carrito, mostrar el selector de cantidad
            showQuantitySelector(item.id);
            // Actualizar la cantidad mostrada con la cantidad del carrito
            quantities[item.id] = item.quantity;
            updateQuantityDisplay(item.id);
        }
    });
    
    console.log('Interface update completed');
}

// Función para sincronizar un producto específico con el carrito
function syncProductWithCart(productId) {
    const cartItem = cart.find(item => item.id === productId);
    if (cartItem) {
        // Si está en el carrito, mostrar selector y sincronizar cantidad
        showQuantitySelector(productId);
        quantities[productId] = cartItem.quantity;
        updateQuantityDisplay(productId);
    } else {
        // Si no está en el carrito, mostrar botón comprar
        hideQuantitySelector(productId);
    }
}

// Función de debugging para mostrar el estado del carrito
function debugCartState() {
    console.log('=== CART DEBUG INFO ===');
    console.log('Cart items:', cart);
    console.log('Quantities object:', quantities);
    console.log('Products found on page:');
    
    document.querySelectorAll('[id^="addButton_"]').forEach(button => {
        const productId = parseInt(button.id.split('_')[1]);
        const isInCart = cart.find(item => item.id === productId);
        console.log(`Product ${productId}: ${isInCart ? 'IN CART' : 'NOT IN CART'}`);
    });
    
    console.log('=== END DEBUG INFO ===');
}

// Guardar el carrito en localStorage
function saveCart() {
    localStorage.setItem('shoppingCart', JSON.stringify(cart));
}

// Actualizar el contador del carrito
function updateCartCount() {
    const countElement = document.getElementById('cart-count');
    if (countElement) {
        const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
        countElement.textContent = totalItems;
    }
}

// Función mejorada para añadir al carrito
function addToCart(id, name, price) {
    // Inicializar cantidad si no existe
    if (!quantities[id]) {
        quantities[id] = 1;
    }

    const existingItem = cart.find(item => item.id === id);

    if (existingItem) {
        existingItem.quantity += quantities[id];
    } else {
        cart.push({
            id,
            name,
            price,
            quantity: quantities[id]
        });
    }

    saveCart();
    updateCartCount();
    
    // Mostrar el selector de cantidad
    showQuantitySelector(id);
    
    // Sincronizar la cantidad mostrada con la del carrito
    const cartItem = cart.find(item => item.id === id);
    if (cartItem) {
        quantities[id] = cartItem.quantity;
        updateQuantityDisplay(id);
    }
    
    // Mostrar notificación
    showNotification(`${name} añadido al carrito`);
}

// Mostrar el selector de cantidad para un producto específico
function showQuantitySelector(productId) {
    const addButton = document.getElementById(`addButton_${productId}`);
    const quantitySelector = document.getElementById(`quantitySelector_${productId}`);
    
    console.log(`Showing quantity selector for product ${productId}`);
    console.log('AddButton:', addButton ? 'Found' : 'Not found');
    console.log('QuantitySelector:', quantitySelector ? 'Found' : 'Not found');
    
    if (addButton && quantitySelector) {
        addButton.classList.add('hidden');
        quantitySelector.classList.remove('hidden');
        console.log(`Successfully showed quantity selector for product ${productId}`);
    } else {
        console.log(`Failed to show quantity selector for product ${productId}`);
    }
}

// Ocultar el selector de cantidad para un producto específico
function hideQuantitySelector(productId) {
    const addButton = document.getElementById(`addButton_${productId}`);
    const quantitySelector = document.getElementById(`quantitySelector_${productId}`);
    
    console.log(`Hiding quantity selector for product ${productId}`);
    
    if (addButton && quantitySelector) {
        addButton.classList.remove('hidden');
        quantitySelector.classList.add('hidden');
        // Resetear cantidad
        quantities[productId] = 1;
        updateQuantityDisplay(productId);
        console.log(`Successfully hid quantity selector for product ${productId}`);
    } else {
        console.log(`Failed to hide quantity selector for product ${productId}`);
    }
}

// Incrementar cantidad para un producto específico
function increaseQuantity(productId) {
    if (!quantities[productId]) {
        quantities[productId] = 1;
    }
    quantities[productId]++;
    updateQuantityDisplay(productId);
    
    // Actualizar cantidad en el carrito
    const cartItem = cart.find(item => item.id === productId);
    if (cartItem) {
        cartItem.quantity = quantities[productId];
        saveCart();
        updateCartCount();
    }
}

// Decrementar cantidad para un producto específico
function decreaseQuantity(productId) {
    if (!quantities[productId]) {
        quantities[productId] = 1;
    }
    
    if (quantities[productId] > 1) {
        quantities[productId]--;
        updateQuantityDisplay(productId);
        
        // Actualizar cantidad en el carrito
        const cartItem = cart.find(item => item.id === productId);
        if (cartItem) {
            cartItem.quantity = quantities[productId];
            saveCart();
            updateCartCount();
        }
    } else {
        // Si la cantidad es 1, remover del carrito y ocultar el selector
        removeFromCart(productId);
        hideQuantitySelector(productId);
    }
}

// Actualizar la visualización de cantidad para un producto específico
function updateQuantityDisplay(productId) {
    const quantityDisplay = document.getElementById(`quantityDisplay_${productId}`);
    if (quantityDisplay && quantities[productId]) {
        quantityDisplay.textContent = quantities[productId];
    }
}

// Eliminar producto del carrito
function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    saveCart();
    updateCartDisplay();
    updateCartCount();
    
    // Actualizar la interfaz del producto en la página
    const productExists = document.getElementById(`addButton_${id}`);
    if (productExists) {
        hideQuantitySelector(id);
    }
    
    showNotification('Producto eliminado del carrito');
}

// Actualizar la visualización del carrito
function updateCartDisplay() {
    const cartItems = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');

    updateCartCount();

    if (!cartItems || !cartTotal) return;

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
    quantities = {};
    saveCart();
    updateCartDisplay();
    updateCartCount();
    
    // Resetear todos los selectores de cantidad
    document.querySelectorAll('.quantity-selector').forEach(selector => {
        selector.classList.add('hidden');
    });
    document.querySelectorAll('.add-button').forEach(button => {
        button.classList.remove('hidden');
    });
    
    // Reinicializar cantidades
    document.querySelectorAll('[id^="quantityDisplay_"]').forEach(display => {
        const productId = parseInt(display.id.split('_')[1]);
        quantities[productId] = 1;
        updateQuantityDisplay(productId);
    });
}

// Mostrar notificación
function showNotification(message) {
    const notification = document.getElementById('notification');
    if (notification) {
        notification.textContent = message;
        notification.classList.add('show');

        setTimeout(() => {
            notification.classList.remove('show');
        }, 2000);
    }
}

// Navegación entre páginas
function showPage(pageId) {
    // Ocultar todas las páginas
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Mostrar la página seleccionada
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadCart();
    updateCartCount();
    
    // Inicializar todas las cantidades en 1 para productos que no están en el carrito
    initializeProductQuantities();

    // Event delegation para botones de agregar al carrito
    setupEventListeners();
});

// Función para inicializar las cantidades de productos
function initializeProductQuantities() {
    document.querySelectorAll('[id^="quantityDisplay_"]').forEach(display => {
        const productId = parseInt(display.id.split('_')[1]);
        if (!quantities[productId]) {
            quantities[productId] = 1;
            updateQuantityDisplay(productId);
        }
    });
}

// Función para configurar los event listeners
function setupEventListeners() {
    // Event delegation para botones de agregar al carrito
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('add-button')) {
            const productId = parseInt(e.target.dataset.productId);
            const productName = e.target.dataset.productName;
            const productPrice = parseFloat(e.target.dataset.productPrice);
            addToCart(productId, productName, productPrice);
        }
        
        if (e.target.classList.contains('increase-btn')) {
            const productId = parseInt(e.target.dataset.productId);
            increaseQuantity(productId);
        }
        
        if (e.target.classList.contains('decrease-btn')) {
            const productId = parseInt(e.target.dataset.productId);
            decreaseQuantity(productId);
        }
    });
}

// Listener para cuando HTMX carga contenido nuevo
document.addEventListener('htmx:afterSwap', (event) => {
    console.log('HTMX content loaded, syncing cart with interface...');
    
    // Debug del estado actual
    debugCartState();
    
    // Esperar un poco para que el DOM se actualice completamente
    setTimeout(() => {
        // Inicializar cantidades para los nuevos productos
        initializeProductQuantities();
        
        // Sincronizar con el carrito guardado
        updateProductsInterface();
        
        console.log('Cart sync completed');
        debugCartState();
    }, 100);
});

// También escuchar el evento afterSettle por si acaso
document.addEventListener('htmx:afterSettle', (event) => {
    console.log('HTMX settled, ensuring cart sync...');
    // Doble verificación de sincronización
    setTimeout(() => {
        updateProductsInterface();
    }, 50);
});