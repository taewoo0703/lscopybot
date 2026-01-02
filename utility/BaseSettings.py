import os
from dataclasses import dataclass, fields
from dotenv import load_dotenv
from typing import get_type_hints
import json

@dataclass
class BaseSettings:
    """
    환경 변수를 로드하고, 필드의 타입 힌트에 따라 타입 변환을 수행.
    타입 힌트가 없으면 기본적으로 문자열(str)로 처리.
    """
    def __post_init__(self):
        if load_dotenv():  # .env 파일 로드
            type_hints = get_type_hints(self.__class__)  # 타입 힌트를 가져옴
            for field in fields(self):  # 클래스 필드 순회
                env_value = os.getenv(field.name)  # 환경 변수 값 가져오기
                if env_value is not None:  # 환경 변수가 설정된 경우
                    # 필드의 타입 힌트를 확인하고 변환
                    target_type = type_hints.get(field.name, str)  # 타입 힌트 없으면 str 기본값
                    converted_value = self._convert_value(env_value, target_type)
                    setattr(self, field.name, converted_value)

    def _convert_value(self, value: str, target_type):
        """
        타입 힌트에 따라 값을 변환. 힌트가 없으면 문자열로 반환.
        """
        if target_type in {float, float|None}:
            return float(value)
        elif target_type in {int, int|None}:
            return int(value)
        elif target_type in {bool, bool|None}:
            return self._str_to_bool(value)
        elif target_type in {str, str|None}:
            return value
        elif target_type in {list, list[str], list[str]|None}:
            return json.loads(value)
        elif target_type is None or target_type == type(None):
            return None
        else:
            raise ValueError(f"Unsupported target type: {target_type}")

    @staticmethod
    def _str_to_bool(value: str) -> bool | None:
        """
        문자열을 boolean으로 변환. True/False로 인식할 값들을 처리.
        """
        true_values = {"1", "true", "True", "TRUE"}
        false_values = {"0", "false", "False", "FALSE", "None", "none", ""}
        if value in true_values:
            return True
        elif value in false_values:
            return False
        else:
            return None