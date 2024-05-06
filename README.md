# Calibre NAVER OpenAPI Metadata Source Plugin

NAVER OpenAPI를 이용한 캘리버 메타데이터 다운로드 플러그인

## 설치 방법
1. [네이버 개발자 센터](https://developers.naver.com/main/)에서 API를 발급
    - 사용 API는 "검색" 선택
    - 발급 후 Client ID와 Client Secret 메모
2. `__init__.py` 파일을 열고 `API_ID`에는 Client ID를 `API_KEY`에는 Client Secret를 적어둔다.
3. `__init__.py` 파일을 압축 후 Calibre에서 플러그인을 등록한다.
4. 메타데이터 편집하기에서 메타데이터 다운로드를 클릭하면 책 정보와 책 표지를 받아오게 된다.

### 참고사항
- calibre 7.10에서 테스트되었습니다.
- 언어는 한국어로 고정되어 있습니다.