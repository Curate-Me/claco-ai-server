import csv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from infra.s3 import get_csv_from_s3
import io

# CSV 파일에서 공연 데이터 읽기 (S3에서 가져오기)
def read_concert_data(bucket_name, folder_name, concert_file):

    concerts = []
    # S3에서 CSV 파일 읽기
    csv_data = get_csv_from_s3(bucket_name, folder_name, concert_file)
    
    if csv_data is None:
        return concerts

    # CSV 데이터 파싱
    for row in csv_data:
        concert_name = row['Performance Id']
        # 공연 특성 값들을 가져와서 float 리스트로 변환
        features = [float(row[col]) for col in row if col != 'Performance Id']
        concerts.append((concert_name, features))
    return concerts

# CSV 파일에서 사용자 데이터 읽기 (S3에서 가져오기)
def read_user_features(user_id, bucket_name, folder_name, user_file):

    # S3에서 CSV 파일 읽기
    csv_data = get_csv_from_s3(bucket_name, folder_name, user_file)
    
    if csv_data is None:
        return None

    # 사용자 ID에 해당하는 특성 값 추출
    for row in csv_data:
        if row['User Id'] == user_id:
            # 사용자 ID 제외하고 특성 값만 가져오기
            user_features = [float(row[col]) for col in row if col != 'User Id']
            return user_features
    return None

def recommend_similar_concerts(user_id, top_n=5):

    # S3 파일 경로 설정
    user_file = 'users.csv'
    concert_file = 'concerts.csv'
    bucket_name = 'claco-bucket'
    folder_name = 'datasets'

    # 사용자 특성 값 가져오기
    user_features = read_user_features(user_id, bucket_name, folder_name, user_file)
    if user_features is None:
        print(f"User ID {user_id} not found.")
        return []

    # CSV 파일에서 공연 데이터 가져오기
    concerts = read_concert_data(bucket_name, folder_name, concert_file)
    
    user_features = np.array(user_features, dtype=float).reshape(1, -1)

    # 유사도 계산 및 정렬
    recommendations = []
    for concert_name, concert_features in concerts:
        concert_features = np.array(concert_features).reshape(1, -1)
        # 코사인 유사도 계산
        similarity = cosine_similarity(user_features, concert_features)[0][0]
        recommendations.append((concert_name, similarity))

    # 유사도 높은 순으로 정렬
    recommendations.sort(key=lambda x: x[1], reverse=True)

    # 상위 N개의 공연 추천
    return recommendations[:top_n]

