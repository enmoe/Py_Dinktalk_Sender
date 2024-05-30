import sys
import os
import requests
from typing import List
from alibabacloud_dingtalk.robot_1_0.client import Client as DingtalkRobotClient
from alibabacloud_tea_openapi import models as OpenApiModels
from alibabacloud_dingtalk.robot_1_0 import models as DingtalkRobotModels
from alibabacloud_tea_util import models as UtilModels
from alibabacloud_tea_util.client import Client as UtilClient

def create_dingtalk_client() -> DingtalkRobotClient:
    """创建DingtalkRobotClient实例"""
    config = OpenApiModels.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    return DingtalkRobotClient(config)

def build_file_param(media_id: str, file_name: str, file_type: str) -> str:
    """构建file_param字符串"""
    return f'{{"mediaId":"{media_id}","fileName":"{file_name}","fileType":"{file_type}"}}'

def send_dingtalk_file(client: DingtalkRobotClient, access_token: str, file_param: str, file_key: str, robot_code: str, conversation_id: str):
    """发送Dingtalk文件消息"""
    headers = DingtalkRobotModels.OrgGroupSendHeaders()
    headers.x_acs_dingtalk_access_token = access_token
    request = DingtalkRobotModels.OrgGroupSendRequest(
        msg_param=file_param,
        msg_key=file_key,
        robot_code=robot_code,
        open_conversation_id=conversation_id
    )
    try:
        client.org_group_send_with_options(request, headers, UtilModels.RuntimeOptions())
    except Exception as err:
        print(f"发送文件消息失败: {err}")
        raise  # 抛出异常，让调用者处理

def upload_file(access_token: str, file_path: str, file_name: str) -> str:
    """上传文件并获取media_id"""
    files = {'media': open(os.path.join(file_path, file_name), 'rb')}
    url = f'https://oapi.dingtalk.com/media/upload?access_token={access_token}'
    data = {'type': 'file'}
    response = requests.post(url, files=files, data=data)
    response.raise_for_status()  # 确保请求成功
    return response.json()['media_id']

def get_access_token(app_key: str, app_secret: str) -> str:
    """获取访问令牌"""
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    payload = {
        "appKey": app_key,
        "appSecret": app_secret
    }
    headers = {
        'Content-Type': "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # 确保请求成功
    return response.json()["accessToken"]

def main(ak_sk_string: str):
    """主函数"""
    app_key, app_secret, robot_id, conversation_id ,file_type ,full_file_path = ak_sk_string.split(',')
    file_path, file_name = os.path.split(full_file_path)
    
    token_info = get_access_token(app_key, app_secret)
    if not token_info:
        print("无法获取访问令牌。", file=sys.stderr)
        exit(1)
    
    media_id = upload_file(token_info, file_path, file_name)
    
    # 假设已经获得了file_type，这里只是示例，实际情况需要根据具体文件确定
    file_type = file_type
    robot_id=robot_id
    conversation_id=conversation_id
    
    dingtalk_client = create_dingtalk_client()
    file_param = build_file_param(media_id, file_name, file_type)
    send_dingtalk_file(dingtalk_client, token_info, file_param, 'sampleFile', robot_id, conversation_id)

    print(token_info + "," + file_path + "," + file_name + "," + media_id)

if __name__ == "__main__":
    ak_sk_string = sys.argv[1]
    main(ak_sk_string)

    

'''

使用方法
export app_key=''
export app_secret=''
export robot_id=''
export conversation_id=''
export file_type=''
export full_file_path=''

python3 Get_Dingtalk_Access_Token.py "$app_key,$app_secret,$robot_id,$conversation_id,$file_type,$full_file_path"

'''

