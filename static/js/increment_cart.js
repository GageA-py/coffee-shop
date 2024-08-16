document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[id^=increment-]').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.id.split('-')[1];
            const quantityInput = document.getElementById(`quantity-${productId}`);
            let quantity = parseInt(quantityInput.value) || 0;
            quantity++;
            quantityInput.value = quantity;
            updateCart(productId, quantity);
        });
    });

    document.querySelectorAll('[id^=decrement-]').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.id.split('-')[1];
            const quantityInput = document.getElementById(`quantity-${productId}`);
            let quantity = parseInt(quantityInput.value) || 0;
            if (quantity > 1) {
                quantity--;
                quantityInput.value = quantity;
                updateCart(productId, quantity);
            }
        });
    });

    function updateCart(productId, quantity) {
        fetch(`/update_cart/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            },
            body: JSON.stringify({ quantity: quantity })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Server response:', data);
            if (data.success) {
                updateTotalPrice();  // Call to update the total price
            } else {
                console.error('Failed to update cart');
            }
        })
        .catch(error => {
            console.error('Error updating cart:', error);
        });
    }
    
    function updateTotalPrice() {
        console.log('Updating total price...');
        const cartItems = document.querySelectorAll('.cart-item');
        let totalPrice = 0;

        cartItems.forEach(item => {
            const quantity = parseInt(item.querySelector('.quantity-input').value) || 0;
            const priceText = item.querySelector('.item-price').textContent;
            const price = parseFloat(priceText.replace('$', '').trim()) || 0;
            totalPrice += quantity * price;
        });

        console.log('Calculated total price:', totalPrice);
        document.getElementById('total-price').textContent = `$${totalPrice.toFixed(2)}`;
    }

    updateTotalPrice();  // Initialize total price on page load
});
