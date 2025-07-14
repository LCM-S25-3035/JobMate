/**
 * Ensure Bootstrap 5 Collapse functionality works correctly
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all collapse elements on the page
  var collapseElementList = [].slice.call(document.querySelectorAll('.collapse'));
  collapseElementList.forEach(function(collapseEl) {
    // Check if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
      new bootstrap.Collapse(collapseEl, {
        toggle: collapseEl.classList.contains('show')
      });
    }
  });
});
