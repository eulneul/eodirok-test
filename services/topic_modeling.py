from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from konlpy.tag import Okt
import re

class TopicExtractor:
    def __init__(self, stop_words_file):
        """
        TopicExtractor 클래스 초기화

        Args:
            stop_words_file (str): 불용어 파일 경로
        """
        with open(stop_words_file, 'r', encoding='utf-8') as file:
            self.stop_words = [line.strip() for line in file]
        self.okt = Okt()

    def preprocess_text(self, text):
        """
        텍스트 전처리:
        1. 특수문자 제거
        2. 형태소 분석 및 명사 추출
        3. 불용어 제거

        입력 파라미터:
            text (str): 입력 텍스트

        반환된 결과:
            str: 전처리된 텍스트
        """
        # 특수문자 제거
        text = re.sub(r'[^가-힣\s]', '', text)

        # 형태소 분석 (명사만 추출)
        tokens = self.okt.nouns(text)

        # 불용어 제거
        tokens = [word for word in tokens if word not in self.stop_words]

        # 토큰을 공백으로 연결하여 반환
        return ' '.join(tokens)

    def extract_topics(self, input_text, num_topics=1):
        """
        LDA 기반 주제 추출

        입력 파라미터:
            input_text (str): 입력 텍스트
            num_topics (int): 추출할 주제 개수

        반환된 결과:
            list: 추출된 주제 리스트
        """
        # 입력 텍스트 전처리
        processed_text = self.preprocess_text(input_text)

        # 문서를 리스트 형태로 변환
        documents = [processed_text]

        # CountVectorizer로 텍스트 벡터화
        vectorizer = CountVectorizer(max_df=1.0, min_df=1, stop_words=None)
        dtm = vectorizer.fit_transform(documents)

        # LDA 모델 초기화
        lda = LatentDirichletAllocation(n_components=num_topics, random_state=0)
        lda.fit(dtm)

        # 주제 추출
        topics = []
        for idx, topic in enumerate(lda.components_):
            top_words = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-5:]]
            topics.append("/".join(top_words))

        return topics

"""
# 불용어 파일 경로
stop_words_file = 'server/services/stop_word.txt'

# TopicExtractor 클래스 초기화
topic_extractor = TopicExtractor(stop_words_file)

# 입력 텍스트1
input_text = "안녕하세요! 고객사로부터 전달받은 데이터와 관련하여, 통합과 전처리를 진행하였습니다! 감사합니다!"

# 주제 추출
topics = topic_extractor.extract_topics(input_text, num_topics=1)

print("추출된 주제:", topics)
"""