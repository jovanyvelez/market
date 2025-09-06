// Estado del carrito
let cart = [];

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
        // Buscar tanto en cards normales como en modal de detalle
        const productExists = document.getElementById(`addButton_${item.id}`) || 
                            document.getElementById(`addButton_detalle_${item.id}`);
        console.log(`Checking product ${item.id}:`, productExists ? 'Found' : 'Not found on page');
        
        if (productExists) {
            console.log(`Syncing product ${item.id} with quantity ${item.quantity}`);
            // Si el producto está en el carrito, mostrar el selector de cantidad
            showQuantitySelector(item.id);
            // También sincronizar el modal de detalle si existe
            showQuantitySelector(item.id, 'detalle_');
            // Actualizar la cantidad mostrada con la cantidad del carrito
            updateQuantityDisplay(item.id);
        }
    });
    
    console.log('Interface update completed');
}

// Función para sincronizar un producto específico con el carrito
function syncProductWithCart(productId) {
    const cartItem = cart.find(item => item.id === productId);
    if (cartItem) {
        // Si está en el carrito, mostrar selector y sincronizar cantidad en cards normales
        showQuantitySelector(productId);
        updateQuantityDisplay(productId);
        
        // También sincronizar en modal de detalle si existe
        showQuantitySelector(productId, 'detalle_');
        updateQuantityDisplay(productId, 'detalle_');
    } else {
        // Si no está en el carrito, mostrar botón comprar en ambos lugares
        hideQuantitySelector(productId);
        hideQuantitySelector(productId, 'detalle_');
    }
}

// Función de debugging para mostrar el estado del carrito
function debugCartState() {
    console.log('=== CART DEBUG INFO ===');
    console.log('Cart items:', cart);
    console.log('Cart length:', cart.length);
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
        countElement.textContent = cart.length;
    }
}

// Función mejorada para añadir al carrito
function addToCart(id, name, price, imageUrl = null) {
    const existingItem = cart.find(item => item.id === id);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id,
            name,
            price,
            quantity: 1,
            imageUrl: imageUrl && imageUrl.trim() !== '' ? imageUrl : null
        });
    }

    saveCart();
    updateCartCount();
    
    // Mostrar el selector de cantidad
    showQuantitySelector(id);
    
    // Sincronizar la cantidad mostrada con la del carrito
    updateQuantityDisplay(id);
    
    // Mostrar notificación
    showNotification(`${name} añadido al carrito`);
}

// Mostrar el selector de cantidad para un producto específico
function showQuantitySelector(productId, prefix = '') {
    const addButton = document.getElementById(`addButton_${prefix}${productId}`);
    const quantitySelector = document.getElementById(`quantitySelector_${prefix}${productId}`);
    
    console.log(`Showing quantity selector for product ${productId} with prefix '${prefix}'`);
    console.log('AddButton:', addButton ? 'Found' : 'Not found');
    console.log('QuantitySelector:', quantitySelector ? 'Found' : 'Not found');
    
    if (addButton && quantitySelector) {
        addButton.classList.add('hidden');
        quantitySelector.classList.remove('hidden');
        console.log(`Successfully showed quantity selector for product ${productId} with prefix '${prefix}'`);
    } else {
        console.log(`Failed to show quantity selector for product ${productId} with prefix '${prefix}'`);
    }
}

// Ocultar el selector de cantidad para un producto específico
function hideQuantitySelector(productId, prefix = '') {
    const addButton = document.getElementById(`addButton_${prefix}${productId}`);
    const quantitySelector = document.getElementById(`quantitySelector_${prefix}${productId}`);
    
    console.log(`Hiding quantity selector for product ${productId} with prefix '${prefix}'`);
    
    if (addButton && quantitySelector) {
        addButton.classList.remove('hidden');
        quantitySelector.classList.add('hidden');
        // Resetear el display de cantidad a 1
        updateQuantityDisplay(productId, prefix);
        console.log(`Successfully hid quantity selector for product ${productId} with prefix '${prefix}'`);
    } else {
        console.log(`Failed to hide quantity selector for product ${productId} with prefix '${prefix}'`);
    }
}

