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
    if (cart.length === 0) {
        return;
    }
    
    cart.forEach(item => {
        const productExists = document.getElementById(`addButton_${item.id}`);
        
        if (productExists) {
            // Si el producto está en el carrito, mostrar el selector de cantidad
            showQuantitySelector(item.id);
            // Actualizar la cantidad mostrada con la cantidad del carrito
            updateQuantityDisplay(item.id);
        }
    });
}

// Función para sincronizar un producto específico con el carrito
function syncProductWithCart(productId) {
    const cartItem = cart.find(item => item.id === productId);
    if (cartItem) {
        // Si está en el carrito, mostrar selector y sincronizar cantidad
        showQuantitySelector(productId);
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
function showQuantitySelector(productId) {
    const addButton = document.getElementById(`addButton_${productId}`);
    const quantitySelector = document.getElementById(`quantitySelector_${productId}`);
    
    if (addButton && quantitySelector) {
        addButton.classList.add('hidden');
        quantitySelector.classList.remove('hidden');
        console.log(`✅ Quantity selector shown for product ${productId}`);
    } else {
        console.warn(`❌ Could not find elements for product ${productId}`);
    }
}

// Ocultar el selector de cantidad para un producto específico
function hideQuantitySelector(productId) {
    const addButton = document.getElementById(`addButton_${productId}`);
    const quantitySelector = document.getElementById(`quantitySelector_${productId}`);
    
    if (addButton && quantitySelector) {
        addButton.classList.remove('hidden');
        quantitySelector.classList.add('hidden');
        // Resetear el display de cantidad a 1
        updateQuantityDisplay(productId);
        console.log(`✅ Quantity selector hidden for product ${productId}`);
    } else {
        console.warn(`❌ Could not find elements for product ${productId}`);
    }
}

// Incrementar cantidad para un producto específico
function increaseQuantity(productId) {
    const cartItem = cart.find(item => item.id === productId);
    if (cartItem) {
        cartItem.quantity++;
        saveCart();
        updateCartCount();
        updateQuantityDisplay(productId);
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
            updateQuantityDisplay(productId);
        } else {
            // Si la cantidad es 1, remover del carrito y ocultar el selector
            removeFromCart(productId);
            hideQuantitySelector(productId);
        }
    }
}

// Actualizar la visualización de cantidad para un producto específico
function updateQuantityDisplay(productId) {
    const quantityDisplay = document.getElementById(`quantityDisplay_${productId}`);
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

    // Usar la función clearCart para limpiar
    clearCart();
}

// Función específica para limpiar el carrito
function clearCart() {
    // Vaciar carrito
    cart = [];
    saveCart();
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
    
    console.log('Carrito limpiado exitosamente');
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
    console.log('Sending cart to backend. Cart length:', cart.length);
    
    if (!cart || cart.length === 0) {
        // Si el carrito está vacío, usar GET
        console.log('Cart is empty, using GET request');
        fetch('/api/v2/categorias/carrito', {
            method: 'GET',
            headers: {
                'Accept': 'text/html',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            document.getElementById('reemplazar').innerHTML = html;
            console.log('Empty cart view loaded successfully');
        })
        .catch(error => {
            console.error('Error cargando carrito vacío:', error);
            document.getElementById('reemplazar').innerHTML = '<div class="error-message">Error al cargar el carrito</div>';
        });
        return;
    }
    
    // Enviar datos del carrito al backend via POST
    console.log('Cart has items, using POST request');
    fetch('/api/v2/categorias/carrito', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/html',
        },
        body: JSON.stringify({
            items: cart
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        document.getElementById('reemplazar').innerHTML = html;
        console.log('Cart with items loaded successfully');
    })
    .catch(error => {
        console.error('Error enviando carrito:', error);
        // Fallback a GET si hay error
        console.log('Falling back to GET request');
        fetch('/api/v2/categorias/carrito', {
            method: 'GET',
            headers: {
                'Accept': 'text/html',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            document.getElementById('reemplazar').innerHTML = html;
            console.log('Fallback cart view loaded');
        })
        .catch(fallbackError => {
            console.error('Fallback also failed:', fallbackError);
            document.getElementById('reemplazar').innerHTML = '<div class="error-message">Error al cargar el carrito</div>';
        });
    });
}



// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadCart();
    updateCartCount();
    
    // Inicializar todas las cantidades en 1 para productos que no están en el carrito
    initializeProductQuantities();
});

// Event delegation para botones de agregar al carrito (en scope global)
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