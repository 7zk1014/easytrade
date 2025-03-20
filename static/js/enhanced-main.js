// EasyTrade Enhanced JavaScript

$(document).ready(function() {
    console.log("EasyTrade Enhanced JS loaded successfully.");
    
    // Add page loading animation
    animateElementsOnLoad();
    
    // Animation effect on scroll
    $(window).on('scroll', function() {
        animateOnScroll();
    });
    
    // Enhanced shopping cart quantity control
    initQuantityControls();
    
    // Enhanced product image preview
    initImagePreview();
    
    // Enhanced AJAX add to cart
    initAjaxAddToCart();
    
    // Enhanced live search
    initLiveSearch();
    
    // Enhanced tab functionality
    initTabs();
    
    // Enhanced form validation
    initFormValidation();
    
    // Enhanced hover effects
    initHoverEffects();
    
    // Enhanced modal effects
    initModalEffects();
});

// Animation effects on page load
function animateElementsOnLoad() {
    // Add different animation classes for elements
    $('.hero-section').addClass('fade-in');
    
    // Add delayed animation for navigation items
    $('.navbar-nav .nav-item').each(function(index) {
        $(this).css('animation-delay', (index * 0.1) + 's');
        $(this).addClass('slide-in-right');
    });
    
    // Add staggered animation for product cards
    $('.product-card').each(function(index) {
        $(this).css('animation-delay', (index * 0.05) + 's');
        $(this).addClass('scale-in');
    });
    
    // Add staggered animation for category cards
    $('.category-card').each(function(index) {
        $(this).css('animation-delay', (index * 0.05) + 's');
        $(this).addClass('fade-in');
    });
}

// Animation effects on scroll
function animateOnScroll() {
    $('.animate-on-scroll').each(function() {
        const elementTop = $(this).offset().top;
        const elementHeight = $(this).outerHeight();
        const windowHeight = $(window).height();
        const scrollY = $(window).scrollTop();
        
        // Add animation class when element enters viewport
        if (scrollY > elementTop - windowHeight + elementHeight / 2) {
            $(this).addClass('animated');
        }
    });
}

// Enhanced shopping cart quantity control
function initQuantityControls() {
    $('#decreaseQuantity').on('click', function() {
        let quantity = parseInt($('#quantity').val());
        if (quantity > 1) {
            $('#quantity').val(quantity - 1);
            $(this).addClass('active');
            setTimeout(() => $(this).removeClass('active'), 200);
        }
    });
    
    $('#increaseQuantity').on('click', function() {
        let quantity = parseInt($('#quantity').val());
        if (quantity < 10) {
            $('#quantity').val(quantity + 1);
            $(this).addClass('active');
            setTimeout(() => $(this).removeClass('active'), 200);
        }
    });
    
    // Quantity input validation
    $('#quantity').on('change', function() {
        let quantity = parseInt($(this).val());
        if (isNaN(quantity) || quantity < 1) {
            $(this).val(1);
        } else if (quantity > 10) {
            $(this).val(10);
        }
    });
}

// Enhanced product image preview
function initImagePreview() {
    $('#id_image').on('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $('#imagePreview').html(`<img src="${e.target.result}" alt="Preview" class="img-preview">`);
                $('#imagePreview img').addClass('scale-in');
            }
            reader.readAsDataURL(file);
        }
    });
}

// Enhanced AJAX add to cart
function initAjaxAddToCart() {
    $('.ajax-add-to-cart').on('click', function(e) {
        e.preventDefault();
        const button = $(this);
        const productId = button.data('product-id');
        const quantity = 1;
        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

        button.html('<i class="fas fa-spinner fa-spin"></i> Adding...');
        button.prop('disabled', true);
        
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
                    showNotification('Item added to cart', 'success');
                    button.html('<i class="fas fa-check"></i> Added');
                    setTimeout(() => {
                        button.html('<i class="fas fa-cart-plus"></i> Add to Cart');
                        button.prop('disabled', false);
                    }, 2000);
                } else {
                    showNotification('Failed to add: ' + response.message, 'danger');
                    button.html('<i class="fas fa-times"></i> Failed');
                    setTimeout(() => {
                        button.html('<i class="fas fa-cart-plus"></i> Add to Cart');
                        button.prop('disabled', false);
                    }, 2000);
                }
            },
            error: function() {
                showNotification('Failed to add, please try again later', 'danger');
                button.html('<i class="fas fa-times"></i> Failed');
                setTimeout(() => {
                    button.html('<i class="fas fa-cart-plus"></i> Add to Cart');
                    button.prop('disabled', false);
                }, 2000);
            }
        });
    });
}

