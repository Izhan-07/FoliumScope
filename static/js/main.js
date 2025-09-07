$(document).ready(function () {
    // Initialize
    $('.image-section').hide();
    $('.loading-section').hide();
    $('#result').hide();

    // Smooth scrolling for anchor links
    $('.smooth-scroll, a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 80
            }, 800, 'swing');
        }
    });

    // Upload area click handler
    $('#uploadArea, .upload-area, .btn.btn-success.btn-lg').on('click', function() {
        $('#imageUpload').click();
    });

    // Drag and drop handlers
    $('#uploadArea').on({
        'dragover dragenter': function(e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).addClass('dragover');
        },
        'dragleave dragend drop': function(e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).removeClass('dragover');
        },
        'drop': function(e) {
            const files = e.originalEvent.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        }
    });

    // File input change handler
    $('#imageUpload').on('change', function() {
        if (this.files && this.files[0]) {
            handleFileSelect(this.files[0]);
        }
    });

    // Predict button click handler - Flask integration
    $(document).on('click', '#btn-predict', function(){
        const formData = new FormData();
        const fileInput = document.getElementById('imageUpload');

        if (!fileInput.files[0]) {
            showAlert('Please select an image first.', 'warning');
            return;
        }

        formData.append('file', fileInput.files[0]);

        // Show loading state
        showLoading();

        // Make AJAX request to Flask backend
        $.ajax({
            type: 'POST',
            url: '/predict',  // Flask endpoint
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            timeout: 30000,
            success: function(data) {
                hideLoading();
                // Check for the 'class' property first for clean results
                if (data.class) {
                    showResult(data.class, data.confidence);
                } else if (data.result) { // Fallback for other potential formats
                    showResult(data.result, data.confidence);
                } else if (typeof data === 'string') {
                    showResult(data, null);
                }
            },

            error: function(xhr, status, error) {
                hideLoading();
                let errorMessage = 'Analysis failed. Please try again.';

                if (status === 'timeout') {
                    errorMessage = 'Request timeout. Please try with a smaller image.';
                } else if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                } else if (xhr.status === 413) {
                    errorMessage = 'File too large. Please select an image under 5MB.';
                } else if (xhr.status === 500) {
                    errorMessage = 'Server error. Please try again later.';
                }

                showAlert(errorMessage, 'danger');
                console.error('Prediction error:', error);
            }
        });
    });

    // File selection handler with Flask-compatible validation
    function handleFileSelect(file) {
        // Validate file type
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!allowedTypes.includes(file.type)) {
            showAlert('Please select a valid image file (JPG, PNG, JPEG).', 'warning');
            return;
        }

        // Validate file size (5MB limit to match Flask config)
        const maxSize = 5 * 1024 * 1024; // 5MB in bytes
        if (file.size > maxSize) {
            showAlert('File size too large. Please select an image under 5MB.', 'warning');
            return;
        }

        // Read and display image
        const reader = new FileReader();
        reader.onload = function(e) {
            $('#imagePreview').css({
                'background-image': 'url(' + e.target.result + ')',
                'background-size': 'cover',
                'background-position': 'center'
            });

            // Show image preview section with animation
            $('.image-section').fadeIn(500);
            $('#btn-predict').show();

            // Hide previous results
            $('#result').fadeOut(300);
            $('.loading-section').hide();
        };
        reader.readAsDataURL(file);
    }

    // Show loading state
    function showLoading() {
        $('#btn-predict').hide();
        $('.loading-section').fadeIn(300);
        $('#result').fadeOut(300);
    }

    // Hide loading state
    function hideLoading() {
        $('.loading-section').fadeOut(300);
        $('#btn-predict').fadeIn(300);
    }

    // Show result with Flask response handling
    function showResult(result, confidence) {
        let resultText = result || 'Unknown';

        // Color code the result based on disease classification
        const $resultText = $('#result-text');
        const $resultIcon = $('.result-header i');

        if (resultText.toLowerCase().includes('healthy')) {
            $resultText.removeClass('text-warning text-danger').addClass('text-success');
            $resultIcon.removeClass('fa-exclamation-triangle fa-times-circle').addClass('fa-check-circle text-success');
            $('.result-info').removeClass('bg-warning bg-danger').addClass('bg-light border-success');
        } else if (resultText.toLowerCase() === 'unknown' || !resultText) {
            $resultText.removeClass('text-success text-danger').addClass('text-warning');
            $resultIcon.removeClass('fa-check-circle fa-times-circle').addClass('fa-exclamation-triangle text-warning');
            $('.result-info').removeClass('bg-light bg-danger border-success').addClass('bg-warning');
        } else {
            // Disease detected
            $resultText.removeClass('text-success text-warning text-danger').addClass('text-white');
            // Always show check icon, never X
            $resultIcon.removeClass('fa-exclamation-triangle fa-times-circle').addClass('fa-check-circle text-success');
            $('.result-info').removeClass('bg-light bg-warning border-success').addClass('bg-danger');
        }

        // Always show both class and confidence
        let html = '';
        if (resultText && resultText !== 'Unknown') {
            html += `<span>Disease: <b>${resultText}</b></span><br>`;
        }
        if (confidence !== undefined && confidence !== null) {
            html += `<span class="text-muted">Confidence: ${confidence}%</span>`;
        }
        $resultText.html(html);

        $('#result').fadeIn(500);

        // Scroll to results
        setTimeout(() => {
            $('html, body').animate({
                scrollTop: $('#result').offset().top - 100
            }, 500);
        }, 200);
    }
    // ...existing code...

    // Show alert message
    function showAlert(message, type = 'info') {
        // Remove existing alerts
        $('.alert').remove();

        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show mt-3" role="alert">
                <i class="fas fa-${getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;

        $('.upload-container').prepend(alertHtml);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            $('.alert').fadeOut();
        }, 5000);
    }

    // Get alert icon based on type
    function getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Navbar scroll effect
    $(window).scroll(function() {
        if ($(this).scrollTop() > 50) {
            $('.navbar').addClass('shadow-sm').css('background-color', 'rgba(255, 255, 255, 0.95)');
        } else {
            $('.navbar').removeClass('shadow-sm').css('background-color', 'rgba(255, 255, 255, 1)');
        }
    });

    // Add loading animation to buttons
    $('a[href^="#"]').on('click', function() {
        const $btn = $(this);
        if ($btn.hasClass('btn')) {
            $btn.addClass('disabled');
            setTimeout(() => $btn.removeClass('disabled'), 800);
        }
    });

    // Health check endpoint for debugging
    function checkServerHealth() {
        $.get('/health')
            .done(function(data) {
                console.log('Server health:', data);
            })
            .fail(function() {
                console.warn('Health check failed');
            });
    }

    // Check server health on load
    checkServerHealth();
});

// Global function to reset upload (called from HTML)
function resetUpload() {
    $('#imageUpload').val('');
    $('.image-section').fadeOut(300);
    $('#result').fadeOut(300);
    $('.loading-section').hide();
    $('.alert').fadeOut();

    // Reset upload area
    $('#uploadArea').removeClass('dragover');
    $('#imagePreview').css('background-image', '');

    // Reset result styling
    $('.result-info').removeClass('bg-warning bg-danger border-success').addClass('bg-light');
}

// Accessibility: Keyboard navigation for upload area
$(document).on('keydown', '#uploadArea', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        $('#imageUpload').click();
    }
});

// Flask-specific error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});