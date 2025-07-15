/**
 * Job Description Enhancement Script
 * This script improves job description formatting
 */

document.addEventListener('DOMContentLoaded', function() {
    // Parse and enhance job description
    enhanceJobDescription();
    
    // Format requirements as bullet points
    formatRequirements();
    
    // Setup toggle button manually
    setupToggleButton();
});

/**
 * Enhances the job description by identifying and formatting key sections
 */
function enhanceJobDescription() {
    const description = document.querySelector('.formatted-description');
    if (!description) return;
    
    // Keywords that likely indicate section headers
    const sectionKeywords = [
        'Responsibilities', 'Requirements', 'Qualifications',
        'Skills', 'Experience', 'About', 'Benefits',
        'Education', 'Duties', 'Role', 'Position', 'Overview'
    ];
    
    // Extract text content and format it
    const content = description.textContent;
    
    // If the description doesn't have the special ** formatting, try to identify sections
    if (!content.includes('**')) {
        const paragraphs = Array.from(description.querySelectorAll('p'));
        
        paragraphs.forEach(p => {
            const text = p.textContent.trim();
            
            // Check if paragraph starts with a keyword
            for (const keyword of sectionKeywords) {
                if (text.startsWith(keyword + ':') || text === keyword) {
                    p.classList.add('section-title');
                    p.innerHTML = `<strong>${text}</strong>`;
                    return;
                }
            }
            
            // Look for lines that might be bullet points
            if (text.startsWith('•') || text.startsWith('-') || text.startsWith('*')) {
                p.style.paddingLeft = '1rem';
                p.style.position = 'relative';
                p.innerHTML = `<span style="position: absolute; left: 0;">${text.charAt(0)}</span> ${text.substring(1)}`;
            }
        });
    }
}

/**
 * Formats the requirements section as bullet points if needed
 */
function formatRequirements() {
    const requirementsList = document.querySelector('.requirements-list');
    if (!requirementsList) return;
    
    const listItems = requirementsList.querySelectorAll('li');
    if (listItems.length === 0) {
        // If no list items, try to create them from text
        const text = requirementsList.textContent;
        const lines = text.split('\n').filter(line => line.trim());
        
        if (lines.length > 0) {
            requirementsList.innerHTML = '';
            lines.forEach(line => {
                const li = document.createElement('li');
                li.textContent = line.trim().replace(/^[•\-*]\s*/, '');
                requirementsList.appendChild(li);
            });
        }
    }
}

/**
 * Sets up the toggle button for job details with proper state management
 */
function setupToggleButton() {
    // Get toggle button and collapsible element
    const toggleBtn = document.querySelector('[data-bs-toggle="collapse"][data-bs-target="#jobDetailsCollapse"]');
    const collapseElement = document.getElementById('jobDetailsCollapse');
    
    if (!toggleBtn || !collapseElement) return;
    
    // Initialize the button text based on current state
    updateToggleButtonText();
    
    // Use Bootstrap's collapse events to update the button text
    collapseElement.addEventListener('shown.bs.collapse', updateToggleButtonText);
    collapseElement.addEventListener('hidden.bs.collapse', updateToggleButtonText);
    
    // If Bootstrap is not initializing the collapse properly, initialize it manually
    if (typeof bootstrap !== 'undefined') {
        new bootstrap.Collapse(collapseElement, {toggle: false});
    } else {
        // Fallback if Bootstrap JavaScript is not available
        toggleBtn.addEventListener('click', function() {
            const isCollapsed = !collapseElement.classList.contains('show');
            if (isCollapsed) {
                collapseElement.classList.add('show');
            } else {
                collapseElement.classList.remove('show');
            }
            updateToggleButtonText();
        });
    }
    
    function updateToggleButtonText() {
        const isCollapsed = !collapseElement.classList.contains('show');
        toggleBtn.innerHTML = isCollapsed ? 
            '<i class="fas fa-plus-circle me-1"></i> Show Details' : 
            '<i class="fas fa-minus-circle me-1"></i> Hide Details';
    }
}
