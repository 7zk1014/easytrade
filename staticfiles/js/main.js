// EasyTrade Main JavaScript

$(document).ready(function() {
    console.log("EasyTrade loaded successfully.");
    
    // Add fade-in animation effect
    $('.hero-section, .product-card, .category-card').addClass('fade-in');
    
    // Cart quantity control
    $('#decreaseQuantity').on('click', function() {
        let quantity = parseInt($('#quantity').val());
        if (quantity > 1) {
            $('#quantity').val(quantity - 1);
        }
    });
    
    $('#increaseQuantity').on('click', function() {
        let quantity = parseInt($('#quantity').val());
        if (quantity < 10) {
            $('#quantity').val(quantity + 1);
        }
    });
    
    // Product image preview
    $('#id_image').on('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $('#imagePreview').html(`<img src="${e.target.result}" alt="Preview" class="img-preview">`);
            }
            reader.readAsDataURL(file);
        }
    });
    
    // Use AJAX to add product to cart
    $('.ajax-add-to-cart').on('click', function(e) {
        e.preventDefault();
        const productId = $(this).data('product-id');
        const quantity = 1;
        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        $.ajax({
            url: '/cart/add/',
            type: 'POST',
            data: {
                'product_id': productId,
                'quantity': quantity,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.status === 'success') {
                    showNotification('Product added to cart', 'success');
                } else {
                    showNotification('Failed to add: ' + response.message, 'danger');
                }
            },
            error: function() {
                showNotification('Failed to add, please try again later', 'danger');
            }
        });
    });
    
    // Use AJAX to search products
    let searchTimeout;
    $('#live-search').on('input', function() {
        clearTimeout(searchTimeout);
        const query = $(this).val();
        
        if (query.length >= 3) {
            searchTimeout = setTimeout(function() {
                $.ajax({
                    url: '/search/ajax/',
                    type: 'GET',
                    data: {'query': query},
                    success: function(response) {
                        displaySearchResults(response.results);
                    }
                });
            }, 500);
        } else {
            $('#search-results').empty().hide();
        }
    });
    
    // Display notification message
    function showNotification(message, type) {
        const notification = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        $('.messages').append(notification);
        
        // Auto close after 5 seconds
        setTimeout(function() {
            $('.alert').alert('close');
        }, 5000);
    }
    
    // Display search results
    function displaySearchResults(results) {
        const resultsContainer = $('#search-results');
        resultsContainer.empty();
        
        if (results.length > 0) {
            const resultsList = $('<div class="list-group"></div>');
            
            results.forEach(function(product) {
                const resultItem = `
                    <a href="/products/${product.id}/" class="list-group-item list-group-item-action">
                        <div class="d-flex align-items-center">
                            <div class="flex-shrink-0">
                                ${product.image ? `<img src="${product.image}" alt="${product.title}" width="50">` : '<div class="no-image-small">No Image</div>'}
                            </div>
                            <div class="ms-3">
                                <h6 class="mb-0">${product.title}</h6>
                                <p class="mb-0 text-primary">£${product.price}</p>
                            </div>
                        </div>
                    </a>
                `;
                resultsList.append(resultItem);
            });
            
            resultsContainer.append(resultsList);
            resultsContainer.show();
        } else {
            resultsContainer.html('<p class="text-center py-3">No related products found</p>');
            resultsContainer.show();
        }
    }
    
    // Form validation
    $('.needs-validation').on('submit', function(event) {
        if (!this.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        }
        $(this).addClass('was-validated');
    });
});
