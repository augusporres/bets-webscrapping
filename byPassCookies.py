import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as ex
import json
import pandas as pd
from datetime import datetime


def scrap_links(url):
    links = []
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(url)
    time.sleep(2)
    driver.switch_to.frame('sp_message_iframe_950597')
    time.sleep(2)
    # si navegador esta en ingles reemplazar feliz por happy
    # esto es para poder sacar el pop up de cookies y permitirte
    # hacer click en las distintas jornadas de partidos
    button = driver.find_element(By.XPATH, "//button[contains(text(), 'feliz')]")
    button.click()
    driver.switch_to.default_content()
    time.sleep(5)
    # left_arrow_clicked = False
    # left_arrow_button = driver.find_element(By.XPATH, "//button[contains(@class, 'header_previous__v_AQ7')")
    try:
        buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'stage_stage__DnLaS') or contains(@class, 'stage_active__7dnKz')]")
        for button in buttons:
            try:
                # Wait for the button to be clickable (maximum 10 seconds)
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'stage_stage__DnLaS') or contains(@class, 'stage_active__7dnKz')]")))

                # Scroll into view
                #driver.execute_script("arguments[0].scrollIntoView();", button)

                # Click the button
                button.click()
            except Exception as click_exception:
                print(f'Hubo un problema al clickear el elemento: {str(click_exception)}')
                continue
            # time.sleep(2)
            match_day_elements = driver.find_elements(By.XPATH, '//div[@class="match-day_match-day__abKub"]')
            for match in match_day_elements:
                # a_elements = match.find_elements(By.XPATH, 'a[@class="match_match__pP4PJ"]')
                a_elements = match.find_elements(By.TAG_NAME, 'a')
                for a in a_elements:
                    endElement = a.find_element(By.XPATH, "//span[@class='match_score__EI49F']")
                    links.append(a.get_attribute('href'))
    except ex.NoSuchElementException:
        print('--')
    finally:
        driver.quit()
        return links


def getdata(url):
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(url)
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
    script_tag = wait.until(EC.presence_of_element_located((By.ID, '__NEXT_DATA__')))
    data = json.loads(script_tag.get_attribute('innerHTML'))
    driver.quit()

    if "props" in data and "pageProps" in data["props"] and "content" in data["props"]["pageProps"]:
        content_data = data["props"]["pageProps"]["content"]
        if "match" in content_data:
            input_date = content_data["match"]['startDate']
            formated_date = datetime.fromisoformat(input_date)
            date = formated_date.strftime("%Y-%m-%d")
        else:
            date = ''
    else:
        date = ''
        
    if "props" in data and "pageProps" in data["props"] and "content" in data["props"]["pageProps"]:
        content_data = data["props"]["pageProps"]["content"]
        if "match" in content_data:
            teamA = content_data["match"]['teamA']['name']
        else:
            teamA = ''
    else:
        teamA = ''
    if "props" in data and "pageProps" in data["props"] and "content" in data["props"]["pageProps"]:
        content_data = data["props"]["pageProps"]["content"]
        if "match" in content_data:
            teamB = content_data["match"]['teamB']['name']
        else:
            teamB = ''
    else:
        teamB = ''
    
    score_team_A = validate_fields(data, 'teamA')
    score_team_B = validate_fields(data, 'teamB')
    if(score_team_A is not None or score_team_B is not None):
        summary = data["props"]["pageProps"]["content"]['match']['stats']['summary']
        attacking = data["props"]["pageProps"]["content"]['match']['stats']['attacking']
        passing = data["props"]["pageProps"]["content"]['match']['stats']['passing']
        duels = data["props"]["pageProps"]["content"]['match']['stats']['duels']
        defence = data["props"]["pageProps"]["content"]['match']['stats']['defence']
        discipline = data["props"]["pageProps"]["content"]['match']['stats']['discipline']
        info = [summary, attacking, passing, duels, defence, discipline]
    else:
        summary = ''
        attacking = ''
        passing = ''
        duels = ''
        defence = ''
        discipline = ''
        info = []

    flat = {}
    for dataset in info:
        for metric in dataset:
            flat[metric['type'] + '_teamA'] = metric['teamA']
            flat[metric['type'] + '_teamB'] = metric['teamB']
    df = pd.DataFrame([flat])
    df['SCORE_teamA'] = score_team_A
    df['SCORE_teamB'] = score_team_B
    df['Local'] = teamA
    df['Visitante'] = teamB
    df.insert(0, 'date', date)
    return df

