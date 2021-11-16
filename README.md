# Twitter Archive Eraser

## 사용법

1. 다운로드 받은 아카이브 압축 파일을 열어 data 폴더 안에 있는 tweet.js 파일만 압축 해제합니다.</br>(파일명 예시: twitter-2021-06-29-94c57babf6d6cb394004ccfdce15da24e44a46066b9ead31c48fd7059d02a8e8.zip)
2. 압축 해제한 파일을 archive-eraser.exe 파일과 동일한 위치에 둡니다.
    - tweet.js 파일 예시
    ```javascript
    window.YTD.tweet.part0 = [
    {
        "tweet" : {
          "retweeted" : false,
          "source" : "<a href=\"https://mobile.twitter.com\" rel=\"nofollow\">Twitter Web App</a>",
          "entities" : {
            "hashtags" : [ ],
            "symbols" : [ ],
            "user_mentions" : [ ],
            "urls" : [ ]
          },
          "display_text_range" : [
            "0",
            "22"
          ],
          "favorite_count" : "0",
          "id_str" : "1417481148444430349",
          "truncated" : false,
          "retweet_count" : "0",
          "id" : "1417481148444430349",
          "created_at" : "Tue Jul 20 13:46:55 +0000 2021",
          "favorited" : false,
          "full_text" : "그럼 얼굴 갈아엎게해줘!!!!!!!!!!",
          "lang" : "ko"
        }
      },
    ]
    ```

3. 명령 프롬프트 창을 열고 archive-eraser.exe를 실행시킵니다.

- Runtime Options
    - --threads: 프로그램을 실행할 쓰레드 수를 정합니다.(최대 64쓰레드)
    - --file: tweet.js 파일의 위치를 지정합니다.

## License
- AGPLv3+
