import csv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# CSV 파일에서 공연 데이터 읽기
def read_concert_data(file_name):
    concerts = []
    with open(file_name, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            concert_name = row['Performance Name']
            # 공연 특성 값들을 가져와서 float 리스트로 변환
            features = [float(row[col]) for col in row if col != 'Performance Name']
            concerts.append((concert_name, features))
    return concerts

# CSV 파일에서 사용자 데이터 읽기
def read_user_features(user_id, file_name):
    with open(file_name, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['User Id'] == user_id:
                # 사용자 ID 제외하고 특성 값만 가져오기
                user_features = [float(row[col]) for col in row if col != 'User Id']
                return user_features
    return None

def recommend_similar_concerts(user_id, user_file, csv_file, top_n=3):
    # 사용자 특성 값 가져오기
    user_features = read_user_features(user_id, user_file)
    if user_features is None:
        print(f"User ID {user_id} not found.")
        return []

    # CSV 파일에서 공연 데이터 가져오기
    concerts = read_concert_data(csv_file)
    
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

# 파일 경로 설정
user_file = 'datasets/users.csv'
concert_file = 'datasets/concerts.csv'

# 사용자 ID를 입력으로 받아 공연 추천
user_id = '1'  # 예시 사용자 ID

recommended_concerts = recommend_similar_concerts(user_id, user_file, concert_file)

# 추천 결과 출력
print("Recommended Concerts:")
for concert_name, similarity in recommended_concerts:
    print(f"{concert_name}: Similarity = {similarity:.2f}")
