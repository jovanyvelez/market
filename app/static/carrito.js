// Estado del carrito
let cart = [];
window.cart = cart;


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


// Guardar el carrito en localStorage
function saveCart() {
    localStorage.setItem('shoppingCart', JSON.stringify(cart));
    window.cart = cart; // Sincronizar con window.cart
}

// Actualizar el contador del carrito
function updateCartCount() {
    const countElement = document.getElementById('cart-count');
    if (countElement) {
        countElement.textContent = cart.length;
    }
}

// Función para añadir al carrito
function addToCart(id, name, price, imageUrl = null) {
    const existingItem = cart.find(item => item.id === id);
    const isFirstItem = cart.length === 0; // Verificar si el carrito está vacío antes de agregar

    if (existingItem) {
        existingItem.quantity += 1;
        // Mostrar notificación normal para incremento de cantidad
        showNotification(`${name} cantidad actualizada`);
    } else {
        cart.push({
            id,
            name,
            price,
            quantity: 1,
            imageUrl: imageUrl && imageUrl.trim() !== '' ? imageUrl : null
        });
        
        // Mostrar notificación especial si es el primer producto
        if (isFirstItem) {
            showNotification('Primer producto añadido al carrito');
        } else {
            showNotification(`${name} añadido al carrito`);
        }
    }

    saveCart();
    updateCartCount();

    // Mostrar el selector de cantidad
    showQuantitySelector(id);

    // Sincronizar la cantidad mostrada con la del carrito
    updateQuantityDisplay(id);
}