// Incrementar cantidad para un producto específico
function increaseQuantity(productId) {
    const cartItem = cart.find(item => item.id === productId);
    if (cartItem) {
        cartItem.quantity++;
        saveCart();
        updateCartCount();
        // Actualizar ambas interfaces
        updateQuantityDisplay(productId);
        updateQuantityDisplay(productId, 'detalle_');
    }
}

// Decrementar cantidad para un producto específico
function decreaseQuantity(productId) {
    const cartItem = cart.find(item => item.id === productId);
    if (cartItem) {
        if (cartItem.quantity > 1) {
            cartItem.quantity--;
            saveCart();
            updateCartCount();
            // Actualizar ambas interfaces
            updateQuantityDisplay(productId);
            updateQuantityDisplay(productId, 'detalle_');
        } else {
            // Si la cantidad es 1, remover del carrito y ocultar el selector
            removeFromCart(productId);
            hideQuantitySelector(productId);
            hideQuantitySelector(productId, 'detalle_');
        }
    }
}

// Actualizar la visualización de cantidad para un producto específico
function updateQuantityDisplay(productId, prefix = '') {
    const quantityDisplay = document.getElementById(`quantityDisplay_${prefix}${productId}`);
    const cartItem = cart.find(item => item.id === productId);
    if (quantityDisplay && cartItem) {
        quantityDisplay.textContent = cartItem.quantity;
    } else if (quantityDisplay) {
        quantityDisplay.textContent = '1';
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
                <div class="cart-item-image">
                    ${item.imageUrl && item.imageUrl.trim() !== '' ? 
                        `<img src="${item.imageUrl}" alt="${item.name}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                         <div class="default-image" style="display: none;">📦</div>` :
                        `<div class="default-image">📦</div>`
                    }
                </div>
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-details">$${item.price.toFixed(2)} c/u</div>
                </div>
                <div class="cart-item-controls">
                    <div class="quantity-controls">
                        <button class="quantity-btn decrease-btn" data-product-id="${item.id}">-</button>
                        <span class="quantity-display" id="quantityDisplay_${item.id}">${item.quantity}</span>
                        <button class="quantity-btn increase-btn" data-product-id="${item.id}">+</button>
                    </div>
                    <button class="remove-btn" onclick="removeFromCart(${item.id})">Eliminar</button>
                </div>
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
    updateCartCount();
    
    // Resetear todos los selectores de cantidad
    document.querySelectorAll('.quantity-selector').forEach(selector => {
        selector.classList.add('hidden');
    });
    document.querySelectorAll('.add-button').forEach(button => {
        button.classList.remove('hidden');
    });
    
    // Reinicializar displays de cantidad
    document.querySelectorAll('[id^="quantityDisplay_"]').forEach(display => {
        display.textContent = '1';
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

// Función para enviar el carrito al backend
function sendCartToBackend() {
    if (!cart || cart.length === 0) {
        // Si el carrito está vacío, usar GET
        fetch('/api/v2/categorias/carrito')
        .then(response => response.text())
        .then(html => {
            document.getElementById('reemplazar').innerHTML = html;
        })
        .catch(error => {
            console.error('Error cargando carrito vacío:', error);
        });
        return;
    }
    
    // Enviar datos del carrito al backend via POST
    fetch('/api/v2/categorias/carrito', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            items: cart
        })
    })
    .then(response => response.text())
    .then(html => {
        document.getElementById('reemplazar').innerHTML = html;
    })
    .catch(error => {
        console.error('Error enviando carrito:', error);
        // Fallback a GET si hay error
        fetch('/api/v2/categorias/carrito')
        .then(response => response.text())
        .then(html => {
            document.getElementById('reemplazar').innerHTML = html;
        });
    });
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
        const cartItem = cart.find(item => item.id === productId);
        if (cartItem) {
            display.textContent = cartItem.quantity;
        } else {
            display.textContent = '1';
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
            const productImageUrl = e.target.dataset.productImageUrl || null;
            addToCart(productId, productName, productPrice, productImageUrl);
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