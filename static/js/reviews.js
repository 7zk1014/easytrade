// Reviews functionality
$(document).ready(function() {
    // Initialize star rating
    initStarRating();
    
    // Initialize review tabs
    initReviewTabs();
});

function initStarRating() {
    // Convert select dropdown to visual star rating
    if ($('#id_rating').length) {
        const ratingSelect = $('#id_rating');
        const starContainer = $('<div class="visual-stars"></div>');
        
        // Create visual stars
        for (let i = 1; i <= 5; i++) {
            const star = $(`<i class="far fa-star" data-rating="${i}"></i>`);
            starContainer.append(star);
        }
        
        // Insert stars before the select
        ratingSelect.before(starContainer);
        
        // Hide the original select
        ratingSelect.hide();
        
        // Set initial stars based on selected value
        updateStars(parseInt(ratingSelect.val()) || 0);
        
        // Handle star click
        starContainer.find('i').on('click', function() {
            const rating = $(this).data('rating');
            ratingSelect.val(rating);
            updateStars(rating);
        });
        
        // Handle star hover
        starContainer.find('i').on('mouseenter', function() {
            const rating = $(this).data('rating');
            previewStars(rating);
        });
        
        starContainer.on('mouseleave', function() {
            updateStars(parseInt(ratingSelect.val()) || 0);
        });
    }
}

function updateStars(rating) {
    $('.visual-stars i').each(function(index) {
        if (index < rating) {
            $(this).removeClass('far').addClass('fas');
        } else {
            $(this).removeClass('fas').addClass('far');
        }
    });
}

function previewStars(rating) {
    $('.visual-stars i').each(function(index) {
        if (index < rating) {
            $(this).removeClass('far').addClass('fas');
        } else {
            $(this).removeClass('fas').addClass('far');
        }
    });
}

function initReviewTabs() {
    // Handle review tab click in product detail page
    $('.tab-btn[data-tab="reviews"]').on('click', function() {
        $('.tab-btn').removeClass('active');
        $(this).addClass('active');
        $('.tab-pane').removeClass('active');
        $('#reviews').addClass('active');
    });
}