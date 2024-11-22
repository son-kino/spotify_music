import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
from spotify_class import SpotifyClient


def extract_data_from_spotify(song_title):
    """ Spotify에서 추천곡을 가져오는 함수 """
    spotify_client = SpotifyClient()
    return spotify_client.find_playlists_by_song(song_title)


def load_data_to_db(playlist_data):
    """ 데이터베이스에 데이터 로드 """
    if not playlist_data:
        print("No data to load.")
        return

    # Postgres 연결 설정 (PostgresHook 사용)
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')  # Airflow에서 설정한 연결 ID 사용
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    # 기존 playlists 테이블 드롭
    cursor.execute("DROP TABLE IF EXISTS spotify_playlist")

    # playlists 테이블 생성 (no는 SERIAL PK로 설정)
    create_table_query = """
    CREATE TABLE spotify_playlist (
        no SERIAL PRIMARY KEY,
        title VARCHAR(256),
        link VARCHAR(256),
        cover_image VARCHAR(256)
    )
    """
    cursor.execute(create_table_query)

    # 데이터를 playlists 테이블에 삽입
    for playlist in playlist_data:
        insert_query = """
        INSERT INTO spotify_playlist (title, link, cover_image)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (playlist['title'], playlist['link'], playlist['cover_image']))


    conn.commit()
    cursor.close()
    conn.close()


# Airflow DAG 정의
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 11, 22),  # 원하는 시작 날짜 설정
}

dag = DAG(
    'spotify_etl_dag_playlist',  # DAG 이름
    default_args=default_args,
    description='ETL for Spotify Playlists',
    schedule_interval='@daily',  # 매일 실행되도록 설정
)

# Airflow Task 정의
def run_etl(song_title):
    playlist_data = extract_data_from_spotify(song_title)
    load_data_to_db(playlist_data)

# DAG 안에서 Task 연결
song_title = 'Shape of You'  # Django를 airflow Variable로 받아오기
etl_task = PythonOperator(
    task_id='spotify_etl_task_playlist',
    python_callable=run_etl,
    op_args=[song_title],
    dag=dag,
)

etl_task
