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
        concert_name = row['concertId']
        # 공연 특성 값들을 가져와서 float 리스트로 변환
        features = [float(row[col]) for col in row if col != 'concertId']
        concerts.append((concert_name, features))
    return concerts

# CSV 파일에서 사용자 데이터 읽기 (S3에서 가져오기)
def read_specific_concert_data(concert_id, bucket_name, folder_name, concert_file):

    # S3에서 CSV 파일 읽기
    csv_data = get_csv_from_s3(bucket_name, folder_name, concert_file)
    
    if csv_data is None:
        return None

    # 사용자 ID에 해당하는 특성 값 추출
    for row in csv_data:
        if row['concertId'] == concert_id:
            # 사용자 ID 제외하고 특성 값만 가져오기
            concert_feature = [float(row[col]) for col in row if col != 'concertId']
            return concert_feature
    return None


# CSV 파일에서 사용자 데이터 읽기 (S3에서 가져오기)
def read_user_features(user_id, bucket_name, folder_name, user_file):

    # S3에서 CSV 파일 읽기
    csv_data = get_csv_from_s3(bucket_name, folder_name, user_file)
    
    if csv_data is None:
        return None

    # 사용자 ID에 해당하는 특성 값 추출
    for row in csv_data:
        if row['userId'] == user_id:
            # 사용자 ID 제외하고 특성 값만 가져오기
            user_features = [float(row[col]) for col in row if col != 'userId']
            return user_features
    return None

def recommend_similar_concerts_user(user_id, top_n):

    top_n = int(top_n)

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


def recommend_similar_users(target_user_id, top_n=1):
    # S3 파일 경로 설정
    user_file = 'users.csv'
    bucket_name = 'claco-bucket'
    folder_name = 'datasets'

    # CSV 파일에서 모든 유저 데이터 가져오기
    all_users = []
    csv_data = get_csv_from_s3(bucket_name, folder_name, user_file)
    for row in csv_data:
        user_id = row['userId']
        user_features = [float(row[col]) for col in row if col != 'userId']
        all_users.append((user_id, user_features))

    # 타겟 유저 특징 가져오기
    target_features = read_user_features(target_user_id, bucket_name, folder_name, user_file)

    # 유사도 계산 및 정렬
    recommendations = []
    for other_user_id, other_features in all_users:
        if other_user_id == target_user_id:
            continue

        # 코사인 유사도 계산
        similarity = cosine_similarity(np.array(target_features).reshape(1, -1), 
                                      np.array(other_features).reshape(1, -1))[0][0]
        recommendations.append((other_user_id, similarity))

    # 유사도가 높은 순으로 정렬
    recommendations.sort(key=lambda x: x[1], reverse=True)

    # 상위 N명의 유사한 유저 추천
    return recommendations[:top_n]