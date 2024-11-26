import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import psycopg2
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SpotifyClient:
    def __init__(self):
        """ 환경 변수 가져오기 """
        load_dotenv()

        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        redirect_uri = os.getenv("REDIRECT_URI")

        # Spotipy initialization
        self.scope = "playlist-read-private playlist-read-collaborative"
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=self.scope,
            )
        )

        # PostgreSQL 연결 설정
        self.db_connection = psycopg2.connect(
            host= "115.139.31.54",
            port = 5432,
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        self.db_cursor = self.db_connection.cursor()

        # 테이블이 존재하면 삭제하고 새로 생성
        self.create_table()

    def create_table(self):
        """ 플레이리스트 정보를 저장할 테이블 생성 (이미 있으면 삭제 후 생성) """
        try:
            # 테이블이 이미 존재하면 삭제
            drop_table_query = "DROP TABLE IF EXISTS playlist_schema.spotify_playlist;"
            self.db_cursor.execute(drop_table_query)
            self.db_connection.commit()
            logging.info("Existing spotify_playlist table dropped (if it existed).")

            # 새로운 테이블 생성
            create_table_query = """
            CREATE TABLE playlist_schema.spotify_playlist (
                no SERIAL PRIMARY KEY,
                title VARCHAR(256),
                link VARCHAR(256),
                cover_image VARCHAR(256)
            );
            """
            self.db_cursor.execute(create_table_query)
            self.db_connection.commit()
            logging.info("New spotify_playlist table created.")
        except Exception as e:
            logging.error(f"Error creating table: {e}")
            self.db_connection.rollback()  # 오류 발생 시 롤백

    def save_playlist_to_db(self, title, link, cover_image):
        """ 플레이리스트 정보를 PostgreSQL에 저장 """
        try:
            # 데이터 삽입 쿼리
            query = """
            INSERT INTO playlist_schema.spotify_playlist (title, link, cover_image)
            VALUES (%s, %s, %s);
            """
            self.db_cursor.execute(query, (title, link, cover_image))
            self.db_connection.commit()  # 변경사항 커밋
            logging.info(f"Saved playlist: {title} to database")
        except Exception as e:
            logging.error(f"Error saving playlist: {e}")
            self.db_connection.rollback()  # 오류 발생 시 롤백

    def find_playlists_by_song(self, song_title):
        # 노래 검색
        results = self.sp.search(q=song_title, type='track', limit=10)
        
        if not results['tracks']['items']:
            print("No track found with that name.")
            return
        
        track = results['tracks']['items'][0]
        print(f"Found track: {track['name']} by {track['artists'][0]['name']}")

        # 해당 트랙을 포함한 플레이리스트 검색
        playlists = self.sp.search(q=track['name'], type='playlist', limit=5)
        
        if not playlists['playlists']['items']:
            print("No playlists found containing this song.")
            return
        
        print(f"Playlists containing '{track['name']}':")
        for idx, playlist in enumerate(playlists['playlists']['items'], 1):
            # 플레이리스트 커버 이미지 가져오기
            title = playlist['name']
            link = playlist['external_urls']['spotify']
            cover_image = playlist['images'][0]['url'] if playlist['images'] else 'No image available'
            
            print(f"{idx}. {title} - {link}")
            print(f"   Cover Image: {cover_image}")
            
            # 플레이리스트 정보를 PostgreSQL에 저장
            self.save_playlist_to_db(title, link, cover_image)
            
    def close_connection(self):
        """ PostgreSQL 연결 종료 """
        self.db_cursor.close()
        self.db_connection.close()

if __name__ == '__main__':
    spotipy_client = SpotifyClient()
    song_title = input("Enter song title: ")
    spotipy_client.find_playlists_by_song(song_title)
    spotipy_client.close_connection()  # 작업 후 연결 종료
