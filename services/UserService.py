import csv
import io
from infra.s3 import get_csv_from_s3, upload_csv_to_s3

def update_user_preferences(user_id, preferences):
    bucket_name = 'claco-bucket'
    folder_name = 'datasets'
    user_file = 'users.csv'

    # 한국어에서 영어로 변환하는 매핑
    preference_mapping = {
        "웅장한": "grand",
        "섬세한": "delicate",
        "고전적인": "classical",
        "현대적인": "modern",
        "서정적인": "lyrical",
        "역동적인": "dynamic",
        "낭만적인": "romantic",
        "비극적인": "tragic",
        "친숙한": "familiar",
        "새로운": "novel"
    }

    # Fetch the CSV data from S3
    csv_data = get_csv_from_s3(bucket_name, folder_name, user_file)
    if csv_data is None:
        print("User CSV file not found in S3.")
        return {"error": "User CSV file not found"}

    updated_rows = []
    user_found = False

    # Append all existing rows from the CSV data
    for row in csv_data:
        updated_rows.append(row)
        
        # Check if the user already exists in the CSV
        if row['userId'] == user_id:
            user_found = True

    # Convert preferences from Korean to English
    converted_preferences = [preference_mapping[pref] for pref in preferences if pref in preference_mapping]

    # Create a new row for the user with the specified preferences
    new_row = {'userId': user_id}
    for field in csv_data[0].keys():
        if field == 'userId':
            new_row[field] = user_id
        elif field in converted_preferences:
            new_row[field] = '1'  # Set specified preferences to '1'
        else:
            new_row[field] = '0'  # Set all other fields to '0'
            
    # Append the new row at the end
    updated_rows.append(new_row)

    # Write the updated data back to a new CSV file in memory
    output = io.StringIO()
    fieldnames = csv_data[0].keys()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(updated_rows)
    output.seek(0)

    # Upload the updated CSV back to S3
    upload_csv_to_s3(bucket_name, folder_name, user_file, output.getvalue())

    return {"message": f"Preferences updated successfully for user {user_id}"}
