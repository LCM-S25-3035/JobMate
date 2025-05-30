from typing import List, Dict, Optional
from onboarding_api.db.mongo_core import get_collection, create_new_collection
from datetime import datetime, timezone
import traceback

def get_questions_by_region(region: str) -> List[dict]:
    """
    Retrieve onboarding questions from MongoDB for the specified region.

    Args:
        region (str): Region that user selected to apply jobs.

    Returns:
        List[dict]: List of question documents.
    """
    try:
        collection = get_collection("onboarding_questions")
        if collection is None:
            raise RuntimeError("Questions collection does not exist in DB.")

        questions = list(collection.find({"region": region}))
        
        print(f"[DEBUG] Loaded {len(questions)} questions for region '{region}'")
        return questions

    except Exception as e:
        print(f"[ERROR] Exception in get_questions_by_region: {e}")
        traceback.print_exc()
        return []


def date_to_datetime(d):
    """
    Convert datetime.date to datetime.datetime (at midnight) for MongoDB compatibility.

    Args:
        d: input date object

    Returns:
        datetime.datetime or original object
    """
    try:
        # Check type properly
        import datetime as dt_mod
        if isinstance(d, dt_mod.date) and not isinstance(d, dt_mod.datetime):
            converted = dt_mod.datetime(d.year, d.month, d.day)
            print(f"[DEBUG] Converted date {d} to datetime {converted}")
            return converted
        return d
    except Exception as e:
        print(f"[ERROR] Exception in date_to_datetime: {e} with value {d}")
        traceback.print_exc()
        return d


def convert_dates_in_answers(answers: dict) -> dict:
    """
    Walk through answers dict and convert date objects to datetime.

    Args:
        answers (dict): question_id -> answer value

    Returns:
        dict: cleaned answers
    """
    try:
        for k, v in answers.items():
            answers[k] = date_to_datetime(v)
        return answers
    except Exception as e:
        print(f"[ERROR] Exception in convert_dates_in_answers: {e}")
        traceback.print_exc()
        return answers


def save_user_answers(user_id: str, region: str, answers: Dict[str, any]) -> None:
    """
    Save or update user answers to onboarding questions in MongoDB.

    Args:
        user_id (str): Unique identifier for the user.
        region (str): Region of application.
        answers (dict): Key-value pairs of question IDs and user answers.

    Returns:
        None
    """
    try:
        collection = get_collection("onboarding_user_answers")
        if collection is None:
            create_new_collection("onboarding_user_answers")
            collection = get_collection("onboarding_user_answers")

        filter_query = {"user_id": user_id, "region": region}
        print(f"[DEBUG] Saving answers for user {user_id}, region {region}: {answers}")

        answers = convert_dates_in_answers(answers)  # convert dates before saving
        update_doc = {
            "$set": {
                "answers": answers,
                "last_updated": datetime.now(timezone.utc)
            }
        }
        collection.update_one(filter_query, update_doc, upsert=True)
        print("[DEBUG] Answers saved successfully.")

    except Exception as e:
        print(f"[ERROR] Exception in save_user_answers: {e}")
        traceback.print_exc()


def load_user_answers(user_id: str, region: str) -> Optional[Dict[str, any]]:
    """
    Load previously saved user answers from MongoDB.

    Args:
        user_id (str): Unique identifier for the user.
        region (str): Region of application.

    Returns:
        dict or None: User answers if found, else None.
    """
    try:
        collection = get_collection("onboarding_user_answers")
        if collection is None:
            print("[DEBUG] User answers collection does not exist.")
            return None

        doc = collection.find_one({"user_id": user_id, "region": region})
        if not doc:
            print(f"[DEBUG] No saved answers found for user {user_id}, region {region}.")
            return None

        print(f"[DEBUG] Loaded saved answers for user {user_id}, region {region}.")
        return doc.get("answers")

    except Exception as e:
        print(f"[ERROR] Exception in load_user_answers: {e}")
        traceback.print_exc()
        return None

# Reference: 
# OpenAI 4o, first prompt:
# okay now we have mongo_client.py and onboarding_db.py .. and the data are already loaded inthe db colleciton.. what should be the next step? 
# remember that i want to split the UI into step1_questions.py and stuff and then i want to have the onboarding_flow.py where i will control the flow of the steps. 

# OpenAI 4o, last prompt:
# Getting error InvalidDocument: cannot encode object: <built-in method utcnow of type object at 0x...>
# Getting error -> AttributeError: module 'datetime' has no attribute 'utcnow'
# Getting error -> InvalidDocument: cannot encode object: datetime.date(2025, 5, 26), of type: <class 'datetime.date'>