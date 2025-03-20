// EasyTrade Enhanced JavaScript

$(document).ready(function() {
    console.log("EasyTrade Enhanced JS loaded successfully.");
    
    // 添加页面加载动画
    animateElementsOnLoad();
    
    // 滚动时的动画效果
    $(window).on('scroll', function() {
        animateOnScroll();
    });
    
    // 购物车数量控制增强
    initQuantityControls();
    
    // 产品图片预览增强
    initImagePreview();
    
    // AJAX添加到购物车增强
    initAjaxAddToCart();
    
    // 实时搜索增强
    initLiveSearch();
    
    // 标签页功能增强
    initTabs();
    
    // 表单验证增强
    initFormValidation();
    
    // 悬停效果增强
    initHoverEffects();
    
    // 模态框增强
    initModalEffects();
});

// 页面加载时的动画效果
function animateElementsOnLoad() {
    // 为不同元素添加不同的动画类
    $('.hero-section').addClass('fade-in');
    
    // 为导航项添加延迟动画
    $('.navbar-nav .nav-item').each(function(index) {
        $(this).css('animation-delay', (index * 0.1) + 's');
        $(this).addClass('slide-in-right');
    });
    
    // 为产品卡片添加交错动画
    $('.product-card').each(function(index) {
        $(this).css('animation-delay', (index * 0.05) + 's');
        $(this).addClass('scale-in');
    });
    
    // 为类别卡片添加交错动画
    $('.category-card').each(function(index) {
        $(this).css('animation-delay', (index * 0.05) + 's');
        $(this).addClass('fade-in');
    });
}

// 滚动时的动画效果
function animateOnScroll() {
    $('.animate-on-scroll').each(function() {
        const elementTop = $(this).offset().top;
        const elementHeight = $(this).outerHeight();
        const windowHeight = $(window).height();
        const scrollY = $(window).scrollTop();
        
        // 当元素进入视口时添加动画类
        if (scrollY > elementTop - windowHeight + elementHeight / 2) {
            $(this).addClass('animated');
        }
    });
}

// 购物车数量控制增强
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
    
    // 数量输入验证
    $('#quantity').on('change', function() {
        let quantity = parseInt($(this).val());
        if (isNaN(quantity) || quantity < 1) {
            $(this).val(1);
        } else if (quantity > 10) {
            $(this).val(10);
        }
    });
}

// 产品图片预览增强
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

// AJAX添加到购物车增强
function initAjaxAddToCart() {
    $('.ajax-add-to-cart').on('click', function(e) {
        e.preventDefault();
        const button = $(this);
        const productId = button.data('product-id');
        const quantity = 1;
        const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        
        // 添加加载动画
        button.html('<i class="fas fa-spinner fa-spin"></i> 添加中...');
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
                    showNotification('商品已添加到购物车', 'success');
                    button.html('<i class="fas fa-check"></i> 已添加');
                    setTimeout(() => {
                        button.html('<i class="fas fa-cart-plus"></i> 加入购物车');
                        button.prop('disabled', false);
                    }, 2000);
                } else {
                    showNotification('添加失败: ' + response.message, 'danger');
                    button.html('<i class="fas fa-times"></i> 添加失败');
                    setTimeout(() => {
                        button.html('<i class="fas fa-cart-plus"></i> 加入购物车');
                        button.prop('disabled', false);
                    }, 2000);
                }
            },
            error: function() {
                showNotification('添加失败，请稍后再试', 'danger');
                button.html('<i class="fas fa-times"></i> 添加失败');
                setTimeout(() => {
                    button.html('<i class="fas fa-cart-plus"></i> 加入购物车');
                    button.prop('disabled', false);
                }, 2000);
            }
        });
    });
}

