$(document).ready(function() {
    // Function to open the modal
    $('#openModalBtn').on('click', function() {
        $('#myModal').removeClass('hidden');
    });

    // Function to close the modal
    $('#closeModalBtn').on('click', function() {
        $('#myModal').addClass('hidden');
    });

    // Close the modal if the user clicks outside of it
    $(window).on('click', function(event) {
        if (event.target === $('#myModal')[0]) {
            $('#myModal').addClass('hidden');
        }
    });
});
