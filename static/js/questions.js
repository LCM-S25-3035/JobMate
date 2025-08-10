// Questions.js - JavaScript for Interview Questions functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Add loading state to form submission
    const forms = document.querySelectorAll('.questions-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating Questions...';
            }
        });
    });

    // Add smooth scroll to generated questions
    const questionsDisplay = document.querySelector('.questions-display');
    if (questionsDisplay) {
        questionsDisplay.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Initialize syntax highlighting if Prism is available
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
});

// Copy code functionality
function copyCode(button) {
    const codeContainer = button.closest('.code-container');
    const codeElement = codeContainer.querySelector('code');
    
    if (codeElement) {
        const textToCopy = codeElement.textContent;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            // Show success state
            const originalContent = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check text-success"></i>';
            button.classList.add('btn-success');
            button.classList.remove('btn-outline-secondary');
            
            // Reset after 2 seconds
            setTimeout(() => {
                button.innerHTML = originalContent;
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-secondary');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            // Fallback for older browsers
            fallbackCopyTextToClipboard(textToCopy, button);
        });
    }
}

// Fallback copy function for older browsers
function fallbackCopyTextToClipboard(text, button) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    
    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            // Show success state
            const originalContent = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check text-success"></i>';
            button.classList.add('btn-success');
            button.classList.remove('btn-outline-secondary');
            
            setTimeout(() => {
                button.innerHTML = originalContent;
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-secondary');
            }, 2000);
        }
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }
    
    document.body.removeChild(textArea);
}

// Print questions functionality
function printQuestions() {
    const questionsContent = document.querySelector('.questions-display');
    if (questionsContent) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Interview Questions</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; color: #111; }
                        h1 { font-size: 22px; margin-bottom: 12px; }
                        .question-card { margin-bottom: 18px; padding: 12px; border-radius: 8px; border: 1px solid #e9ecef; background: #fff; }
                        .section-question { background-color: #e7f3ff; border-left: 5px solid #0d6efd; padding: 10px; border-radius: 6px; color: #052c65; }
                        .section-relevance { background-color: #fff7e6; border-left: 5px solid #ffc107; padding: 10px; border-radius: 6px; color: #4b3b00; margin-top:8px; }
                        .section-expected { background-color: #e9f7ef; border-left: 5px solid #28a745; padding: 10px; border-radius: 6px; color: #073b22; margin-top:8px; }
                        .section-code { background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 10px; border-radius: 6px; color: #343a40; margin-top:8px; }
                        pre { background: #1e1e1e; color: #d4d4d4; padding: 10px; border-radius: 6px; overflow:auto; }
                        @media print {
                            body { margin: 8mm; }
                            pre { page-break-inside: avoid; }
                        }
                    </style>
                </head>
                <body>
                    ${questionsContent.innerHTML}
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

console.log('Questions.js loaded successfully');
