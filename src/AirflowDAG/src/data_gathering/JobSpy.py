import os
import csv
import pandas as pd
from jobspy import scrape_jobs
import time




# ---------- CONFIG ---------- #
KEYWORDS_PATH = "src/data_gathering/keywords.txt"
LOCATIONS_PATH = "src/data_gathering/providence.txt"
OUTPUT_DIR = "src/data_gathering/jobspy_outputs"
FINAL_OUTPUT = "src/data_gathering/JobSpy_scraped_jobs.csv"
CRITERIA_COLUMNS = ["location", "title", "company", "job_type"]
# ---------------------------- #

def load_list_from_file(file_path):
    items = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                item = line.strip()
                if item:
                    items.append(item)
        print(f"✅ Loaded {len(items)} items from {file_path}")
    except FileNotFoundError:
        print(f"⚠️ File not found: {file_path}")
    return items

def run_jobspy_scraper(keywords, locations):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for keyword in keywords:
        for location in locations:
            print(f"🔍 Scraping: {keyword} in {location}")
            jobs = scrape_jobs(
                site_name=["zip_recruiter", "google"],
                search_term=keyword,
                google_search_term=f"{keyword} jobs near {location} since yesterday",
                location=location,
                results_wanted=20000,
                hours_old=720,
                country_indeed="Canada"
            )
            jobs["Provincia"] = location.split(",")[0]
            jobs["Keyword"] = keyword
            print(f"📝 Found {len(jobs)} jobs")

            output_file = os.path.join(OUTPUT_DIR, f"{keyword}_{location}.csv")
            jobs.to_csv(output_file, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
            print(f"✅ Saved to {output_file}")

def load_and_clean_csv_files(folder_path):
    df_list = []
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            if os.path.getsize(file_path) > 0:
                try:
                    df = pd.read_csv(file_path)
                    if not df.empty:
                        df_list.append(df)
                except pd.errors.EmptyDataError:
                    print(f"⚠️ Skipping empty file: {file}")
                except pd.errors.ParserError:
                    print(f"⚠️ Skipping corrupt file: {file}")

    if not df_list:
        print("❌ No valid CSV files found.")
        return pd.DataFrame()

    df = pd.concat(df_list, ignore_index=True)
    print(f"📦 Loaded total {len(df)} rows")

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=CRITERIA_COLUMNS, keep='first')
    after = len(df)
    print(f"🧹 Removed {before - after} duplicate rows")

    return df

def finalize_dataframe(df, output_file):
    selected = df[['title', 'company', 'location', 'salary_source', 'date_posted', 'description', 'job_url', 'Provincia', 'Keyword']]
    selected.rename(columns={
        'title': 'Job Title',
        'company': 'Company Name',
        'location': 'Location',
        'salary_source': 'Salary',
        'date_posted': 'Posted Day',
        'description': 'Job Description',
        'job_url': 'job url'
    }, inplace=True)

    selected.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ Final dataset saved: {output_file}")
    print(selected.head())

if __name__ == "__main__":
    start_time = time.time()
    # Step 1: Load input
    keywords = load_list_from_file(KEYWORDS_PATH)
    locations = load_list_from_file(LOCATIONS_PATH)

    # Step 2: Scrape jobs
    run_jobspy_scraper(keywords, locations)

    # Step 3: Load, clean, and save final data
    final_df = load_and_clean_csv_files(OUTPUT_DIR)
    if not final_df.empty:
        finalize_dataframe(final_df, FINAL_OUTPUT)
    
    tend_time = time.time()
    elapsed_time = tend_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds")
