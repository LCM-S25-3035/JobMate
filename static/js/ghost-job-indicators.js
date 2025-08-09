/**
 * Ghost Job Indicator JavaScript
 * Handles the display and interaction for ghost job indicators
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all ghost job indicators
    const indicators = document.querySelectorAll('.ghost-job-indicator');
    if (indicators.length === 0) return;
    
    // Add tooltips and event handlers to ghost job badges
    const badges = document.querySelectorAll('.ghost-job-badge');
    badges.forEach(function(badge) {
        // Get job ID and percentage
        const jobId = badge.getAttribute('data-job-id');
        const percentage = badge.getAttribute('data-percentage');
        
        // Add click handler for tooltip
        badge.addEventListener('click', function() {
            showGhostJobInfo(jobId, percentage);
        });
    });
});

/**
 * Show ghost job information tooltip
 * @param {string} jobId - The ID of the job
 * @param {string} percentage - The ghost job percentage
 */
function showGhostJobInfo(jobId, percentage) {
    // Get risk level based on percentage
    let riskLevel = 'Low';
    if (percentage >= 70) {
        riskLevel = 'High';
    } else if (percentage >= 40) {
        riskLevel = 'Medium';
    }
    
    // Show alert for now - in future this could be a proper tooltip
    alert(`Ghost Job Warning\n\nThis job posting has a ${percentage}% likelihood of being a "ghost job".\n\nRisk Level: ${riskLevel}\n\nGhost jobs are postings that may not represent real hiring opportunities.`);
}
