
import time
# Opens the Chrome browser
from selenium import webdriver
import json
import pandas as pd
from sqlalchemy import create_engine
from pandas.io import sql
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from fuzzywuzzy import fuzz, process

from bs4 import BeautifulSoup
import re

#drop table:
from sqlalchemy import create_engine, MetaData, Table


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


engine = create_engine("postgresql://postgres:postgres@localhost:5432/ipl25")

#code to drop the table first and then add them again
# Table to drop
TABLE_batting = "masterbattingdf"
TABLE_bowling = "masterbowlingdf"

# Create metadata object
metadata = MetaData()

#batting
try:
    # Reflect the table from the database
    table = Table(TABLE_batting, metadata, autoload_with=engine)

    # Drop the table
    table.drop(engine, checkfirst=True)  # checkfirst=True ensures it doesn't fail if the table doesn't exist
    print(f"Table '{TABLE_batting}' dropped successfully!")

except Exception as e:
    print(f"Error: {e}")

#Bowling
try:
    # Reflect the table from the database
    table = Table(TABLE_bowling, metadata, autoload_with=engine)

    # Drop the table
    table.drop(engine, checkfirst=True)  # checkfirst=True ensures it doesn't fail if the table doesn't exist
    print(f"Table '{TABLE_bowling}' dropped successfully!")

except Exception as e:
    print(f"Error: {e}")

options = webdriver.ChromeOptions()
browser = webdriver.Chrome(options=options)

wait = WebDriverWait(browser, 30)

browser.get("https://www.espncricinfo.com/series/ipl-2025-1449924/match-schedule-fixtures-and-results")

html = browser.page_source

soup = BeautifulSoup(html, 'html.parser')

div = soup.find('div', class_='ds-mb-4')
links = div.find_all("a")

matchlinks = []


def g(x):
    runout = r'run out'
    notout = r'not out'
    bname = r' b (.*)'
    if re.search(runout, x['wkt']):
        return ""
    elif re.search(notout, x['wkt']):
        return ""
    else:
        return re.search(bname, x['wkt']).group(1)


def find_best_match(name, names_to_match, threshold=50):
    best_match = process.extractOne(name, names_to_match, scorer=fuzz.token_sort_ratio, score_cutoff=threshold)
    return best_match[0] if best_match is not None else None


for link in links:
    href = link.get('href')
    if href != "/series/ipl-2025-1449924":
        matchlinks.append(href)
scorecard_links = [link for link in matchlinks if link.endswith('full-scorecard')]
start_match_number = 1
end_match_number = 3

masterbattingdf = pd.DataFrame()
masterbowlingdf = pd.DataFrame()

for match in range(start_match_number-1, end_match_number):
    browser.get("https://www.espncricinfo.com" + scorecard_links[match])
# removing delay - time.sleep(5)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    tables = soup.find_all("table")
    t = tables[0]

    data = []
    for row in t.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            row_data.append(cell.text)
        data.append(row_data)



    df = pd.DataFrame(data)
    df = df.dropna()
    columns = ["player", "wkt", "runs", "balls", "mins", "fours", "sixes", "strikerate"]
