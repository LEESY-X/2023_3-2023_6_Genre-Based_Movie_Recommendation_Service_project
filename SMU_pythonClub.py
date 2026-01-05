from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
from tkinter import *
from tkinter import messagebox

# <--Setting for Selenium.-->

chrome_options = Options()

# Running chromedriver on background.
chrome_options.add_argument("--headless")

# Chromedriver path
# Chromedriver download link : https://chromedriver.chromium.org/downloads
# download version match your current chrome version.
chromedriver_path = '/Users/kang1027/WorkSpace/AutoReservation/chromedriver_mac_arm64'

driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

# <-- Completed selenium setting -->

def Main():
    if input("영화 리스트를 새로 업데이트 하시겠습니까? (Y/N)") == 'Y':
        loding_Movie()

# Update movie data
def loding_Movie():
    print("영화 데이터를 새로 가져오고 있습니다...")

    # Crawling attributes
    fieldnames = ['Name', 'Country', 'Release_date', 'OTT_name', 'Genre', 'Genre2', 'Link']

    rows = []

    for i in range(2020, 2024): # ==> 2020~2023 Movie Data Crawling
        url = f"https://flixpatrol.com/popular/movies/movie-db/{i}/"
        driver.get(url)
        # Extrusion for element from html in movie data.
        elements = driver.find_elements(By.CSS_SELECTOR, '.flex.group.items-center')
        # Data organization.
        for element in elements:
            movie_info = element.text.split('\n')
            movie_title = movie_info[0]
            movie_attributes = [info for info in movie_info[1:] if info != '|']
            ott_name = next((info for info in movie_attributes if info in ['Netflix', 'HBO', 'Apple', 'Disney+', 'Amazon', 'Hulu', 'HBO Max']), None)
            if ott_name:
                rows.append({'Name': movie_title,
                             'Country': movie_attributes[1] if len(movie_attributes) > 1 else None,
                             'Release_date': movie_attributes[2] if len(movie_attributes) > 2 else None,
                             'OTT_name': ott_name if len(movie_attributes) > 3 else None,
                             'Genre': movie_attributes[4] if len(movie_attributes) > 4 else None,
                             'Genre2': movie_attributes[5] if len(movie_attributes) > 5 else None,
                             'Link': element.get_attribute('href')})
            else:
                rows.append({'Name': movie_title,
                             'Country': movie_attributes[1] if len(movie_attributes) > 1 else None,
                             'Release_date': movie_attributes[2] if len(movie_attributes) > 2 else None,
                             'OTT_name': 'None',
                             'Genre': movie_attributes[3] if len(movie_attributes) > 3 else None,
                             'Genre2': movie_attributes[4] if len(movie_attributes) > 4 else None,
                             'Link': element.get_attribute('href')})

    # Save data for csv file.
    with open('Movie_info.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("영화 데이터를 다 가져왔습니다.")


def show_movie_info():
    selected_movie = movie_list.get(ACTIVE)

    if selected_movie :
        with open('Movie_info.csv', 'r', encoding='UTF8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Name'] == selected_movie:
                    url = row['Link']
    driver.get(url)

    if selected_movie:
        with open('Movie_info.csv', 'r', encoding='UTF8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Name'] == selected_movie:
                    info = f"Name: {row['Name']}\n\n"
                    info += f"Country: {row['Country']}\n\n"
                    info += f"Release Date: {row['Release_date']}\n\n"
                    info += f"Genre: {row['Genre']}\n\n"
                    info += f"Genre2: {row['Genre2']}\n\n"
                    info += f"Movie Info : \n{driver.find_element(By.CLASS_NAME, 'card-body').text}\n\n"

                    starring = driver.find_elements(By.CLASS_NAME, 'card-body')[1].text.split('\n')[1].split(',')
                   
                    for i, value in enumerate(starring):
                        if i == 0:
                            info += value+'\n'
                        else:
                            info += value.replace(' ', '', 1) +'\n'

                    director = driver.find_elements(By.CLASS_NAME, 'card-body')[1].text.split('\n')[3]
                    info += f"\nDirector : {director}\n\n"
                    info += f"IMDB : {driver.find_elements(By.CSS_SELECTOR, '.mb-1.text-2xl.text-gray-400')[0].text}\n\n"
                    info += f"ROTTEN TOMATOES : {driver.find_elements(By.CSS_SELECTOR, '.mb-1.text-2xl.text-gray-400')[1].text}\n\n"

                    messagebox.showinfo("Movie Information", info)
                    break

# Read csv file and compare to genre
def genre_matching(user_genre):
    matching_movies = {}

    with open('Movie_info.csv', 'r', encoding='UTF8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Genre'] == user_genre or row['Genre2'] == user_genre:
                matching_movies[row['Name']] = row['Link']

    if len(matching_movies) > 0:
        movie_list.delete(0, END)
        for movie in matching_movies.keys():
            movie_list.insert(END, movie)

Main()

# Create main window
root = Tk()
root.title("Movie Genre Matching")
root.geometry("400x300")

# Genre entry
genre_label = Label(root, text="Enter Genre:")
genre_label.pack()

genre_entry = Entry(root)
genre_entry.pack()

# Genre matching button
match_button = Button(root, text="Match Genre", command=lambda: genre_matching(genre_entry.get()))
match_button.pack()

# Movie list
movie_list = Listbox(root)
movie_list.pack()

# Movie info button
info_button = Button(root, text="Show Movie Info", command=show_movie_info)
info_button.pack()

root.mainloop()

driver.quit()
