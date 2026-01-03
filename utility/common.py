from builtins import print as original_print, input as original_input
from pandas import DataFrame
from prettytable import PrettyTable

from ebest import ResponseValue

ext_print = None
ext_input = None
def set_ext_func(print_func, input_func):
    global ext_print
    global ext_input
    ext_print = print_func
    ext_input = input_func

async def ainput(prompt: str = "") -> str:
    if ext_input is not None:
        return await ext_input(prompt)
    return original_input(prompt)

def format_data_to_str(data):
    """데이터를 예쁜 표 모양의 문자열로 반환"""
    if data is None:
        return ""
    
    result = []
    
    if isinstance(data, str):
        return data
    
    elif isinstance(data, dict):
        table = PrettyTable(['key', 'value'])
        fields = list(data.items())
        table.add_rows([list(x) for x in fields])
        result.append(f'Field Count = {len(fields)}')
        result.append(table.get_string())
        
    elif isinstance(data, list):
        if len(data) == 0:
            return "[]"
        
        table = PrettyTable()
        if isinstance(data[0], dict):
            table.field_names = data[0].keys()
            table.add_rows([x.values() for x in data])
        else:
            table.field_names = ["value"]
            table.add_rows([[x] for x in data])
            
        result.append(f'Row Count = {len(data)}')
        result.append(table.get_string())
        
    elif isinstance(data, ResponseValue):
        result.append(f'tr_cont=\'{data.tr_cont}\', tr_cont_key=\'{data.tr_cont_key}\'')
        for key in data.body.keys():
            result.append(key)
            result.append(format_data_to_str(data.body[key])) # 재귀 호출
            
    else:
        return str(data)
        
    return "\n".join(result)

def format_data_to_dict(data):
    """ResponseValue나 DataFrame 같은 객체를 순수 dict/list 구조로 변환"""
    if isinstance(data, ResponseValue):
        return {
            "tr_cont": data.tr_cont,
            "tr_cont_key": data.tr_cont_key,
            "body": {k: format_data_to_dict(v) for k, v in data.body.items()}
        }
    elif isinstance(data, DataFrame):
        return data.to_dict(orient='records') # 리스트 형태의 딕셔너리로 변환
    elif isinstance(data, list):
        return [format_data_to_dict(item) for item in data]
    elif isinstance(data, dict):
        return {k: format_data_to_dict(v) for k, v in data.items()}
    else:
        return data

# prettytable을 사용하여 데이터를 표로 이쁘게 출력하는 함수
# 표준 print 함수를 대체하여 사용
def print(data, *values):
    if len(values) > 0:
        original_print(data, *values)
        return
    print_func = ext_print if ext_print is not None else original_print

    formatted_str = format_data_to_str(data)
    if formatted_str:
        print_func(formatted_str)

# prettytable을 사용하여 데이터를 표로 이쁘게 출력하는 함수
def print_table(data):
    if data is None: return
    if isinstance(data, dict):
        table = PrettyTable(['key','value'])
        fields = data.items();
        table.add_rows([list(x) for x in fields])
        print(f'Field Count = {len(fields)}')
        print(table)
    elif isinstance(data, list):
        if len(data) == 0: return
        if isinstance(data[0], dict):
            table = PrettyTable()
            table.field_names = data[0]
            table.add_rows([x.values() for x in data])
            print(f'Row Count = {len(data)}')
            print(table)
        else:
            table = PrettyTable(['value'])
            for x in data:
                table.add_row([x])
                pass
            print(f'Row Count = {len(data)}')
            print(table)
    elif isinstance(data, DataFrame):
        table = PrettyTable()
        table.field_names = data.columns
        table.add_rows(data.values)
        print(f'Row Count = {len(data)}')
        print(table)
    pass

# 데이터를 csv로 저장하는 함수
def TOHLCV_to_csv(file_path, data):
    # 데이터프레임 생성
    df = DataFrame(data)
    # 컬럼명 변경
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    # 파일 저장
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    pass

# csv 파일을 데이터프레임으로 변환하는 함수
def csv_to_TOHLCV(file_path):
    # 파일 읽기
    df = DataFrame.from_csv(file_path, encoding='utf-8-sig')
    # 데이터프레임을 리스트로 변환
    data = df.values.tolist()
    return data