#   print(df.head())
    df.columns = columns
    df.player = df.player.str.replace(r' (c)', '')
    df.player = df.player.str.replace(r'†', '')
    df['player'] = df['player'].str.strip()
    df.wkt = df.wkt.str.replace(r'†', '')
    df.wkt = df.wkt.str.replace(r' (c)', '')
    df["innings"] = 1
    df = df.reset_index(drop=True)
    df['battingorder'] = df.index + 1
    df["bowler"] = df.apply(g, axis=1)
    battinginfo_1 = df

    #batting second inning

    t = tables[2]

    data = []
    for row in t.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            row_data.append(cell.text)
        data.append(row_data)



    df = pd.DataFrame(data)
    df = df.dropna()

    columns = ["player", "wkt", "runs", "balls", "mins", "fours", "sixes", "strikerate"]
    df.columns = columns

    df.player = df.player.str.replace(r' (c)', '')
    df.player = df.player.str.replace(r'†', '')
    df['player'] = df['player'].str.strip()
    df.wkt = df.wkt.str.replace(r'†', '')
    df.wkt = df.wkt.str.replace(r' (c)', '')

    df["innings"] = 2
    df = df.reset_index(drop=True)
    df['battingorder'] = df.index + 1
    df["bowler"] = df.apply(g, axis=1)
    battinginfo_2 = df


    # bowling first innings

    t = tables[1]

    data = []
    for row in t.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            row_data.append(cell.text)
        data.append(row_data)



    df = pd.DataFrame(data)
    df = df.dropna()

    columns = ["player", "overs", "maiden", "runs", "wickets", "economy", "dots", "fours", "sixes", "wides", "noball"]
    df.columns = columns

    df.player = df.player.str.replace(r' (c)', '')
    df.player = df.player.str.replace(r'†', '')
    df['player'] = df['player'].str.strip()
    df["innings"] = 1
    df = df.reset_index(drop=True)
    bowlingdf_1 = df

    # bowling second inngs


    t = tables[3]

    data = []
    for row in t.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            row_data.append(cell.text)
        data.append(row_data)



    df = pd.DataFrame(data)
    df = df.dropna()

    columns = ["player", "overs", "maiden", "runs", "wickets", "economy", "dots", "fours", "sixes", "wides", "noball"]
    df.columns = columns

    df.player = df.player.str.replace(r' (c)', '')
    df.player = df.player.str.replace(r'†', '')
    df['player'] = df['player'].str.strip()

    df["innings"] = 2
    df = df.reset_index(drop=True)
    bowlingdf_2 = df

    battinginfo_1['runs'] = battinginfo_1['runs'].astype(float)
    battinginfo_2['runs'] = battinginfo_2['runs'].astype(float)
    bowlingdf_1['wickets'] = bowlingdf_1['wickets'].astype(float)
    bowlingdf_2['wickets'] = bowlingdf_2['wickets'].astype(float)


    battinginfo_1["totalruns"] = battinginfo_1["runs"].sum()
    battinginfo_1["totalwkts"] = bowlingdf_1["wickets"].sum()
    battinginfo_2["totalruns"] = battinginfo_2["runs"].sum()
    battinginfo_2["totalwkts"] = bowlingdf_2["wickets"].sum()

    bowlingdf_1["totalruns"] = battinginfo_1["runs"].sum()
    bowlingdf_1["totalwkts"] = bowlingdf_1["wickets"].sum()
    bowlingdf_2["totalruns"] = battinginfo_2["runs"].sum()
    bowlingdf_2["totalwkts"] = bowlingdf_2["wickets"].sum()

    battinginfo_1['Matched_Name'] = battinginfo_1['player'].apply(lambda x: find_best_match(x, bowlingdf_1['player']))
    batting_merge_df_1 = battinginfo_1.merge(bowlingdf_1, how='left', left_on='Matched_Name', right_on='player')

    battinginfo_2['Matched_Name'] = battinginfo_2['player'].apply(lambda x: find_best_match(x, bowlingdf_2['player']))
    batting_merge_df_2 = battinginfo_2.merge(bowlingdf_2, how='left', left_on='Matched_Name', right_on='player')

    battingdf = pd.concat([batting_merge_df_1, batting_merge_df_2], ignore_index=True)
    battingdf["matchnumber"] = match + 1
    bowlingdf = pd.concat([bowlingdf_1, bowlingdf_2], ignore_index=True)
    bowlingdf["matchnumber"] = match + 1



    masterbattingdf = pd.concat([masterbattingdf, battingdf], ignore_index=True)
    masterbattingdf.drop(["overs", "maiden", "wickets", "economy", "dots", "fours_y", "sixes_y", "wides", "noball", "innings_y", "Matched_Name", "runs_y", "player_y"], axis=1, inplace=True)
    masterbowlingdf = pd.concat([masterbowlingdf, bowlingdf], ignore_index=True)

masterbattingdf = masterbattingdf.rename(columns={"player_x": "player"})
masterbattingdf.to_sql("masterbattingdf", engine)
masterbowlingdf.to_sql("masterbowlingdf", engine)
