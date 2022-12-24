from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys 
from selenium.common.exceptions import NoSuchElementException
import csv
import concurrent.futures
import time


CPU_CORES = 4
PATH = "C:\Program Files (x86)\chromedriver.exe"
PROFILE_PATH = "user-data-dir=C:\\Users\\yusif\\AppData\\Local\\Google\\Chrome\\User Data\\Defaults\\whatsapp_python"

search_XPATH = '//div[@title="Search input textbox"][@data-testid="chat-list-search"]'
msg_XPATH = '//div[@data-testid="msg-container"]'
msg_sender_XPATH = './/span[@class="a71At ajgl1lbb edeob0r2 i0jNr"]'
msg_text_XPATH = './/div[@class="_1Gy50"]/span[1]/span'
msg_time_XPATH = './/span[@class="l7jjieqr fewfhwl7"]'
day_XPATH = '//div[@class="_1-FMR _15WYQ focusable-list-item"]/div/span' 

msg_img_XPATH = ""
msg_quoted_text_XPATH = ".//div[]"
msg_sticker_XPATH = './/img[@class="_3HyaH _3jdoP _2Yjhf"]'


def get_driver_for(browser, path, profile_path=""):
    if browser.lower() == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument(profile_path)
        return webdriver.Chrome(options=options, service=Service(path))
    elif browser.lower() == "edge":
        options = webdriver.EdgeOptions()
        options.add_argument(profile_path)
        return webdriver.Edge(options=options, service=Service(path))

def open_chat(driver, name):
    driver.get('https://web.whatsapp.com') 
    search = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, search_XPATH)))
    search.send_keys(name)
    search.send_keys(Keys.RETURN)
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, msg_XPATH)))

def find_element_by(XPATH, msg):
    try:
        return msg.find_element(By.XPATH, XPATH).text
    except NoSuchElementException as e:
        pass

def last_messge(driver):
    msg = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, msg_XPATH)))
    msg_text = find_element_by(msg_text_XPATH, msg)
    msg_sender = find_element_by(msg_sender_XPATH, msg)   
    msg_time = find_element_by(msg_time_XPATH, msg)
    info = {
        "text": msg_text,
        "sender": msg_sender,
        "time": msg_time
    }
    
    return msg, info

def wrapper(arg):
    save_msgs_as_csv(*arg)


def save_msgs_as_csv(msg_path, msgs):
    with open(msg_path, 'w', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        msg_text=""
        for msg in msgs:
            msg_text = find_element_by(msg_text_XPATH, msg)
            msg_sender = find_element_by(msg_sender_XPATH, msg)   
            msg_time = find_element_by(msg_time_XPATH, msg)
            writer.writerow([msg_text, msg_sender, msg_time])

def save_days(day_path, days):
    with open(day_path, 'w', encoding='utf-8') as f:
        for day in days:
            f.write(day.text + '\n')

def scroll_up(till: int, driver):
    date = " "
    while not date.split('/')[0].isdigit() or not int(date.split('/')[0]) <= till:
        for _ in range(5):
            driver.execute_script('document.getElementsByClassName("_33LGR")[0].scroll(0, -1000)')
            time.sleep(0.25)
        date = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, day_XPATH))).text
        print(date)
        break


def main():
    driver = get_driver_for(browser="Chrome", path=PATH, profile_path=PROFILE_PATH)
    open_chat(driver, "Qarsonlar")
    scroll_up(12, driver)
    
    msgs = WebDriverWait(driver, 50).until(EC.presence_of_all_elements_located((By.XPATH, msg_XPATH)))
    days = driver.find_elements(By.XPATH, day_XPATH)
    print("Length of msgs: ", len(msgs))

    msgs_chunked = [msgs[i:i + len(msgs)//CPU_CORES] for i in range(0, len(msgs), len(msgs)//CPU_CORES)]
    msgs_paths = [f'mesages{i}.csv' for i in range(CPU_CORES)]

    print(list(zip(msgs_paths,msgs_chunked)))
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(wrapper, list(zip(msgs_paths,msgs_chunked)))

    print("--- took %s seconds ---" % (time.time() - start_time))
  
    save_days('days.csv', days)

    time.sleep(2000)

if __name__ == "__main__":
    main()


