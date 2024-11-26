import os
import spotipy
from airflow.models import Variable
from spotipy.oauth2 import SpotifyOAuth
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from spotify_class import SpotifyClient
import psycopg2

def extract_data_from_spotify():
    """ Spotify에서 추천곡을 가져오는 함수 """
    spotify_client = SpotifyClient()
    today_playlists_data = spotify_client.get_top_10_playlists()
    return today_playlists_data

def load_data_to_db(today_playlists_data):
    """ 데이터베이스에 데이터 로드 """
    if not today_playlists_data:
        print("No data to load.")
        return

    pg_hook = PostgresHook(postgres_conn_id='playlist')  # 연결 ID 사용
    conn_tmp = pg_hook.get_connection(pg_hook.postgres_conn_id)
    # 직접 psycopg2로 연결하고 인코딩을 설정
    conn = psycopg2.connect(
        host=conn_tmp.host,
        database=conn_tmp.schema,
        user=conn_tmp.login,
        password=conn_tmp.password,
        port=conn_tmp.port,
        client_encoding='UTF8'  # 인코딩 설정
    )
    cursor = conn.cursor()

    # 기존 songs 테이블 드롭
    cursor.execute("DROP TABLE IF EXISTS playlist_schema.spotify_today_playlists")

    # songs 테이블 생성 (no는 SERIAL PK로 설정)
    create_table_query = """
    CREATE TABLE playlist_schema.spotify_today_playlists (
        no SERIAL PRIMARY KEY,
        title VARCHAR(256),
        link VARCHAR(256),
        cover_image VARCHAR(256)
    )
    """
    cursor.execute(create_table_query)

    # 유튜브 추천 검색을 위한 return list
    recommand_list = []
    # 데이터를 songs 테이블에 삽입
    for song in today_playlists_data:
        insert_query = """
        INSERT INTO playlist_schema.spotify_today_playlists (title, link, cover_image)
        VALUES (%s, %s, %s)
        """
        recommand_list.append(song)
        cursor.execute(insert_query, (song['title'], song['link'], song['cover_image']))

    conn.commit()
    cursor.close()
    conn.close()
    return 


# def get_top_10_playlists(self):
#     # 'Top'이라는 키워드로 플레이리스트 검색
#     results = self.sp.search(q="Top", type='playlist', limit=10)

#     if not results['playlists']['items']:
#         print("No playlists found.")
#         return

#     print(f"Top 10 playlists:")
#     for idx, playlist in enumerate(results['playlists']['items'], 1):
#         playlist_name = playlist['name']
#         playlist_url = playlist['external_urls']['spotify']
#         playlist_cover_url = playlist['images'][0]['url'] if playlist['images'] else 'No image available'
        
#         print(f"{idx}. {playlist_name} - {playlist_url}")
#         print(f"   Cover Image: {playlist_cover_url}")

# Airflow DAG 정의
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2023, 11, 22),  # 원하는 시작 날짜 설정
}

dag = DAG(
    'spotify_etl_dag_today_playlists',  # DAG 이름
    default_args=default_args,
    description='ETL for Spotify today playlists',
    schedule_interval='@daily', 
)

# Airflow Task 정의
def run_etl():
    today_play_list_data = extract_data_from_spotify()
    load_data_to_db(today_play_list_data)

# DAG 안에서 Task 연결
etl_task = PythonOperator(
    task_id='spotify_etl_task_today_playlists',
    python_callable=run_etl,
    dag=dag,
)

etl_task
