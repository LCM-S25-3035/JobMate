import pandas as pd
import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_job_description_for_llm(text):
    """Cleans a job description for LLM parsing by removing bullets, special characters, and fixing formatting."""
    if pd.isna(text):
        return ""

    # Remove common bullet characters and list symbols
    text = re.sub(r'^\s*[-*•]+\s*', '', text, flags=re.MULTILINE)

    # Remove special formatting characters (e.g., asterisks, quotes)
    text = re.sub(r'[*"“”<>]', '', text)

   # Limpiar espacios extra
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove excess blank lines
    text = re.sub(r'\n{3,}', '\n', text)

    # Strip spaces on each line and join
    lines = [line.strip() for line in text.split('\n')]
    cleaned = "\n".join(lines)

    return cleaned.strip()


def clean_data(df):
    """Performs general data cleaning."""
    # Drop columns that are completely empty (all NaN)
    df.dropna(axis=1, how='all', inplace=True)
    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # Trim leading/trailing whitespace and replace empty strings with pd.NA
    for col in df.select_dtypes(include=['object']).columns:
        # Trim whitespace
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        # Replace empty strings with pd.NA
        df[col].replace('', pd.NA, inplace=True)

    # Drop rows that are completely empty (all columns are NaN)
    blank_rows = df.isna().all(axis=1)
    df = df[~blank_rows]

    # Clean the job_description column (if present) for LLM parsing
    if 'job_description' in df.columns:
        logging.info("Cleaning job_description column for LLM parsing...")
        df['Job Description'] = df['Job Description'].apply(clean_job_description_for_llm)

    return df


def main():
    try:
        df1 = pd.read_csv("src/data_gathering/Jobs-Data_Scraped.csv")
        df2 = pd.read_csv("src/data_gathering/JobSpy_scraped_jobs.csv")
    except FileNotFoundError as e:
        logging.error(f"Missing file: {e}")
        return

    logging.info("Combining datasets...")
    combined_df = pd.concat([df1, df2], ignore_index=True)

    logging.info("Cleaning data...")
    cleaned_df = clean_data(combined_df)

    output_file = os.path.join("src", "data_gathering", "Jobs-Data_Cleaned.csv")
    cleaned_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    logging.info(f"Cleaned data saved to: {output_file}")


if __name__ == "__main__":
    main()
