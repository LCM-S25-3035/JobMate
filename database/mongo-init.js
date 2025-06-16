// JobMate MongoDB Initialization Script
// This script sets up the MongoDB database with initial collections and indexes

// Switch to the JobMate database
db = db.getSiblingDB('jobmate_mongo');

// Create collections with validation schemas
db.createCollection("job_postings", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["title", "company", "location", "description", "created_at"],
         properties: {
            title: {
               bsonType: "string",
               description: "Job title must be a string and is required"
            },
            company: {
               bsonType: "string",
               description: "Company name must be a string and is required"
            },
            location: {
               bsonType: "string",
               description: "Location must be a string and is required"
            },
            description: {
               bsonType: "string",
               description: "Job description must be a string and is required"
            },
            created_at: {
               bsonType: "date",
               description: "Creation date must be a date and is required"
            }
         }
      }
   }
});

db.createCollection("parsed_resumes", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["user_id", "content", "parsed_data", "created_at"],
         properties: {
            user_id: {
               bsonType: "int",
               description: "User ID must be an integer and is required"
            },
            content: {
               bsonType: "string",
               description: "Resume content must be a string and is required"
            },
            parsed_data: {
               bsonType: "object",
               description: "Parsed data must be an object and is required"
            },
            created_at: {
               bsonType: "date",
               description: "Creation date must be a date and is required"
            }
         }
      }
   }
});

db.createCollection("ai_analysis", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["analysis_type", "input_data", "result", "created_at"],
         properties: {
            analysis_type: {
               bsonType: "string",
               enum: ["resume_parsing", "job_analysis", "match_scoring", "tailoring", "ghost_detection"],
               description: "Analysis type must be one of the enum values"
            }
         }
      }
   }
});

// Create indexes for better performance
db.job_postings.createIndex({ "title": "text", "description": "text", "company": "text" });
db.job_postings.createIndex({ "location": 1 });
db.job_postings.createIndex({ "created_at": -1 });
db.job_postings.createIndex({ "company": 1 });
db.job_postings.createIndex({ "source": 1 });

db.parsed_resumes.createIndex({ "user_id": 1 });
db.parsed_resumes.createIndex({ "created_at": -1 });
db.parsed_resumes.createIndex({ "skills": 1 });

db.ai_analysis.createIndex({ "analysis_type": 1 });
db.ai_analysis.createIndex({ "created_at": -1 });
db.ai_analysis.createIndex({ "user_id": 1 });

// Create initial admin user settings collection
db.createCollection("app_settings");
db.app_settings.insertOne({
   _id: "global_settings",
   ai_features_enabled: true,
   job_scraping_enabled: true,
   auto_apply_enabled: true,
   max_applications_per_day: 50,
   created_at: new Date(),
   updated_at: new Date()
});

// Create job sources configuration
db.createCollection("job_sources");
db.job_sources.insertMany([
   {
      name: "LinkedIn",
      url: "https://linkedin.com/jobs",
      enabled: true,
      scraping_config: {
         rate_limit: 60,
         selectors: {
            job_title: ".job-title",
            company: ".company-name",
            location: ".job-location"
         }
      },
      created_at: new Date()
   },
   {
      name: "Indeed",
      url: "https://indeed.ca",
      enabled: true,
      scraping_config: {
         rate_limit: 30,
         selectors: {
            job_title: ".jobTitle",
            company: ".companyName",
            location: ".companyLocation"
         }
      },
      created_at: new Date()
   },
   {
      name: "Glassdoor",
      url: "https://glassdoor.ca",
      enabled: true,
      scraping_config: {
         rate_limit: 45,
         selectors: {
            job_title: ".JobsListItem-title",
            company: ".EmployerProfile_companyContainer",
            location: ".JobsListItem-loc"
         }
      },
      created_at: new Date()
   }
]);

// Create logs collection for application monitoring
db.createCollection("application_logs");
db.application_logs.createIndex({ "timestamp": -1 });
db.application_logs.createIndex({ "level": 1 });
db.application_logs.createIndex({ "user_id": 1 });

print("JobMate MongoDB initialization completed successfully!");
print("Created collections: job_postings, parsed_resumes, ai_analysis, app_settings, job_sources, application_logs");
print("Created indexes for optimal performance");
print("Inserted initial configuration data"); 