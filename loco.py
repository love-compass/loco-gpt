import os
import re
import json
from typing import List, Dict
import openai
from google.cloud import translate

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "assets/b7f9.json"
openai.api_key = "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"


def place_en_to_ko(location: str) -> str:
    place_dict ={'강남/역삼/선릉': 'Gangnam / Yeoksam / Seolleung',
                 '강남구청': 'Gangnam-gu Office',
                 '개포/일원/수서': 'Gaepo/Irwon/Suseo',
                 '건대/군자/구의': 'Kondae/Gunja/Guui',
                 '금호/옥수': 'Kumho/Oksu',
                 '명동/을지로/충무로': 'Myeongdong/Euljiro/Chungmuro',
                 '방이': 'Bangi-dong',
                 '북촌/삼청': 'Bukchon/Samcheong',
                 '삼성/대치': 'Samsung/Daechi',
                 '상수/합정/망원': 'Sangsu/Hapjeong/Mangwon',
                 '서울역/회현': 'Seoul Station/Hoehyeon',
                 '서초/방배': 'Seocho/Bangbae',
                 '서촌': 'Seochon',
                 '선릉/삼성': 'Seolleung/Samsung',
                 '성수/뚝섬': 'Seongsu/Ttukseom',
                 '신사/논현': 'Sinsa/Nonhyeon',
                 '신촌/홍대/서교': 'Sinchon / Hongdae / Seogyo',
                 '압구정/청담': 'Apgujeong/Cheongdam',
                 '양재/도곡': 'Yangjae/Dogok',
                 '연남': 'Yeonnam',
                 '영동포/여의도': 'Yeongdongpo/Yeouido',
                 '용산/삼각지': 'Yongsan/Samgakji',
                 '이태원/한남': 'Itaewon/Hannam',
                 '잠실/송파': 'Jamsil/Songpa',
                 '종로/광화문': 'Jongno/Gwanghwamun',
                 '분당': 'Bundang-gu',
                 '수원/광교': 'Suwon/Gwanggyo',
                 '판교': 'Pangyo'}

    gyeonggido_list = ['Bundang-gu', 'Suwon/Gwanggyo', 'Pangyo']

    # gyeonggido-rization
    if place_dict[location] in gyeonggido_list:
        return place_dict[location] + ", GyeongGi-Do"
    else:
        return place_dict[location] + ", Seoul"


def translator(text: str, task: str, project_id="delta-coast-382412") -> str:
    client = translate.TranslationServiceClient()
    location = "us-central1"

    # 아까 지정한 용어집 이름과 같이 맞춰줘야 함
    glossary = client.glossary_path(project_id, location, 'loco_translator_glossary')
    glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)
    parent = f"projects/{project_id}/locations/{location}"

    # Translate text from English to Korean
    if task == 'ko-en':
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": "ko",
                "target_language_code": "en-US",
                "glossary_config": glossary_config,
            }
        )

        return response.glossary_translations[0].translated_text
    elif task == 'en-ko':
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": "en-US",
                "target_language_code": "ko",
                "glossary_config": glossary_config,
            }
        )

        return response.glossary_translations[0].translated_text
    else:
        pass

