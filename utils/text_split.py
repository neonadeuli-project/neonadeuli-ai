def quiz(texts):
    problem = texts.split('\n')[0]
    options = texts.split('\n')[2:11:2]
    answer = texts.split('\n')[12][-2:]
    explane = texts.split('\n')[14]
    return {'problem':problem, 'options':options, 'answer':answer, "explane":explane}

def summary(texts:list):
    start_date = texts[0]
    end_date = texts[1]
    completions = texts[2].split('\n')[0]
    tags = texts[2].split('\n')[-1]
    text = f"""
    <style>
    @font-face {{
        font-family: 'NanumSquareNeo';
        src: url(https://hangeul.pstatic.net/hangeul_static/webfont/NanumSquareNeo/NanumSquareNeoTTF-bRg.eot);
        src: url(https://hangeul.pstatic.net/hangeul_static/webfont/NanumSquareNeo/NanumSquareNeoTTF-bRg.eot?#iefix) format("embedded-opentype"), url(https://hangeul.pstatic.net/hangeul_static/webfont/NanumSquareNeo/NanumSquareNeoTTF-bRg.woff) format("woff"), url(https://hangeul.pstatic.net/hangeul_static/webfont/NanumSquareNeo/NanumSquareNeoTTF-bRg.ttf) format("truetype");
    }}
    .custom-font {{
        font-family: 'NanumSquareNeo', sans-serif;
        font-size: 24px;
    }}
    </style>

    <div class='custom-font'> 

    <h1 align='center'>대화 요약</h1>

    채팅 시작일: {start_date}  

    채팅 종료일: {end_date}  

    <hr style="margin: 20px;">

    {completions}

    <hr style="margin: 20px;">

    <strong>{tags}</strong>
    </div>
    """
    return text