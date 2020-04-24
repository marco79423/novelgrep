class APIError(Exception):
    code = ''
    message = ''

    @classmethod
    def serialize(cls):
        return {
            'code': cls.code,
            'message': cls.message
        }


class InvalidFormatError(APIError):
    code = '400-000'
    message = '格式不合法'


class TargetExistedError(APIError):
    code = '400-001'
    message = '目標已存在'


class DatabaseError(APIError):
    code = '500-001'
    message = '資料庫錯誤'
