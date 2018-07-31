# import bandwidth
# import os
# import pymongo
#
#
# #os.environ['BANDWIDTH_USER_ID'], os.environ['BANDWIDTH_API_TOKEN'],os.environ['BANDWIDTH_API_SECRET']
# user_id = os.environ['BANDWIDTH_USER_ID']
# api_token = os.environ['BANDWIDTH_API_TOKEN']
# api_secret = os.environ['BANDWIDTH_API_SECRET']
#
#
# voice_api = bandwidth.client('voice', user_id, api_token, api_secret)
# messaging_api = bandwidth.client('messaging',  user_id, api_token, api_secret)
# account_api = bandwidth.client('account',  user_id, api_token, api_secret)
#
#
# # voice_api = bandwidth.client('voice', os.environ['BANDWIDTH_USER_ID'], os.environ['BANDWIDTH_API_TOKEN'],os.environ['BANDWIDTH_API_SECRET'])
# # messaging_api = bandwidth.client('messaging', os.environ['BANDWIDTH_USER_ID'], os.environ['BANDWIDTH_API_TOKEN'],os.environ['BANDWIDTH_API_SECRET'])
# # account_api = bandwidth.client('account', os.environ['BANDWIDTH_USER_ID'], os.environ['BANDWIDTH_API_TOKEN'], os.environ['BANDWIDTH_API_SECRET'])
#
# # print(os.environ['BANDWIDTH_USER_ID'])
# # print(os.environ['BANDWIDTH_API_TOKEN'])
# # print(os.environ['BANDWIDTH_API_SECRET'])
#
# # numbers = account_api.search_available_local_numbers(area_code='910', quantity=1)
# # print(numbers[0]['number'])
# # ## +19104440230
# #
# # my_number = account_api.order_phone_number(numbers[0]['number'])
#
# my_number = '+19142268654'
# print(my_number)
#
# message_id = messaging_api.send_message(from_=my_number,
#                                         to='+12033219249',
#                                         text='SMS message')
# print(message_id)