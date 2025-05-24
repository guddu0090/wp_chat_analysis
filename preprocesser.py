import re
from re import split
import pandas as pd


def preprocess(data):
    pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Clean and parse datetime
    df["message_date"] = df["message_date"].str.replace(r"\s*-\s*$", "", regex=True).str.strip()
    df["message_date"] = pd.to_datetime(df["message_date"], format="%d/%m/%y, %H:%M", dayfirst=True, errors="coerce")

    # Rename and add backup column
    df.rename(columns={"message_date": "date"}, inplace=True)
    df["message_date"] = df["date"]  # for helper.py compatibility

    # Parse user and message
    users = []
    messages = []
    for message in df['user_message']:
        entry = split('([\w\W]+?):\s', message)
        if len(entry) >= 3:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(entry[0])
    df['user'] = users
    df['message'] = messages

    # Drop intermediate
    df.drop(columns=["user_message"], inplace=True)

    # Add date components
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['only_date'] = df['date'].dt.date
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    return df