def validate_fields(data, key):
    if "props" in data and "pageProps" in data["props"] and "content" in data["props"]["pageProps"]:
        content_data = data["props"]["pageProps"]["content"]
        if "match" in content_data:
            match_data = content_data["match"]
            if "score" in match_data:
                score_data = match_data["score"]
                if score_data is not None and key in score_data:
                    return score_data[key]
                else:
                    return None
            else:
                return None
        else:
            return None
    else:
        return None


# start of variables
url = 'https://www.goal.com/es/laliga/partidos-resultados/34pl8szyvrbwcmfkuocjm3r6t'
df = pd.DataFrame(columns = ['date','POSSESSION_teamA', 'POSSESSION_teamB', 'SHOT_TOTAL_teamA','SHOT_TOTAL_teamB', 'CORNER_TOTAL_teamA', 'CORNER_TOTAL_teamB','FOUL_TOTAL_teamA', 'FOUL_TOTAL_teamB', 'SHOT_ACCURACY_teamA','SHOT_ACCURACY_teamB', 'SHOT_ON_TARGET_teamA', 'SHOT_ON_TARGET_teamB','SHOT_OFF_TARGET_teamA', 'SHOT_OFF_TARGET_teamB', 'SHOT_BLOCKED_teamA','SHOT_BLOCKED_teamB', 'BIG_CHANCE_MISSED_teamA','BIG_CHANCE_MISSED_teamB', 'OFFSIDE_TOTAL_teamA', 'OFFSIDE_TOTAL_teamB','PASS_TOTAL_teamA', 'PASS_TOTAL_teamB', 'PASS_SUCCESSFUL_teamA','PASS_SUCCESSFUL_teamB', 'PASS_ACCURACY_teamA', 'PASS_ACCURACY_teamB','CROSS_TOTAL_teamA', 'CROSS_TOTAL_teamB', 'CROSS_SUCCESSFUL_teamA','CROSS_SUCCESSFUL_teamB', 'PASS_TACKLE_ACCURACY_teamA','PASS_TACKLE_ACCURACY_teamB', 'DUEL_SUCCESSFUL_teamA','DUEL_SUCCESSFUL_teamB', 'AERIAL_DUEL_SUCCESSFUL_teamA','AERIAL_DUEL_SUCCESSFUL_teamB', 'TAKE_ON_SUCCESSFUL_teamA','TAKE_ON_SUCCESSFUL_teamB', 'BLOCK_TOTAL_teamA', 'BLOCK_TOTAL_teamB','CLEARANCE_TOTAL_teamA', 'CLEARANCE_TOTAL_teamB','INTERCEPTION_TOTAL_teamA', 'INTERCEPTION_TOTAL_teamB','SAVE_TOTAL_teamA', 'SAVE_TOTAL_teamB', 'FOUL_WON_teamA','FOUL_WON_teamB', 'YELLOW_CARD_TOTAL_teamA', 'YELLOW_CARD_TOTAL_teamB', 'SCORE_teamA', 'SCORE_teamB', 'Local', 'Visitante'])
column_check = list(df.columns)
links = scrap_links(url)
words_to_exclude = ['noticias', 'clasificac']
filtered_links = []
# end of variables

for link in links:
    if not any(word in link for word in words_to_exclude):
        filtered_links.append(link)

for link in filtered_links:
    new_row = getdata(link)
    if new_row.isna().any().any():
        continue
    for col in column_check:
        if col not in new_row.columns:
            new_row[col] = 0
    new_row = new_row[column_check]
    df = pd.concat([df,new_row], ignore_index=True)
df.to_excel(r'C:\Users\augus\Desarrollo\Python\bets-webscrapping\Resultados_v5.xlsx', index=False)
    
print('Proceso finalizado')
print(len(filtered_links))