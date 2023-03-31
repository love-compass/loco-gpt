import json
from typing import List
import openai


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


def generating_route(meeting_time, parting_time, budget, place):
    LOCO_INSTRUCTION_RPOMPT = f"""Recommend a date course where meeting time is {meeting_time}, parting time is {parting_time}, budget is {budget}, and Meeting place is {place}.
    
    You should actively recommend names of place that exist in reality and describe about the location briefly.
    
    Output format: 
    
    ```
    ACTIVITY
    "activity_name": "Starbucks Yangjae Station Branch",
    "start_time": "2023-04-09T13:00:00",
    "end_time": "2023-04-09T15:00:00",
    "description": "Starbucks is the world's largest multinational coffee chain.",
    "budget" "Ice Americano is around 5000 Won"
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


def change_course(result: str, place: str) -> List[str]:
    activity = json.loads(result)

    LOCO_CHANGE_PROMPT = f"""Recommend a date course where meeting time is {activity['start_time']}, parting time is {activity['end_time']}, and Meeting place is {place}.
                         
                         You should actively recommend names of place that exist in reality and describe about the location briefly.
                         
                         Output format: 
                         
                         ```
                         ACTIVITY
                         "activity_name": "Starbucks Yangjae Station Branch",
                         "start_time": "2023-04-09T13:00:00",
                         "end_time": "2023-04-09T15:00:00",
                         "description": "Starbucks is the world's largest multinational coffee chain.",
                         "budget" "Ice Americano is around 5000 Won"
                         ```
                         
                         "activity_name" should be a place only, meeting time and parting time are should be fixed.
                         
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

    result = loco.choices[0].message.content

    return result


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

    result = result.replace("    ", "").strip()
    print(result)
    print(" ")

    # change activity
    """example"""
    change_idx_list = [0, 1]

    if change_idx_list: # not empty
        parsed_result = result.replace("\n\n", "").replace("\n", "").split("ACTIVITY")[1:]
        print("parsed_result: ", parsed_result)

        for idx in range(len(parsed_result)):
            parsed_result[idx] = "{" + parsed_result[idx] + "}"
            print(parsed_result[idx])

            if idx in change_idx_list:
                parsed_result[idx] = change_course(parsed_result[idx], place)
                parsed_result[idx] = parsed_result[idx].replace("\n\n", "").replace("\n", "").split("ACTIVITY")[1:][0]
                print("changed: ", parsed_result[idx])

        print("parsed_result: ", parsed_result)
        # print(" ")
        # result = change_course(parsed_result, change_idx_list, place)
        #
        # print("-----------------------------------------------------------")
        # print("".join(result))

    # double check
    # translation


if __name__ == "__main__":
    main()
