from bs4 import BeautifulSoup
import pandas as pd
from queue import Queue
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from threading import Thread

hours_list = []
availability_list = []
hours_not_available = []
key_errors = []
court_queue = Queue()
num_threads = 12

def find_hours(soup, court_name):
    hours = pd.read_html(str(soup.find("table", {"class": "WgFkxc"})))[0]
    hours.columns = ["Day", "Hours"]
    hours["Court"] = court_name
    return hours

def find_availability(soup, court_name, hours):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_open = [f"{d}s" for d in days if hours.loc[hours["Day"] == d, "Hours"].item() != "Closed"]

    all_dfs = []
    for d in days_open:
        day_info = str(soup.find("div", {"aria-label": f"Histogram showing popular times on {d}"}))
        day_soup = BeautifulSoup(day_info, "html.parser")
        tags = day_soup.find_all("div", {"class": ["lubh-bar", "lubh-bar lubh-sel"]})

        time = []
        value = []
        description = []
        for t in tags:
            attributes = t.attrs
            time.append(attributes['aria-label'].split(": ")[0])
            height_value = re.findall(r'\d+', attributes["style"])[0]
            value.append(height_value)
            description.append(attributes['aria-label'].split(": ")[1])

        day = [d for _ in range(len(tags))]
        court = [court_name for _ in range(len(tags))]

        day_df = pd.DataFrame({"Court": court, "Day": day, "Time": time, "Value": value, "Description": description})
        all_dfs.append(day_df)

    combined_df = pd.concat(all_dfs, axis=0).reset_index(drop=True)
    return combined_df

def scrape_single_court_info(q, i):
    while True:
        court_name = q.get()
        print(f"Starting {court_name}", i)
        url = "https://www.google.com/"

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        with webdriver.Chrome(options=chrome_options) as driver:
            driver.get(url)
            time.sleep(2)

            search = driver.find_element_by_xpath("//input[@name='q']")
            search.send_keys(court_name)
            search.send_keys(Keys.RETURN)

            soup = BeautifulSoup(driver.page_source, "html.parser")

        try:
            hours = find_hours(soup, court_name)
            hours_list.append(hours)

            availability = find_availability(soup, court_name, hours)
            availability_list.append(availability)

        except ValueError:
            hours_not_available.append(court_name)

        except KeyError:
            key_errors.append(court_name)

        print(f"Done {court_name}")
        q.task_done()


def scrape_all_courts():
    court_info = pd.read_csv("court_information.csv")

    for i in range(num_threads):
        worker = Thread(target=scrape_single_court_info, args=(court_queue, i))
        worker.setDaemon(True)
        worker.start()

    for c in list(court_info['name']):
        if c != "Kezar Pavilion":
            court_queue.put(c)

    print("***Main Thread Waiting\n")
    court_queue.join()
    print("***Done")

def main():
    scrape_all_courts()

    all_courts_hours_df = pd.concat(hours_list, axis=0)
    all_courts_hours_df.to_csv("Court_Hours.csv")

    all_courts_availability_df = pd.concat(availability_list, axis=0)
    all_courts_availability_df.to_csv("Court_Availability.csv")

    print("Not available: ", hours_not_available)
    print("Key error ", key_errors)

if __name__ == "__main__":
    main()
