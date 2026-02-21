# Step 1: Create Empty Data Structures
songs = []
genre_count = {}

# Step 2 & 3: Collect Song Information and Store Data
for i in range(5):
    print(f"Enter Song {i+1}:")
    song_name = input(" Song name: ")
    genre = input(" Genre: ")
    
    # Store as a tuple
    songs.append((song_name, genre))
    
    # Count genres
    genre_count[genre] = genre_count.get(genre, 0) + 1
    print()  # blank line for readability

# Step 4: Display Results

# Display song list
print("=== YOUR MUSIC LIBRARY ===")
for idx, (song_name, genre) in enumerate(songs, start=1):
    print(f" {idx}: {song_name} ({genre})")

print("\n=== GENRE STATISTICS ===")
for genre, count in genre_count.items():
    print(f"{genre}: {count} song{'s' if count > 1 else ''}")

# Identify the most popular genre
most_popular = max(genre_count, key=genre_count.get)
print(f"Most popular genre: {most_popular}")