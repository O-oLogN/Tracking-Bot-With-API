from selenium import webdriver

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import NoSuchElementException

from flask import Flask, jsonify, send_file

from datetime import datetime

import threading

import time

import os

            #################### Constants here ####################

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

TRACKING_FILE_PATH = os.path.join(ROOT_DIR, "Curr", "tracking.txt")

INFO_FILE_PATH = os.path.join(ROOT_DIR, "Info", "Info.txt")

WEB_PATH = "https://www.facebook.com"

SCREENSHOT_PATH = os.path.join(ROOT_DIR, "Curr", "temp.png")

SLEEP_TIME = 60


            #######################################################

app = Flask(__name__)

tracking_thread = None

stop_tracking_thread = False

currentSessionDayMonthYear = ""

latestSessionDayMonthYear = ""

nameDayInTheWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

sessionInDay = ["night", "morning", "afternoon", "evening"]     # 0-6, 6-12, 12-18, 18-24

def GetSaveFileName():
    global currentSessionDayMonthYear
    now = datetime.now()
    currentTime = now.strftime("%H:%M")
    currentDayInWeek = now.weekday()
    currentDayInMonth = now.day
    currentMonth = now.month
    currentYear = now.year
    strFileName = f"{nameDayInTheWeek[currentDayInWeek]}-{sessionInDay[int(((int(currentTime[:2])) * 60 + int(currentTime[3:5])) / 360)]}({currentDayInMonth}-{currentMonth})"
    currentSessionDayMonthYear = f"{sessionInDay[int(((int(currentTime[:2])) * 60 + int(currentTime[3:5])) / 360)]}-{nameDayInTheWeek[currentDayInWeek]}-{currentDayInMonth}-{currentMonth}-{currentYear}"
    return strFileName

def tracking():

    infoFile = open(INFO_FILE_PATH, "r")

    info = infoFile.read().split()

    username = info[0]

    password = info[1]

    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--enable-javascript")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")  # Updated user-agent
    options.add_argument("--disable-features=RendererCodeIntegrity")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    
    driver = webdriver.Chrome(options=options)

    # driver.maximize_window()  

    driver.get(WEB_PATH)

    # WebDriverWait(driver, 7200).until(EC.presence_of_all_elements_located(
    #     (By.XPATH, "/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div[1]/form/div[2]/button")))

    driver.find_element(By.NAME, "email").send_keys(username, Keys.ESCAPE)

    driver.find_element(By.NAME, "pass").send_keys(password, Keys.ENTER)

    WebDriverWait(driver, 7200).until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "xe3v8dz")))        # wait for the presence of main page
    

    driver.get(info[2])     # Access the main page

    WebDriverWait(driver, 7200).until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.xi112ho.x17zwfj4.x585lrc.x1403ito.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xn6708d.x1ye3gou.xtvsq51.x1r1pt67")))        # wait for the presence of "Nhắn tin" button

    driver.find_element(By.CLASS_NAME, "x1n2onr6.x1ja2u2z.x78zum5.x2lah0s.xl56j7k.x6s0dn4.xozqiw3.x1q0g3np.xi112ho.x17zwfj4.x585lrc.x1403ito.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xn6708d.x1ye3gou.xtvsq51.x1r1pt67").click()
    WebDriverWait(driver, 7200).until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "x5yr21d.x1uvtmcs")))   # wait for the presence of message window

    driver.save_screenshot(SCREENSHOT_PATH)

    global stop_tracking_thread, latestSessionDayMonthYear
    while not stop_tracking_thread:
        saveFileName = GetSaveFileName()    # NOTE: Although saveFileName is not used but GetSaveFileName()
                                            # should be called to update currentSessionDayMonthYear
        now = datetime.now()

        currentTime = now.strftime("%H:%M")

        tracking = open(TRACKING_FILE_PATH, "a")

        if (latestSessionDayMonthYear == ""):
            with open(TRACKING_FILE_PATH, "r") as tracking_file:
                line = tracking_file.readline()
                while (line):
                    if (line.startswith(tuple(sessionInDay))):
                        latestSessionDayMonthYear = line.strip()
                    line = tracking_file.readline()
            
        if currentSessionDayMonthYear != latestSessionDayMonthYear:
            tracking_file = open(TRACKING_FILE_PATH, "w")
            tracking_file.write(currentSessionDayMonthYear + "\n")
            latestSessionDayMonthYear = currentSessionDayMonthYear
        tracking_file.close()        

        isOnlineStatus = True
        try:
            driver.find_element(By.CLASS_NAME, "x6s0dn4.xzolkzo.x12go9s9.x1rnf11y.xprq8jg.x9f619.x3nfvp2.xl56j7k.xv9rvxn.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x1gp4ovq.xdio9jc.x1h2mt7u.x7g060r.x10w6t97.x1td3qas.x6zyg47.x1xm1mqw.xpn8fn3.xtct9fg")
                    # try to find green dot on avatar
        except NoSuchElementException:
            isOnlineStatus = False

        if isOnlineStatus == True:
            strStatus = f"{currentTime} 1"
        else:
            strStatus = f"{currentTime} 0"
        
        tracking.write(strStatus + '\n')

        tracking.close()

        # newFilePath = f"Data\\{saveFileName}.txt"

        # if os.path.isfile(newFilePath) == False:
        #     os.system(f'echo new > "{newFilePath}"')  # Create new save data file with content "new" 

        # os.system(f'type "{TRACKING_FILE_PATH}" > "{newFilePath}"')
        #     # Copy data from tracking.txt to saveFileName.txt

        time.sleep(SLEEP_TIME)

