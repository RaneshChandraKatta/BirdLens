// Quick frontend validation and interactions using jQuery
$(document).ready(function() {
    // Show loading UI on image upload submit
    $('#uploadForm').on('submit', function() {
        if ($('#image_upload').val()) {
            $('#predictBtn').prop('disabled', true).text('Uploading...');
            $('#loadingIndicator').fadeIn();
        }
    });

    // Form validation enhancements
    $('#registerForm').on('submit', function(e) {
        var pw = $('#password').val();
        if (pw.length < 6) {
            e.preventDefault(); // Prevent submission
            $('#password').addClass('is-invalid');
            $('#pwFeedback').show();
        } else {
            $('#password').removeClass('is-invalid');
            $('#pwFeedback').hide();
        }
    });

    $('#loginForm').on('submit', function(e) {
        if (!$('#username').val().trim()) {
            e.preventDefault();
            $('#username').addClass('is-invalid');
        } else {
            $('#username').removeClass('is-invalid');
        }
    });

    // Clear invalid class on keyup
    $('input').on('keyup', function() {
        $(this).removeClass('is-invalid');
    });

    // Auto dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
});
