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
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        .question-item { margin-bottom: 30px; page-break-inside: avoid; }
                        .card-header { background: #007bff; color: white; padding: 10px; font-weight: bold; }
                        .card-body { padding: 15px; border: 1px solid #ddd; }
                        .question-text, .answer-text, .evaluation-text { 
                            padding: 10px; 
                            background: #f8f9fa; 
                            border-left: 4px solid #007bff; 
                            margin: 10px 0;
                        }
                        .code-container { 
                            background: #f8f9fa; 
                            padding: 10px; 
                            border: 1px solid #ddd; 
                            font-family: monospace;
                        }
                        h6 { color: #495057; font-weight: bold; margin-top: 15px; }
                        @media print {
                            .copy-btn { display: none; }
                            .question-item { page-break-inside: avoid; }
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
        button.style.right = '10px';
    });

    // Print functionality
    window.printQuestions = function() {
        const questionsContent = document.querySelector('.questions-display');
        if (questionsContent) {
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <html>
                    <head>
                        <title>Interview Questions</title>
                        <style>
                            body { font-family: Arial, sans-serif; margin: 20px; }
                            h1, h2, h3 { color: #333; }
                            pre { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                            .copy-btn { display: none; }
                        </style>
                    </head>
                    <body>
                        <h1>Interview Questions</h1>
                        ${questionsContent.innerHTML}
                    </body>
                </html>
            `);
            printWindow.document.close();
            printWindow.print();
        }
    };
});

console.log('Questions.js loaded successfully');
