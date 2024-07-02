import os
import pandas as pd
import requests
import tkinter as tk
import time

# Adjust the file path to be relative
file_path = os.path.join(os.path.dirname(__file__), "merged_file_cleaned_modified.csv")
movies = pd.read_csv(file_path)


def get_recommendations(input_tconst, movies, top_n=5):
    """Fetches movie recommendations based on the input IMDb ID (tconst) using the OMDB API.

    Args:
        input_tconst (str): The IMDb ID of the movie to base recommendations on.
        movies (pd.DataFrame): DataFrame containing movie data.
        top_n (int): The number of top recommendations to return.

    Returns:
        list: List of formatted recommendation strings.
    """
    base_url = 'http://www.omdbapi.com/'

    params = {
        'apikey': api_key,
        'i': input_tconst,
        'r': 'json'  # Response format
    }

    try:
        # Sending GET request to OMDB API
        response = requests.get(base_url, params=params)
        data = response.json()

        if data['Response'] == 'True':
            # Extracting relevant information
            genres = data['Genre']
            directors = data['Director']
            title_type = data['Type']
        else:
            print(f"OMDB API: Movie not found for tconst {input_tconst}")
            return []  # Return empty list if movie not found

    except requests.exceptions.RequestException as e:
        print(f'Error fetching data: {e}')
        return []

    print(f"Genres: {genres}, Directors: {directors}, Title Type: {title_type}")

    # Filter the DataFrame by genres
    genre_list = [genre.strip() for genre in genres.split(',')]
    genre_filtered = movies[movies['genres'].str.contains('|'.join(genre_list), na=False)].copy()

    if genre_filtered.empty:
        print("Genre Filtering: No matching genres found.")
        return []

    # Filter by directors
    if directors:
        director_list = [director.strip() for director in directors.split(',')]
        filtered_by_directors = genre_filtered[
            genre_filtered['directors'].str.contains('|'.join(director_list), na=False)].copy()
        filtered_by_directors = filtered_by_directors[
            filtered_by_directors['tconst'] != input_tconst]  # Exclude input movie

        if len(filtered_by_directors) > 5:
            sorted_movies = filtered_by_directors.sort_values(by='averageRating', ascending=False)
            print(f"Director Filtering: Found {len(filtered_by_directors)} movies by same directors.")
        else:
            sorted_movies = genre_filtered.sort_values(by='averageRating', ascending=False)
            print("Director Filtering: Not enough movies by same directors, using genre-filtered movies.")
    else:
        sorted_movies = genre_filtered.sort_values(by='averageRating', ascending=False)

    if sorted_movies.empty:
        print("Sorting: No movies found after sorting.")
        return []

    # Filter by title type
    typetitle_filtered = sorted_movies[sorted_movies['titleType'] == title_type].copy()

    if typetitle_filtered.empty or len(typetitle_filtered) < 5:
        recommendations = sorted_movies.head(top_n)
    else:
        recommendations = typetitle_filtered.head(top_n)

    if recommendations.empty:
        print("Recommendations: No recommendations found.")
        return []

    # Format the recommendations as strings
    recommendation_texts = []
    for index, row in recommendations.iterrows():
        recommendation_texts.append(
            f"Title: {row['tconst']}\n"
            f"Genres: {row['genres']}\n"
            f"Directors: {row['directors']}\n"
            f"Title Type: {row['titleType']}\n"
            f"Average Rating: {row['averageRating']}\n"
            "------------------------\n"
        )

    return recommendation_texts


def open_main_window():
    """Opens the main window for the movie recommender application."""
    global api_key

    api_key = api_key_entry.get()
    if not api_key:
        error_label.config(text="No API key found. Please enter the API key.")
        return

    # Close the configuration window
    first_window.destroy()

    def search_movie():
        """Searches for movie recommendations based on user input IMDb ID."""
        input_tconst = user_tconst_entry.get().strip()
        if not input_tconst:
            error_label.config(text="Please enter a valid IMDb ID.")
            return

        recommendations_text.delete('1.0', tk.END)  # Clear previous recommendations
        start_time = time.time()  # Start time measurement

        recommendations = get_recommendations(input_tconst, movies)

        end_time = time.time()  # End time measurement
        elapsed_time = end_time - start_time  # Calculate elapsed time

        if recommendations:
            for recommendation in recommendations:
                recommendations_text.insert(tk.END, recommendation)
        else:
            recommendations_text.insert(tk.END, "No recommendations found.")

        # Display the elapsed time
        time_label.config(text=f"Time to find your results: {elapsed_time:.2f} seconds")

    # Create the main window
    window = tk.Tk()
    window.title("Movie Recommender")
    window.geometry("500x700")

    # Label and Entry for searching IMDb ID (tconst)
    search_label = tk.Label(window, text="Enter IMDb ID:")
    search_label.pack(pady=10)

    user_tconst_entry = tk.Entry(window, width=20)
    user_tconst_entry.pack()

    search_button = tk.Button(window, text="Search", command=search_movie)
    search_button.pack(pady=10)

    # Label for text box
    recommendations_text_label = tk.Label(window, text="Movie recommendations:")
    recommendations_text_label.pack(pady=10)

    # Textbox for displaying recommendations
    recommendations_text = tk.Text(window, wrap=tk.WORD)
    recommendations_text.pack(pady=2)

    # Label for displaying the elapsed time
    time_label = tk.Label(window, text="")
    time_label.pack(pady=10)

    window.mainloop()


# Create the first window
first_window = tk.Tk()
first_window.title("API KEY CONFIGURATION")
first_window.geometry("500x400")

# Label and entry for API key input
api_key_label = tk.Label(first_window, text="Enter your API key:")
api_key_label.pack(pady=20)

api_key_entry = tk.Entry(first_window, width=50, show='*')
api_key_entry.pack(pady=5)

# Button to submit API key
submit_button = tk.Button(first_window, text="Submit", command=open_main_window)
submit_button.pack(pady=20)

# Label for error message
error_label = tk.Label(first_window, fg="red")
error_label.pack(pady=5)

first_window.mainloop()