// Mostrar el selector de cantidad para un producto específico
function showQuantitySelector(productId) {
    const addButton = document.getElementById(`addButton_${productId}`);
    const quantitySelector = document.getElementById(`quantitySelector_${productId}`);

    if (addButton && quantitySelector) {
        addButton.classList.add('hidden');
        quantitySelector.classList.remove('hidden');
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
        
        // Si estamos en la vista del carrito, actualizar también el HTML
        updateCartDisplay();
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
            
            // Si estamos en la vista del carrito, actualizar también el HTML
            updateCartDisplay();
        } else {
            // Si la cantidad es 1, remover del carrito
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
                    <button class="remove-btn" data-product-id="${item.id}">Eliminar</button>
                </div>
            </div>
        `;
    });

    cartItems.innerHTML = itemsHTML;
    cartTotal.textContent = total.toFixed(2);
    
    // Actualizar también el form del checkout
    generateCheckoutForm();
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

    updateCartDisplay();
}

// Generar formulario para checkout con datos del carrito
function generateCheckoutForm() {
    const checkoutContainer = document.getElementById('checkout-container');
    if (!checkoutContainer) return;

    // Limpiar contenido existente
    checkoutContainer.innerHTML = '';

    // Crear el botón para mostrar el formulario de checkout
    const submitBtn = document.createElement('button'); 
    submitBtn.id = 'checkout-btn';
    submitBtn.className = 'checkout-btn';
    submitBtn.textContent = 'Finalizar Compra';
    submitBtn.disabled = cart.length === 0;
    submitBtn.setAttribute('hx-get', '/checkout-form');
    submitBtn.setAttribute('hx-target', '#reemplazar');
    submitBtn.setAttribute('hx-swap', 'innerHTML');
    checkoutContainer.appendChild(submitBtn);

    // Procesar el botón con HTMX para que funcione
    htmx.process(submitBtn);
}

// Mostrar notificación
function showNotification(message) {
    let notification = document.getElementById('notification');
    
    // Si no existe el elemento notification, crearlo dinámicamente
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.className = 'notification';
        document.body.appendChild(notification);
    }
    
    notification.textContent = message;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 2000);
}


// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadCart();
    updateCartCount();

    // Inicializar todas las cantidades en 1 para productos que no están en el carrito
    initializeProductQuantities();
    
    updateCartDisplay();
});

// Función para mostrar la vista completa del carrito desde JavaScript
function mostrarCarrito() {
    // Si ya estamos en la vista del carrito, no hacer nada
    if (document.querySelector('.carrito-container')) {
        return;
    }
    
    // Crear HTML completo del carrito
    const html = `     
        <div class="carrito-container">
            <h2>Mi Carrito de Compras</h2>
            
            <div id="cart-items" class="cart-items">
                <!-- Los items se generarán aquí -->
            </div>
            
            <div class="cart-total-section">
                <div class="cart-total">
                    <strong>Total: $</strong><span id="cart-total">0.00</span>
                </div>
                <div id="checkout-container">
                    <!-- El botón se generará aquí dinámicamente -->
                </div>
            </div>
            
            <div id="notification" class="notification"></div>
            <div id="resultado"></div>
        </div>
    `;
    
    // Reemplazar solo el contenido del div "reemplazar" en lugar de todo el body
    const reemplazarDiv = document.getElementById('reemplazar');
    if (reemplazarDiv) {
        reemplazarDiv.innerHTML = html;
    } else {
        console.error('No se encontró el div con id "reemplazar"');
        return;
    }
    
    // Cargar el carrito desde localStorage
    loadCart();
    
    // Generar la vista del carrito
    updateCartDisplay();
    
    // Configurar event listeners para los botones dinámicos
    setupCartEventListeners();
}

// Función para volver a la vista de productos
function volverAProductos() {
    // Usar HTMX para cargar la vista de productos en el div "reemplazar"
    if (typeof htmx !== 'undefined') {
        // Cargar la vista de categorías raíz activas
        fetch('/api/v2/categorias/raiz_activas')
            .then(response => response.text())
            .then(html => {
                const reemplazarDiv = document.getElementById('reemplazar');
                if (reemplazarDiv) {
                    reemplazarDiv.innerHTML = html;
                    // Recargar las funciones del carrito después de cambiar el contenido
                    setTimeout(() => {
                        loadCart();
                        updateCartCount();
                        updateProductsInterface();
                    }, 100);
                }
            })
            .catch(error => {
                console.error('Error cargando productos:', error);
                // Fallback: recargar la página completa
                window.location.href = '/';
            });
    } else {
        // Fallback si HTMX no está disponible
        window.location.href = '/';
    }
}

// Configurar event listeners para botones dinámicos del carrito
function setupCartEventListeners() {
    // Event delegation para manejar clicks en botones dinámicos del carrito
    document.addEventListener('click', function(event) {
        const target = event.target;
        
        // Manejar clicks en el icono del carrito (solo si no estamos ya en la vista del carrito)
        if (target.closest('#cart-icon') && !document.querySelector('.carrito-container')) {
            mostrarCarrito();
            event.preventDefault();
        }
    });
}

// Variables para controlar el long press
let pressTimer;
const longPressDelay = 800; // 800ms para long press - balance entre usabilidad y prevención de clicks accidentales

// Detectar si es dispositivo touchscreen
const isTouchDevice = 'ontouchstart' in window;

// Función para manejar la acción de los botones
function handleButtonAction(target) {
    // Evitar procesar clicks en el cart-icon
    if (target.closest('#cart-icon') || target.id === 'cart-icon') {
        return;
    }
    
    if (target.classList.contains('add-button')) {
        const productId = parseInt(target.dataset.productId);
        const productName = target.dataset.productName;
        const productPrice = parseFloat(target.dataset.productPrice);
        const productImageUrl = target.dataset.productImageUrl || null;

        addToCart(productId, productName, productPrice, productImageUrl);
    }

    if (target.classList.contains('increase-btn')) {
        const productId = parseInt(target.dataset.productId);
        increaseQuantity(productId);
    }

    if (target.classList.contains('decrease-btn')) {
        const productId = parseInt(target.dataset.productId);
        decreaseQuantity(productId);
    }
    
    // Manejar clicks en botones de eliminar (estos no necesitan long press)
    if (target.classList.contains('remove-btn')) {
        const productId = parseInt(target.dataset.productId);
        removeFromCart(productId);
    }
}

// Event delegation para dispositivos táctiles - Long press requerido
if (isTouchDevice) {
    document.addEventListener('touchstart', (e) => {
        const target = e.target;
        
        // Solo aplicar long press a botones específicos del carrito
        if (target.classList.contains('add-button') || 
            target.classList.contains('increase-btn') || 
            target.classList.contains('decrease-btn')) {
            
            e.preventDefault(); // Prevenir scroll accidental
            
            // Iniciar timer para long press
            pressTimer = setTimeout(() => {
                handleButtonAction(target);
            }, longPressDelay);
        }
        // Los botones remove-btn mantienen comportamiento inmediato
        else if (target.classList.contains('remove-btn')) {
            handleButtonAction(target);
        }
    });

    document.addEventListener('touchend', (e) => {
        // Cancelar el timer si se suelta antes del long press
        clearTimeout(pressTimer);
    });

    document.addEventListener('touchmove', (e) => {
        // Cancelar el timer si hay movimiento (scroll)
        clearTimeout(pressTimer);
    });
}

// Event delegation para clicks normales (desktop o fallback)
document.addEventListener('click', (e) => {
    const target = e.target;
    
    // En dispositivos no táctiles, comportamiento normal
    if (!isTouchDevice) {
        handleButtonAction(target);
    }
    // En dispositivos táctiles, solo manejar botones que no requieren long press
    else if (target.classList.contains('remove-btn')) {
        handleButtonAction(target);
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

// También ejecutar cuando HTMX carga esta vista
document.addEventListener('htmx:afterSwap', function (event) {
    if (event.target.id === 'reemplazar') {
        setTimeout(function () {
            if (typeof updateCartDisplay === 'function') {
                updateCartDisplay();
            }
        }, 100);
    }
});
// También escuchar el evento afterSettle por si acaso
document.addEventListener('htmx:afterSettle', (event) => {
    setTimeout(() => {
        updateProductsInterface();
    }, 50);
});


async function enviarCarrito(e) {
    e.preventDefault(); // Prevenir el comportamiento por defecto del formulario
    
    try {
        const response = await fetch('/prueba', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(cart) // Enviar el carrito completo como JSON
        });
        
        // Verificar si la respuesta es exitosa (opcional, pero recomendado)
        if (!response.ok) {
            throw new Error(`Error en la respuesta: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Respuesta del servidor:', data);
        
        // Calcular datos para el resumen
        const total_items = cart.length;
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const items = [...cart]; // Copia de los items
        
        // Generar HTML del resumen
        let itemsHTML = '';
        items.forEach(item => {
            const itemTotal = item.price * item.quantity;
            itemsHTML += `
                <div class='item'>
                    ID: ${item.id}, ${item.name} - $${item.price.toFixed(2)} x ${item.quantity} = $${itemTotal.toFixed(2)}
                </div>
            `;
        });
        
        const summaryHTML = `
            <div class="result success">
                <h3>✅ ¡Compra procesada exitosamente!</h3>
                <p><strong>Total productos:</strong> ${total_items}</p>
                <p><strong>Valor total:</strong> $${total.toFixed(2)}</p>
                <div><strong>Productos comprados:</strong>
                    ${itemsHTML}
                </div>
                <p style='margin-top: 15px; color: #28a745; font-weight: bold;'>
                    ¡Gracias por tu compra! 🎉
                </p>
                <div style="margin-top: 20px;">
                    <button onclick="volverAProductos()"
                        style="background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                        Seguir Comprando
                    </button>
                </div>
            </div>
        `;
        
        // Reemplazar el contenido del div "reemplazar" con el resumen
        const reemplazarDiv = document.getElementById('reemplazar');
        if (reemplazarDiv) {
            reemplazarDiv.innerHTML = summaryHTML;
        }
        
        // Limpiar el carrito después de mostrar el resumen
        clearCart();
        
    } catch (error) {
        console.error('Error enviando datos a /prueba:', error);
    }
}