def translator_chatgpt(text: str, task: str) -> str:
    TRANSLATION_TASK_PROMPT = ""

    if task == 'ko-en':
        TRANSLATION_TASK_PROMPT = f"Translate {text} into English."
    elif task == 'en-ko':
        TRANSLATION_TASK_PROMPT = f"Translate {text} into Korean."
    else:
        pass

    LOCO_TRANSLATION_PROMPT = f"""{TRANSLATION_TASK_PROMPT}
    
    You should not translate the following words: ACTIVITY, "activity_name", "start_time", "end_time", "description", "budget".
    
    Begin!: 
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"{LOCO_TRANSLATION_PROMPT}."}],
        temperature=1.1,
        max_tokens=2048,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    result = response.choices[0].message.content

    return result


def init() -> None:
    LOCO_PREFIX_RPOMPT = """We are making LOCO, a dating application.

    LOCO aims to recommend the best dating route by receiving the Meeting and Parting time, Cost, and Approximate location as input.

    You must tell the user in detail where and what to do depending on the time of day.

    You should not provide virtual location information, but must present location information that exists in reality.

    You must not recommend physically impossible routes. For example, Human can not travel from Anam Station to Seoul Nat'l Univ. Station in 1 minutes. 

    You must not make recommendations beyond a given budget. For example, you shouldn't be recommending $10 spaghetti to your user if user's budget is only $5.
    
    You must create a date path strictly according to our instructions.

    Do you understand this task is?:"""

    while True:
        init_loco = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user",
                       "content": f"{LOCO_PREFIX_RPOMPT}"}],
            temperature=1.1,
            max_tokens=2048,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        print("---------------------------------------------------")
        print("\"Human\": Do you understand what this task is?")
        print("\"AI\":", init_loco.choices[0].message.content)

        if "yes" in init_loco.choices[0].message.content.lower():
            print("\"Human\": Great, Let's begin!")
            print("---------------------------------------------------")
            break
        else:
            continue


def postprocessing(result: str) -> str:
    """
    [Exception 1] OUTPUT FORMAT:
        ACTIVITY

        1. ~

    [Exception 1-1] "activity_name" not in result
        ACTIVITY

        1. "Lotte World Tower Observation Deck"

    [Exception 1-2] "ACTIVITY" not in result
        1. Breakfast at Bongchu Jjimdak (봉추찜닭) in Jamsil
        - "activity_name": "Bongchu Jjimdak (봉추찜닭)",

    [Exception 1-3] Variation 1-3
        ACTIVITY
        1. "activity_name": "Seoul Sky Observatory",

    [Exception 1-4] Variation 1-4
        ACTIVITY
        1. "Breakfast at Paul Bassett"


    [Exception 2] UNINTENDED OUTPUT:
        "budget": "39000"

        Total budget: 101000 Won <- THIS
    """

    # exception: 1-4
    activity_findall = re.compile(r'\d\. .*').findall(result)

    for a in activity_findall:
        if "activity_name" not in a:
            result = re.sub(a, '\nACTIVITY', result)

    # exception: 1-3
    if "ACTIVITY\n1. \"activity_name\"" in result:
        result = re.sub(r'\d\. ', 'ACTIVITY\n', result)

    exception_pattern_1 = re.compile(r'\d\. ' + '\"*[a-zA-Z| *|:|é|\"]*\"*')

    # exception: 1-1
    if "activity_name" not in result:
        activity_findall = exception_pattern_1.findall(result)

        for a in activity_findall:
            result = re.sub(exception_pattern_1, 'ACTIVITY\n\"activity_name\": ' + a, result)
            result = re.sub(r'\d\. ', "", result)

    # exception: 1-2
    if "ACTIVITY" not in result:
        activity_findall = exception_pattern_1.findall(result)

        for _ in activity_findall:
            result = re.sub(exception_pattern_1, 'ACTIVITY\n', result)
            result = re.sub(r'\d\. ', "", result)
            result = re.sub(r'\([^)]*\) *[a-zA-Z| *|가-힣]*', "", result)

    # exception: 1
    if exception_pattern_1.match(result):
        result = re.sub('\d\. ' + '[a-zA-Z | *]*', 'ACTIVITY', result)

    if "ACTIVITY\n\nACTIVITY" in result:
        result = result.replace("ACTIVITY\n\nACTIVITY", "ACTIVITY")

    if "ACTIVITY\nACTIVITY" in result:
        result = result.replace("ACTIVITY\nACTIVITY", "ACTIVITY")

    if "\n\nACTIVITY" in result:
        result = result.replace("\n\nACTIVITY", "\nACTIVITY")

    result = result.replace("- ", "")

    # exception: 2
    exception_pattern_2 = re.compile(r"\"budget\": \"[a-zA-Z0-9]*\"")

    findall_budget = exception_pattern_2.findall(result)

    if findall_budget: # not empty
        chop_idx_from = result.rfind(findall_budget[-1])
        chop_idx_to = len(findall_budget[-1])
        result = result[:chop_idx_from + chop_idx_to]

        return result
    else: # empty -> no error
        return result


def remove_verb(p: str) -> str:
    p = p.replace("Artistic exploration at ", "")
    p = p.replace("Breakfast at ", "")
    p = p.replace("Brunch at ", "")
    p = p.replace("Coffee at ", "")
    p = p.replace("Coffee and Cake at ", "")
    p = p.replace("Coffee and dessert at ", "")
    p = p.replace("Coffee break at ", "")
    p = p.replace("Dinner at ", "")
    p = p.replace("Explore ", "")
    p = p.replace("Go to ", "")
    p = p.replace("Hiking at ","")
    p = p.replace("Karaoke at ", "")
    p = p.replace("Lunch at ", "")
    p = p.replace("Night view at ", "")
    p = p.replace("Night view of ", "")
    p = p.replace("Picnic at ", "")
    p = p.replace("Riding the Cable Car at ", "")
    p = p.replace("Relax at ", "")
    p = p.replace("Shopping at ", "")
    p = p.replace("Shopping in ", "")
    p = p.replace("Stroll around ", "")
    p = p.replace("Tea time at ", "")
    p = p.replace("Visit ", "")
    p = p.replace("Visit to ", "")
    p = p.replace("Visiting ", "")
    p = p.replace("Virtual Reality Experience at ", "")
    p = p.replace("Walking tour of ", "")
    p = p.replace("Walking tour in ", "")
    p = p.replace("Walk in ", "")
    p = p.replace("Walk around ", "")

    return p


def change_route(meeting_time: str,
                 parting_time: str,
                 budget: str,
                 place: str,
                 user_request: str,
                 prior_places: List[str]) -> str:

    m_year, m_time = meeting_time.split("T")
    m_year = m_year.split('-')
    meeting_time = m_time.strip() + ", " + m_year[0] + "/" + m_year[1] + "/" + m_year[2]

    p_year, p_time = parting_time.split("T")
    p_year = p_year.split('-')
    parting_time = p_time.strip() + ", " + p_year[0] + "/" + p_year[1] + "/" + p_year[2]
    print(f"time: from {meeting_time} to {parting_time}, budget: {budget}, place: {place}")
    print("---------------------------------------------------")

    USER_REQUEST_PROMPT = ""

    # user_request: "가격이 너무 비싸요"
    if user_request:
        user_request = translator(user_request, task='ko-en')  # 'ko-en' or 'en-ko'
        USER_REQUEST_PROMPT = f"You should consider this message: {user_request}. "

    # prior_places: ['서울올림픽미술관', '꼬꼬춘천치킨', '코엑스 아쿠아리움', '스타필드 코엑스몰']
    if prior_places:
        temp_places = ""
        for idx, pp in enumerate(prior_places):
            if idx == len(prior_places) - 1:
                temp_places += translator(pp, task="ko-en")
            else:
                temp_places = temp_places + translator(pp, task="ko-en") + ", "
        USER_REQUEST_PROMPT += f"You must not include the following locations: {temp_places}"

    print("USER_REQUEST_PROMPT: ", USER_REQUEST_PROMPT)

    LOCO_INSTRUCTION_RPOMPT = f"""Plan a date from {meeting_time} to {parting_time}, budget is {budget}, and Meeting place is {place}.

    You should actively recommend names of place that exist in reality, what it actually costs.

    {USER_REQUEST_PROMPT}. You should recommend only one place and don't give me a choice.

    OUTPUT FORMAT: 

    ```
    ACTIVITY
    "activity_name": "Starbucks Yangjae Station Branch",
    "start_time": "2023-04-09T13:00:00",
    "end_time": "2023-04-09T15:00:00",
    "description": "Starbucks is the world's largest multinational coffee chain.",
    "budget": "10000"
    ```
    
    "activity_name" should be a place only and "description" should consist of one sentence
    """

    LOCO_SUFFIX_PROMPT = """You must follow the OUTPUT FORMAT, Begin!:"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"{LOCO_INSTRUCTION_RPOMPT}. {LOCO_SUFFIX_PROMPT}"}],
        temperature=1.1,
        max_tokens=2048,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    result = response.choices[0].message.content

    return result


