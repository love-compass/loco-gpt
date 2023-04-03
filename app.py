from flask import Flask, jsonify
from flask import request
app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello():
    return jsonify(
        hello = "hello world"
    )

@app.route("/course/full",methods=['POST'])
def getFullCourseRequest():
    params = request.get_json()
    print(params['question'], params['start_time'], params['end_time'], params['budget'], params['place'])
    result = [{
        "activity_name": "경복궁",
        "start_time": "2023-04-10T10:00:00",
        "end_time": "2023-04-10T11:00:00",
        "description": "경복궁은 1395년에 처음 지어진 역사적인 사이트입니다. 서울에서 가장 상징적인 랜드마크 중 하나로, 한국의 전통적인 아름다움을 대표합니다.",
        "budget": 1000
        },{
        "activity_name": "카페 노티드 안국",
        "start_time": "2023-04-10T12:00:00",
        "end_time": "2023-04-10T13:00:00",
        "description": "노티드 안국에서 유명한 맛있는 도넛집입니다.",
        "budget": 20000
    }]
    '''
    :params
    Should give dictionary
    
    result = List of {
        activity_name: String,
        start_time: String,
        end_time: String,
        description: String,
        budget: Long    }
    '''

    return jsonify(
        result = result
    )

@app.route("/course",methods=['POST'])
def getSimpleCourseRequest():
    params = request.get_json()
    print(params['prior_activity_name'], params['place'], params['start_time'], params['end_time'], params['question'])
    return jsonify(
        activity_name = "경복궁",
        start_time = "2022-12-10T09:10:00",
        end_time = "2022-12-10T11:10:00",
        description = "경복궁은 1395년에 처음 지어진 역사적인 사이트입니다. 서울에서 가장 상징적인 랜드마크 중 하나로, 한국의 전통적인 아름다움을 대표합니다.",
        budget = 120000
    )

if __name__ == "__main__":
    app.run()