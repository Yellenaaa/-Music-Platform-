from abc import ABC, abstractmethod
from functools import wraps
import time
import re


class InvalidSongError(Exception):
    pass

class PlaylistError(Exception):
    pass

class SearchError(Exception):
    pass

def log_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        with open("user_actions.log", "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {func.__name__} called\n")
        return result
    return wrapper

types =  {"email": lambda val: isinstance(val, str) and bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', val)),
          str: lambda val: isinstance(val, str) and len(val) >= 3,
          int: lambda val: isinstance(val, int) and val >= 0,
          float: lambda val: isinstance(val, float) and val >= 0
          }
class Validator:
    def __init__(self, type):
        self.validator_foo = types[type]

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    
    def __set__(self, instanse, value):
        if not self.validator_foo(value):
            raise TypeError(f"Invalid Type for {self.name}")
        instanse.__dict__[self.name] = value

class Song(ABC):
    title = Validator(str)
    duration = Validator(float)
    def __init__(self, title, artist, duration):
        self.title = title
        self.artist = artist
        self.duration = duration

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def get_details(self):
        pass

class RockSong(Song):
    def __init__(self, title, artist, duration, energy_level=5):
        super().__init__(title, artist, duration)
        self.energy_level = energy_level 

    def play(self):
        print(f"Playing rock song: '{self.title}' by {self.artist.name} with energy level {self.energy_level}.")

    def get_details(self):
        return (f"Rock Song: {self.title} | Artist: {self.artist.name} | Duration: {self.duration} mins | "
            f"Energy Level: {self.energy_level}")
        
class PopSong(Song):
    def __init__(self, title, artist, duration, danceability=5):
        super().__init__(title, artist, duration)
        self.danceability = danceability 

    def play(self):
        print(f"Playing pop song: '{self.title}' by {self.artist.name} with danceability {self.danceability}.")

    def get_details(self):
        return (f"Pop Song: {self.title} | Artist: {self.artist.name} | Duration: {self.duration} mins | "
                f"Danceability: {self.danceability}")
    
class Artist:
    name = Validator(str)
    contact_info = Validator("email")

    def __init__(self, name, contact_info):
        self.name = name
        self.contact_info = contact_info
        self.songs = []

    def add_song(self, song):
        if not song in self.songs:
            self.songs.append(song)
        else:
            print(f"Song '{song.title}' is already added for {self.name}.")

    def get_songs(self):
        return self.songs
    
class User:
    name = Validator(str)
    contact_info = Validator("email")

    def __init__(self, name, contact_info):
        self.name = name
        self.contact_info = contact_info
        self.favorites = {"favorite_songs": [], "favorite_artists": []}
        self.playlists = {}
        self.queue = []
        

    def add_to_queue(self, song):
        self.queue.append(song)
        print(f"Added '{song.title}' to queue.")

    def play_next(self):
        if self.queue:
            next_song = self.queue.pop(0)
            next_song.play()
        else:
            print("The song queue is empty.")


    @log_action
    def play_song(self, song):
        song.play()

    @log_action
    def add_to_favorites(self, item):
        if isinstance(item, Song):
            if not item in self.favorites["favorite_songs"]:
                self.favorites["favorite_songs"].append(item)
                print(f"Song '{item.title}' added to favorites.")
            else:
                print(f"Song '{item.title}' is already in favorites.")
        elif isinstance(item, Artist):
            if not item  in self.favorites["favorite_artists"]:
                self.favorites["favorite_artists"].append(item)
                print(f"Artist '{item.name}' added to favorites.")
            else:
                print(f"Artist '{item.name}' is already in favorites.")
        else:
            print("Invalid item type. Only Song or Artist can be added to favorites.")

    def create_playlist(self, name, songs):

        if name in self.playlists:
            raise PlaylistError(f"A playlist with the name '{name}' already exists.")
        self.playlists[name] = list(songs)
        print(f"Playlist '{name}' created.")

    def add_song_to_playlist(self, playlist_name, song):
        if playlist_name not in self.playlists:
            raise PlaylistError(f"Playlist '{playlist_name}' does not exist.")
        self.playlists[playlist_name].append(song)
        print(f"Added '{song.title}' to playlist '{playlist_name}'.")
    
    def remove_from_playlist(self, playlist_name, song):
        if playlist_name not in self.playlists:
            raise PlaylistError(f"Playlist '{playlist_name}' does not exist.")
        try:
            self.playlists[playlist_name].remove(song)
            print(f"Removed '{song.title}' from playlist '{playlist_name}'.")
        except ValueError:
            print(f"Song '{song.title}' not found in playlist '{playlist_name}'.")

    def search_songs(self, songs, query):
        results = [song for song in songs if query.lower() in song.title.lower() or
                   query.lower() in song.artist.name.lower()]
        if not results:
            raise SearchError(f"No songs found matching query: '{query}'.")
        return results          
    

artist1 = Artist("The Rockers", "rockers@example.com")
artist2 = Artist("PopStars", "popstars@gmail.com")

rock_song1 = RockSong("Thunder Strike", artist1, 3.5, energy_level=8)
pop_song1 = PopSong("Dance All Night", artist2, 4.0, danceability=9)

artist1.add_song(rock_song1)
artist2.add_song(pop_song1)

user1 = User("Alice", "alice@example.com")
user2 = User("Emma", "emma@gmail.com")

all_songs = [rock_song1, pop_song1]
try:
    search_results = user1.search_songs(all_songs, "thunder")
    for song in search_results:
        print(song.get_details())
except SearchError as e:
    print(e)

user1.play_song(rock_song1)
user1.add_to_favorites(rock_song1)
user1.add_to_favorites(artist1)

try:
    user1.create_playlist("My Rock Playlist", [rock_song1])
    user1.add_song_to_playlist("My Rock Playlist", pop_song1)  
    user1.remove_from_playlist("My Rock Playlist", pop_song1)
except PlaylistError as e:
    print(e)

user1.add_to_queue(rock_song1)
user1.add_to_queue(pop_song1)
user1.play_next()
user1.play_next()









    