def generate_route(meeting_time: str,
                   parting_time: str,
                   budget: str,
                   place: str,
                   user_request: str) -> str:

    m_year, m_time = meeting_time.split("T")
    m_year = m_year.split('-')
    meeting_time = m_time.strip() + ", " + m_year[0] + "/" + m_year[1] + "/" + m_year[2]

    p_year, p_time = parting_time.split("T")
    p_year = p_year.split('-')
    parting_time = p_time.strip() + ", " + p_year[0] + "/" + p_year[1] + "/" + p_year[2]
    print(f"time: from {meeting_time} to {parting_time}, budget: {budget}, place: {place}")
    print("---------------------------------------------------")

    USER_REQUEST_PROMPT = ""

    # user_request: "가격이 너무 비싸요"
    if user_request:
        user_request = translator(user_request, task='ko-en')  # 'ko-en' or 'en-ko'
        USER_REQUEST_PROMPT = f"You should consider this message: {user_request}. "

    # date time <= 2 hours -> recommend a place
    SINGLE_PLACE_PROMPT = ""

    if int(p_time.split(":")[0]) - int(m_time.split(":")[0]) <= 3:
        SINGLE_PLACE_PROMPT = "If date time is less than 2 hours, you recommend only one place. Do not give me a choice."

    LOCO_INSTRUCTION_RPOMPT = f"""Plan a date from {meeting_time} to {parting_time}, budget is {budget}, and Meeting place is {place}.

    You should actively recommend names of place that exist in reality, what it actually costs. 
    
    {USER_REQUEST_PROMPT}. {SINGLE_PLACE_PROMPT}
    
    OUTPUT FORMAT: 

    ```
    ACTIVITY
    "activity_name": "Starbucks Yangjae Station Branch",
    "start_time": "2023-04-09T13:00:00",
    "end_time": "2023-04-09T15:00:00",
    "description": "Starbucks is the world's largest multinational coffee chain.",
    "budget": "10000"
    ```
    
    "activity_name" should be a place only, "budget" should be only numbers and "description" should consist of one sentence
    """

    LOCO_SUFFIX_PROMPT = """You must follow the OUTPUT FORMAT, Begin!:"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"{LOCO_INSTRUCTION_RPOMPT}. {LOCO_SUFFIX_PROMPT}"}],
        temperature=1.1,
        max_tokens=2048,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    result = response.choices[0].message.content

    return result


class LOCO:
    def __init__(self):
        print("Initializing LOCO")
        # init()

    def inference(self,
                  meeting_time: str,
                  parting_time: str,
                  place: str,
                  budget: int,
                  user_request: str,
                  prior_places: List[str]) -> List[Dict]:

        # preprocessing
        place = place_en_to_ko(place)
        budget = str(budget) + " Won"

        if prior_places: # user-requested try (not empty)
            print("Change a meeting place")
            print("---------------------------------------------------")
            # change a meeting place
            result = change_route(meeting_time,
                                  parting_time,
                                  budget,
                                  place,
                                  user_request,
                                  prior_places)
        else: # first try
            # generate schedule
            print("Generate Routes")
            result = generate_route(meeting_time,
                                    parting_time,
                                    budget,
                                    place,
                                    user_request)

        print(result)
        print("---------------------------------------------------")
        # remove multiple spaces
        result = re.sub('  +', '', result)

        # main postprocessing
        result = postprocessing(result)

        # e.g., ACTIVITY 1 -> ACTIVITY
        result = re.sub(r'ACTIVITY ' + '[0-9]+', 'ACTIVITY', result)

        # e.g., ACTIVITY 1: OR ACTIVITY1: OR ACTIVITY: OR ACTIVITY : -> ACTIVITY
        result = re.sub(r'ACTIVITY' + '[0-9| ]*:', 'ACTIVITY', result)

        # remove (SOMETHING)
        result = re.sub(re.compile(r'\([^)]*\) *'), "", result)

        # remove #
        # e.g., "budget": "0" # free admission -> "budget": "0"
        result = re.sub(re.compile(r'# *.*'), "", result)

        # remove . , -gu, -dong, and high-quality (json issue)
        result = result.replace(".", "")
        result = result.replace("high-quality", "high quality")
        result = result.replace("-gu", " gu")
        result = result.replace("-dong", " dong")

        print(result)
        print("---------------------------------------------------")

        # split paragraph
        parsed_result = result.replace("\n\n", "").replace("\n", "").split("ACTIVITY")[1:]

        # remove verb from activity, translate en to ko, and json formatting
        parsed_result = [json.loads("{" + translator(remove_verb(p), task='en-ko') + "}") for p in parsed_result]
        # parsed_result = [json.loads("{" + p.replace("Lunch at ", "").replace("Dinner at ", "") + "}") for p in parsed_result]

        # budget; str to int
        for idx in range(len(parsed_result)):
            try:
                parsed_result[idx]["budget"] = int(parsed_result[idx]["budget"])
            except:
                parsed_result[idx]["budget"] = 0

        return parsed_result