// 实时搜索增强
function initLiveSearch() {
    let searchTimeout;
    const searchInput = $('#live-search');
    const resultsContainer = $('#search-results');
    
    if (searchInput.length) {
        // 添加搜索加载指示器
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
                            resultsContainer.html('<p class="text-center py-3 text-danger">搜索出错，请重试</p>');
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
        
        // 点击外部关闭搜索结果
        $(document).on('click', function(e) {
            if (!searchInput.is(e.target) && !resultsContainer.is(e.target) && resultsContainer.has(e.target).length === 0) {
                resultsContainer.empty().hide();
            }
        });
    }
}

// 显示搜索结果增强
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
            
            // 添加延迟动画
            resultItem.css('animation-delay', (index * 0.05) + 's');
            resultItem.addClass('slide-in-right');
            
            resultsList.append(resultItem);
        });
        
        resultsContainer.append(resultsList);
        resultsContainer.show();
    } else {
        resultsContainer.html('<p class="text-center py-3">没有找到相关商品</p>');
        resultsContainer.show();
    }
}

// 显示通知消息增强
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
    
    // 自动关闭
    setTimeout(function() {
        notification.removeClass('slide-in-right').addClass('slide-out-right');
        setTimeout(() => notification.alert('close'), 500);
    }, 5000);
}

// 标签页功能增强
function initTabs() {
    const tabButtons = $('.tab-btn');
    const tabPanes = $('.tab-pane');
    
    if (tabButtons.length) {
        tabButtons.on('click', function() {
            const targetTab = $(this).data('tab');
            
            // 移除所有活动状态
            tabButtons.removeClass('active');
            tabPanes.removeClass('active');
            
            // 添加活动状态到当前标签
            $(this).addClass('active');
            $(`#${targetTab}`).addClass('active');
        });
    }
}

// 表单验证增强
function initFormValidation() {
    const forms = $('.needs-validation');
    
    if (forms.length) {
        forms.each(function() {
            const form = $(this);
            
            form.on('submit', function(event) {
                if (!this.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    // 高亮显示第一个错误字段
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
            
            // 实时验证反馈
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

// 悬停效果增强
function initHoverEffects() {
    // 为按钮添加悬停效果
    $('.btn').on({
        mouseenter: function() {
            $(this).addClass('btn-hover');
        },
        mouseleave: function() {
            $(this).removeClass('btn-hover');
        }
    });
    
    // 为卡片添加悬停效果
    $('.product-card, .category-card, .related-product-card').on({
        mouseenter: function() {
            $(this).addClass('card-hover');
        },
        mouseleave: function() {
            $(this).removeClass('card-hover');
        }
    });
}

// 模态框效果增强
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
    
    // 为模态框添加动画效果
    $('.modal-content').addClass('scale-in');
}

// 添加CSS类到元素
$(document).ready(function() {
    // 为产品详情页添加动画类
    $('.product-detail-container').addClass('animate-on-scroll');
    $('.product-gallery').addClass('animate-on-scroll');
    $('.product-info').addClass('animate-on-scroll');
    $('.product-details-tabs').addClass('animate-on-scroll');
    $('.related-products').addClass('animate-on-scroll');
    
    // 为产品卡片添加动画类
    $('.product-card').addClass('animate-on-scroll');
    $('.category-card').addClass('animate-on-scroll');
    
    // 为按钮添加波纹效果
    $('.btn, .btn-primary, .btn-secondary, .btn-add-to-cart, .btn-buy-now, .btn-view-details, .btn-add-cart').addClass('ripple');
    
    // 波纹效果实现
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

// 添加滚动到顶部按钮
$(window).on('scroll', function() {
    if ($(this).scrollTop() > 300) {
        if (!$('#scroll-to-top').length) {
            $('body').append('<button id="scroll-to-top" title="返回顶部"><i class="fas fa-arrow-up"></i></button>');
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

// 图片懒加载
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
        // 回退方案
        lazyImages.forEach(function(image) {
            image.src = image.dataset.src;
        });
    }
}

// 页面加载完成后执行懒加载
$(window).on('load', function() {
    lazyLoadImages();
});