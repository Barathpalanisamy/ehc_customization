document.addEventListener('DOMContentLoaded', function() {
    // Create a MutationObserver to observe changes in the DOM
    var observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                // Check if the added node has the class "notification-item"
                if (node.nodeType === 1 && node.classList.contains('notification-item')) {
                    // Attach a click event listener to the added node
                    node.addEventListener('click', function(event) {
                        event.preventDefault();
                        // Get the href attribute of the clicked element
                        var href = this.getAttribute('href');
                        if (href.includes('app/job-opening')) {
                            href = href.replace('app/job-opening/', 'internal_job?job=');
                        }
                        // window.location.href = href;
                        window.open(href)
                    });
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
