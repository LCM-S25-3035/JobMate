// MongoDB setup for Jobs faceting functionality
// Run this script in MongoDB shell or MongoDB Compass

// Create text indexes for search functionality
db.jobs.createIndex({
    "title": "text",
    "description": "text", 
    "company": "text",
    "skills": "text",
    "requirements": "text"
});

// Create additional indexes for filtering performance
db.jobs.createIndex({ "location": 1 });
db.jobs.createIndex({ "job_type": 1 });
db.jobs.createIndex({ "experience_level": 1 });
db.jobs.createIndex({ "company": 1 });
db.jobs.createIndex({ "salary_min": 1, "salary_max": 1 });
db.jobs.createIndex({ "salary": 1 });
db.jobs.createIndex({ "date_posted": -1 });
db.jobs.createIndex({ "status": 1 });

// Compound indexes for common filter combinations
db.jobs.createIndex({ "location": 1, "job_type": 1 });
db.jobs.createIndex({ "company": 1, "date_posted": -1 });
db.jobs.createIndex({ "experience_level": 1, "salary_min": 1 });

// Index for saved jobs functionality
db.saved_jobs.createIndex({ "user_id": 1, "job_id": 1 }, { unique: true });
db.saved_jobs.createIndex({ "user_id": 1, "saved_at": -1 });

// Index for tailored resumes (application tracking)
db.tailored_resumes.createIndex({ "user_id": 1, "job_id": 1 }, { unique: true });
db.tailored_resumes.createIndex({ "user_id": 1 });

console.log("✅ MongoDB indexes created successfully for Jobs faceting functionality");
console.log("📊 Use db.jobs.getIndexes() to verify indexes");