// Enhanced live search
function initLiveSearch() {
    let searchTimeout;
    const searchInput = $('#live-search');
    const resultsContainer = $('#search-results');
    
    if (searchInput.length) {
        // Add search loading indicator
        searchInput.after('<div class="search-indicator"><i class="fas fa-spinner fa-spin"></i></div>');
        const searchIndicator = $('.search-indicator');
        searchIndicator.hide();
        
        searchInput.on('input', function() {
            clearTimeout(searchTimeout);
            const query = $(this).val();
            
            if (query.length >= 2) {
                searchIndicator.fadeIn(200);
                searchTimeout = setTimeout(function() {
                    $.ajax({
                        url: '/search/ajax/',
                        type: 'GET',
                        data: {'query': query},
                        success: function(response) {
                            displaySearchResults(response.results);
                            searchIndicator.fadeOut(200);
                        },
                        error: function() {
                            resultsContainer.html('<p class="text-center py-3 text-danger">Search error, please try again</p>');
                            resultsContainer.show();
                            searchIndicator.fadeOut(200);
                        }
                    });
                }, 500);
            } else {
                resultsContainer.empty().hide();
                searchIndicator.fadeOut(200);
            }
        });
        
        // Close search results when clicking outside
        $(document).on('click', function(e) {
            if (!searchInput.is(e.target) && !resultsContainer.is(e.target) && resultsContainer.has(e.target).length === 0) {
                resultsContainer.empty().hide();
            }
        });
    }
}

// Display search results enhanced
function displaySearchResults(results) {
    const resultsContainer = $('#search-results');
    resultsContainer.empty();
    
    if (results.length > 0) {
        const resultsList = $('<div class="list-group search-results-list"></div>');
        
        results.forEach(function(product, index) {
            const resultItem = $(`
                <a href="/products/${product.id}/" class="list-group-item list-group-item-action search-result-item">
                    <div class="d-flex align-items-center">
                        <div class="flex-shrink-0 search-result-image">
                            ${product.image ? `<img src="${product.image}" alt="${product.title}" width="60">` : '<div class="no-image-small"><i class="fas fa-image"></i></div>'}
                        </div>
                        <div class="ms-3 search-result-details">
                            <h6 class="mb-0">${product.title}</h6>
                            <p class="mb-0 search-result-price">￥${product.price}</p>
                            <small class="text-muted">${product.category}</small>
                        </div>
                    </div>
                </a>
            `);

            resultItem.css('animation-delay', (index * 0.05) + 's');
            resultItem.addClass('slide-in-right');
            
            resultsList.append(resultItem);
        });
        
        resultsContainer.append(resultsList);
        resultsContainer.show();
    } else {
        resultsContainer.html('<p class="text-center py-3">No products found</p>');
        resultsContainer.show();
    }
}

// Show notification message enhanced
function showNotification(message, type) {
    const iconMap = {
        'success': '<i class="fas fa-check-circle me-2"></i>',
        'danger': '<i class="fas fa-exclamation-circle me-2"></i>',
        'warning': '<i class="fas fa-exclamation-triangle me-2"></i>',
        'info': '<i class="fas fa-info-circle me-2"></i>'
    };
    
    const icon = iconMap[type] || '';
    
    const notification = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${icon}${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);
    
    $('.messages').append(notification);
    notification.addClass('slide-in-right');

    setTimeout(function() {
        notification.removeClass('slide-in-right').addClass('slide-out-right');
        setTimeout(() => notification.alert('close'), 500);
    }, 5000);
}

// Tab functionality enhanced
function initTabs() {
    const tabButtons = $('.tab-btn');
    const tabPanes = $('.tab-pane');
    
    if (tabButtons.length) {
        tabButtons.on('click', function() {
            const targetTab = $(this).data('tab');

            tabButtons.removeClass('active');
            tabPanes.removeClass('active');

            $(this).addClass('active');
            $(`#${targetTab}`).addClass('active');
        });
    }
}

