# [Backend] Dark Pattern Detector

## Introduction
이 레포지토리는 다크 패턴 탐지 및 교정 도구 "라이트가드(Light Guard)"의 백엔드 서버를 포함하고 있습니다.

## 다크 패턴이란?
다크 패턴(Dark Pattern)은 사업자가 자신의 이익을 위해 소비자의 착각, 실수, 비합리적인 지출 등을 유도하기 위해 의도한 웹이나 앱의 설계 또는 디자인을 의미합니다. 
예를 들어, 예약 과정에서 수수료 및 세금 등의 추가 비용을 숨기거나, 반복적인 압박으로 불필요한 상품을 구매하도록 유도하는 등의 방법이 있습니다. 
이 프로젝트는 이러한 다크 패턴을 식별하고 사용자에게 경고하여 기술 활용 불법 콘텐츠에 의한 피해를 경계하여 공정한 인터넷 환경을 조성하는 데 기여하고자 합니다.

## Setup
1. 레포지토리를 클론합니다:
    ```bash
    git clone https://github.com/pja9362/Dark-Pattern-Detector-Server-py.git
    cd Dark-Pattern-Detector-Server-py
    ```
    
2. 필요한 패키지를 설치합니다:
    ```bash
    pip install selenium 
    ```

3. 서버를 시작합니다:
    ```bash
    python manage.py runserver
    ```

## Architecture
![KakaoTalk_Photo_2024-06-01-00-19-02](https://github.com/pja9362/Dark-Pattern-Detector/assets/80195979/7aa5bb48-6f1e-472a-a04f-d1885b9e235e)

## Prototype
https://github.com/pja9362/Dark-Pattern-Detector/assets/80195979/dd28d6c9-8944-42b5-8cf8-d2661a5c70a7