#------------------------------ Triggering new thread   ---------------------------------

@app.route('/', methods=['GET'])
def hello():
    return "Hello", 200

@app.route("/pic", methods=['GET'])
def download():
    try:
        return send_file(SCREENSHOT_PATH, as_attachment=True)
    except FileNotFoundError:
        return "Screenshot not found", 404

@app.route('/start')
def start_tracking_thread():
    global tracking_thread, stop_tracking_thread
    if tracking_thread is None:
        stop_tracking_thread = False
        tracking_thread = threading.Thread(target=tracking)
        tracking_thread.start()
    return "Tracking thread started", 200

@app.route('/result')
def retrieve_result():
    try: 
        info_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Info", "Info.txt")
        print(f"INFO_FILE_PATH: {info_file_path}")      # For debugging: show dirname

        with open(TRACKING_FILE_PATH, "r") as file:
            file_content = file.read()  

        return jsonify({
            "message": "Tracking thread still in progress, retrieving result",
            "content": file_content
        }), 200
    except FileNotFoundError:
        return jsonify({
            "message": "Tracking thread still in progress, but tracking file was not found.",
            "file": None
        }), 404
    
@app.route('/delete')
def deleteTrackingFileContent():
    # allowed_ranges = [
    #     (5, 55, 6, 5),
    #     (11, 55, 12, 5),
    #     (17, 55, 18, 5),
    #     (23, 55, 0, 5)
    # ]

    # # Get the current time
    # now = datetime.now()
    # current_hour = now.hour
    # current_minute = now.minute

    # # Function to check if current time is within any of the allowed ranges
    # def is_within_disallowed_range():
    #     for start_hour, start_min, end_hour, end_min in allowed_ranges:
    #         if start_hour <= current_hour <= end_hour:
    #             if start_hour == end_hour:
    #                 # Single hour range
    #                 return start_min <= current_minute <= end_min
    #             elif current_hour == start_hour:
    #                 return current_minute >= start_min
    #             elif current_hour == end_hour:
    #                 return current_minute <= end_min
    #             else:
    #                 return False
    #     return False

    # # Check if current time falls within disallowed ranges
    # if is_within_disallowed_range():
    #     return jsonify({
    #         "message": "Deleting data is restricted outside the allowed time windows."
    #     }), 403
    
    try:
        global latestSessionDayMonthYear
        latestSessionDayMonthYear = ""
        with open(TRACKING_FILE_PATH, "w") as file:
            file.truncate()
        return jsonify({
            "message": "Data in tracking file deleted successfully"
        }), 200
    except Exception:
        return jsonify({
            "message": "Error occurred while deleting data in tracking file"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port = port)