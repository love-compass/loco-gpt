import re
import json
from typing import List
import openai
from google.cloud import translate
from google.api_core.exceptions import AlreadyExists

openai.api_key = "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"

LOCO_SUFFIX_PROMPT = """"""

LOCO_ADDITIONAL_PROMPT = """It's the 100th day since I met my girlfriend. It's a very special day for us"""


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


def translate_en_to_ko(text, project_id="delta-coast-382412"):
    client = translate.TranslationServiceClient()


def clean_text(result: str) -> str:
    print("\n[Exception 1] preprocessing.")
    result = re.sub('\d. ' + '[a-zA-Z | *]*', 'ACTIVITY', result)

    if "ACTIVITY\n\nACTIVITY" in result:
        result = result.replace("ACTIVITY\n\nACTIVITY", "ACTIVITY")

    return result


def generating_route(meeting_time, parting_time, budget, place):
    LOCO_INSTRUCTION_RPOMPT = f"""Recommend a date course where meeting time is {meeting_time}, parting time is {parting_time}, budget is {budget}, and Meeting place is {place}.
    
    You should actively recommend names of place that exist in reality, what it actually costs, and describe about the location briefly.
    
    Output format: 
    
    ```
    ACTIVITY
    "activity_name": "Starbucks Yangjae Station Branch",
    "start_time": "2023-04-09T13:00:00",
    "end_time": "2023-04-09T15:00:00",
    "description": "Starbucks is the world's largest multinational coffee chain.",
    "budget": "10000"
    ```
    
    "activity_name" should be a place only.
    
    You must follow the Output format, Begin!:
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"{LOCO_INSTRUCTION_RPOMPT}"}],
        temperature=1.1,
        max_tokens=2048,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return response.choices[0].message.content


def change_route(parsed_result: List[str], change_idx_list: List[int], place: str) -> List[str]:
    for idx in range(len(parsed_result)):
        # str to dict
        parsed_result[idx] = "{" + parsed_result[idx] + "}"
        parsed_result[idx] = json.loads(parsed_result[idx])

        if idx in change_idx_list:
            LOCO_CHANGE_PROMPT = f"""Recommend a date course where MEETING TIME is {parsed_result[idx]['start_time']}, PARTING TIME is {parsed_result[idx]['end_time']}, and Meeting place is {place}.
                                 
                                 You should actively recommend names of place that exist in reality, what it actually costs, and describe about the location briefly.
                                 
                                 MEETING TIME and PARTING TIME must be adhered to. 
                                 
                                 Output format: 
                                 
                                 ```
                                 ACTIVITY
                                 "activity_name": "Starbucks Yangjae Station Branch",
                                 "start_time": "MEETING TIME",
                                 "end_time": "PARTING TIME",
                                 "description": "Starbucks is the world's largest multinational coffee chain.",
                                 "budget": "10000"
                                 ```
                                 
                                 "activity_name" should be a place only, meeting time and parting time are should be considered.
                                 
                                 You must follow the Output format, Begin!:
                                 """

            loco = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user",
                           "content": f"{LOCO_CHANGE_PROMPT}"}],
                temperature=1.1,
                max_tokens=2048,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            parsed_result[idx] = loco.choices[0].message.content
            # postprocessing
            parsed_result[idx] = re.sub('  +', '', parsed_result[idx])
            exception_pattern_1 = re.compile('\d. ' + '[a-zA-Z | *]*')

            """Exception 1"""
            if exception_pattern_1.match(parsed_result[idx]):
                parsed_result[idx] = clean_text(parsed_result[idx])

            """Exception 2"""
            exception_pattern_2 = re.compile(r"\"budget\": \"[a-zA-Z0-9]*\"")

            print("\n[Exception 2] preprocessing.")

            findall_budget = exception_pattern_2.findall(parsed_result[idx])
            chop_idx_from = parsed_result[idx].index(findall_budget[-1])
            chop_idx_to = len(findall_budget[-1])
            parsed_result[idx] = parsed_result[idx][:chop_idx_from + chop_idx_to]

            parsed_result[idx] = parsed_result[idx].replace("\n\n", "").replace("\n", "").replace("```", "").split("ACTIVITY")[1:][0]
            parsed_result[idx] = "{" + parsed_result[idx] + "}"
            parsed_result[idx] = json.loads(parsed_result[idx])

        # budget str -> int
        try:
            parsed_result[idx]["budget"] = int(parsed_result[idx]["budget"])
        except:
            parsed_result[idx]["budget"] = 0

    return parsed_result


def location_double_check(result):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": f"Make sure the places you recommend in {result} match actual location:"}],
        temperature=1.1,
        max_tokens=2048,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return response.choices[0].message.content


def init() -> None:
    LOCO_PREFIX_RPOMPT = """We are making LOCO, a dating application.

    LOCO aims to recommend the best dating route by receiving the Meeting and Parting time, Cost, and Approximate location as input.

    You must tell the user in detail where and what to do depending on the time of day.

    You should not provide virtual location information, but must present location information that exists in reality.

    You must not recommend physically impossible routes. For example, Human can not travel from Anam Station to Seoul Nat'l Univ. Station in 1 minutes. 

    You must not make recommendations beyond a given budget. For example, you shouldn't be recommending $10 spaghetti to your user if user's budget is only $5.

    You must create a date path strictly according to our instructions.

    Do you understand this task is?:"""

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
    else:
        exit(1)


def main():
    init()

    # input
    """example"""
    meeting_time = "2023-04-09T09:00:00"
    parting_time = "2023-04-09T18:00:00"
    place = "잠실/송파"
    budget = "100000"

    # preprocessing
    place = place_en_to_ko(place)
    budget += " Won"

    # generate schedule
    result = generating_route(meeting_time,
                              parting_time,
                              budget,
                              place)

    # postprocessing
    # remove multiple spaces
    result = re.sub('  +', '', result)
    print(result)
    print("---------------------------------------------------")

    """[Exception 1] OUTPUT FORMAT:
    ACTIVITY

    1. ~
    """
    exception_pattern_1 = re.compile('\d. ' + '[a-zA-Z | *]*')

    if exception_pattern_1.match(result):
        result = clean_text(result)

    """[Exception 2] UNINTENDED OUTPUT: 
    "budget": "39000"

    Total budget: 101000 Won <- THIS
    """
    exception_pattern_2 = re.compile(r"\"budget\": \"[a-zA-Z0-9]*\"")

    print("\n[Exception 2] preprocessing.")

    findall_budget = exception_pattern_2.findall(result)
    chop_idx_from = result.index(findall_budget[-1])
    chop_idx_to = len(findall_budget[-1])
    result = result[:chop_idx_from + chop_idx_to]
    print(result)

    print("---------------------------------------------------")

    # change activity
    """example"""
    change_idx_list = [0, 1]

    if change_idx_list: # not empty
        parsed_result = result.replace("\n\n", "").replace("\n", "").split("ACTIVITY")[1:]
        print("parsed_result: ", parsed_result)

        parsed_result = change_route(parsed_result, change_idx_list, place)

        for p in parsed_result:
            print(p)

        """translation"""


    print("------------------------------------------")


    # double check

if __name__ == "__main__":
    main()
