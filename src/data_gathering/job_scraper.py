# backend/services/job_scraper.py

from jobspy import scrape_jobs
from datetime import datetime
from backend.database import db
import pandas as pd
import logging

async def scrape_and_store_data_jobs(days_back=3, limit_per_location=50):
    try:
        logging.info("🔍 Scraping data-related jobs (full-time, part-time, remote) for Canada and USA...")

        common_params = {
            "site_name": ["linkedin", "indeed"],
            "search_term": "data",
            "results_wanted": limit_per_location,
            "hours_old": days_back * 24,
            "linkedin_job_type": ["F", "P"],  # F = Full-time, P = Part-time
            "linkedin_work_type": ["Remote", "Hybrid", "OnSite"],
        }

        # Scrape jobs from Canada
        jobs_df_canada = scrape_jobs(
            **common_params,
            location="canada",
            country_indeed="canada"
        )

        # Scrape jobs from USA
        jobs_df_usa = scrape_jobs(
            **common_params,
            location="usa",
            country_indeed="usa"
        )

        # Combine the results
        combined_df = pd.concat([jobs_df_canada, jobs_df_usa], ignore_index=True)

        # Add timestamp
        combined_df["scraped_at"] = datetime.utcnow()

        # Define only the datetime columns you expect
        datetime_cols = ['date_posted', 'scraped_at']

        # Convert these columns to datetime
        for col in datetime_cols:
            if col in combined_df.columns:
                combined_df[col] = pd.to_datetime(combined_df[col], errors='coerce')

        # Optional debug logging
        for col in datetime_cols:
            if col in combined_df.columns and combined_df[col].isna().any():
                logging.warning(f"⚠️ Found NaT values in datetime column '{col}' before dropping.")

        # Drop rows with NaT in critical datetime columns
        combined_df = combined_df.dropna(subset=datetime_cols)

        # Replace any remaining NaN/NaT with None for MongoDB compatibility
        combined_df = combined_df.where(pd.notnull(combined_df), None)

        # Convert to dict records
        jobs = combined_df.to_dict("records")

        inserted_count = 0
        for job in jobs:
            try:
                await db["jobs"].insert_one(job)
                inserted_count += 1
            except Exception as e:
                logging.warning(f"⚠️ Skipping job due to DB error: {e}")

        logging.info(f"✅ Inserted {inserted_count}/{len(jobs)} jobs.")
        return {"message": "Scraping completed", "inserted": inserted_count, "total": len(jobs)}

    except Exception as e:
        logging.error(f"❌ Scraping failed: {e}")
        return {"error": str(e)}