// Form validation enhanced
function initFormValidation() {
    const forms = $('.needs-validation');
    
    if (forms.length) {
        forms.each(function() {
            const form = $(this);
            
            form.on('submit', function(event) {
                if (!this.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();

                    const firstInvalid = form.find(':invalid').first();
                    if (firstInvalid.length) {
                        $('html, body').animate({
                            scrollTop: firstInvalid.offset().top - 100
                        }, 500);
                        firstInvalid.focus();
                    }
                }
                
                form.addClass('was-validated');
            });

            form.find('input, textarea, select').on('input blur', function() {
                const field = $(this);
                const feedbackEl = field.next('.invalid-feedback');
                
                if (this.checkValidity()) {
                    field.removeClass('is-invalid').addClass('is-valid');
                } else {
                    field.removeClass('is-valid').addClass('is-invalid');
                }
            });
        });
    }
}

// Hover effects enhanced
function initHoverEffects() {
    $('.btn').on({
        mouseenter: function() {
            $(this).addClass('btn-hover');
        },
        mouseleave: function() {
            $(this).removeClass('btn-hover');
        }
    });

    $('.product-card, .category-card, .related-product-card').on({
        mouseenter: function() {
            $(this).addClass('card-hover');
        },
        mouseleave: function() {
            $(this).removeClass('card-hover');
        }
    });
}

// Modal effects enhanced
function initModalEffects() {
    const modal = $('#offerModal');
    const btn = $('#makeOfferBtn');
    const closeBtn = $('.close');
    
    if (btn.length && modal.length) {
        btn.on('click', function() {
            modal.fadeIn(300);
            modal.addClass('modal-open');
        });
        
        closeBtn.on('click', function() {
            modal.fadeOut(300);
            setTimeout(() => modal.removeClass('modal-open'), 300);
        });
        
        $(window).on('click', function(e) {
            if ($(e.target).is(modal)) {
                modal.fadeOut(300);
                setTimeout(() => modal.removeClass('modal-open'), 300);
            }
        });
    }
    
    $('.modal-content').addClass('scale-in');
}


$(document).ready(function() {

    $('.product-detail-container').addClass('animate-on-scroll');
    $('.product-gallery').addClass('animate-on-scroll');
    $('.product-info').addClass('animate-on-scroll');
    $('.product-details-tabs').addClass('animate-on-scroll');
    $('.related-products').addClass('animate-on-scroll');

    $('.product-card').addClass('animate-on-scroll');
    $('.category-card').addClass('animate-on-scroll');

    $('.btn, .btn-primary, .btn-secondary, .btn-add-to-cart, .btn-buy-now, .btn-view-details, .btn-add-cart').addClass('ripple');
    
    $(document).on('click', '.ripple', function(e) {
        const button = $(this);
        const ripple = $('<span class="ripple-effect"></span>');
        const diameter = Math.max(button.outerWidth(), button.outerHeight());
        const radius = diameter / 2;
        
        ripple.css({
            width: diameter,
            height: diameter,
            left: e.pageX - button.offset().left - radius,
            top: e.pageY - button.offset().top - radius
        });
        
        button.append(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
});

$(window).on('scroll', function() {
    if ($(this).scrollTop() > 300) {
        if (!$('#scroll-to-top').length) {
            $('body').append('<button id="scroll-to-top" title="Back to Top"><i class="fas fa-arrow-up"></i></button>');
            $('#scroll-to-top').fadeIn(300);
        }
    } else {
        $('#scroll-to-top').fadeOut(300, function() {
            $(this).remove();
        });
    }
});

$(document).on('click', '#scroll-to-top', function() {
    $('html, body').animate({scrollTop: 0}, 500);
    return false;
});

function lazyLoadImages() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const image = entry.target;
                    image.src = image.dataset.src;
                    image.classList.add('fade-in');
                    imageObserver.unobserve(image);
                }
            });
        });
        
        lazyImages.forEach(function(image) {
            imageObserver.observe(image);
        });
    } else {
        lazyImages.forEach(function(image) {
            image.src = image.dataset.src;
        });
    }
}

$(window).on('load', function() {
    lazyLoadImages();
});

document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    const messageForm = document.getElementById('messageForm');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            fetch(this.action, {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload(); 
                }
            });
        });
    }
});

function initProductTabs() {
    $('.tab-btn').on('click', function() {
        const tabId = $(this).data('tab');
        $('.tab-btn').removeClass('active');
        $(this).addClass('active');
        $('.tab-pane').removeClass('active').hide();
        $('#' + tabId).addClass('active').show();
    });

    $('.tab-btn:first').click();
}

$(document).ready(function() {

    initProductTabs();
});