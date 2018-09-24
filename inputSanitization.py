import phonenumbers
import re

def sanitize_phone_number(phone_number):

    phone_number = purify_digits(phone_number)

    try:
        phone_num_object = phonenumbers.parse("+" + phone_number, None)
    except phonenumbers.phonenumberutil.NumberParseException:
        print(f"{phone_number} could not parse number!")
        return False, None

    if len(phone_number) < 11:
        print(f"{phone_number} is not long enough!")
        return False, None

    if not phonenumbers.is_possible_number(phone_num_object):
        print(f"{phone_number} is not a possible number!")
        return False, None
    if not phonenumbers.is_valid_number(phone_num_object):
        print(f"{phone_number} is not a valid/working number!")
        return False, None
    else:
        good_number = phonenumbers.format_number(phone_num_object, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return True, good_number


def purify_digits(number):
    result = re.sub('[^0-9]', '', number)
    if len(result) == 10:
        result = '1' + result
    return result


def is_name_valid(name_text):
    allowed_chars = ' abcdefghijklmnopqrstuvwxyzABCEFGHIJKLMNOPQRSTUVQRSWXYZ'
    if my_contains_all(name_text, allowed_chars):
        return True
    else:
        return False


def my_contains_all(str, set):
    for c in str:
        if c not in set:
            return 0
    return 1


def input_sanitizer(curr_first_name, curr_last_name, curr_number):
    if curr_first_name == '' or curr_first_name == '' or curr_number == '':
        return_msg = f"USER {curr_first_name}, {curr_last_name}, {curr_number}  Data is missing."
        return False, return_msg

    num_is_valid, _ = sanitize_phone_number(curr_number)
    first_name_is_valid = is_name_valid(curr_first_name)
    last_name_is_valid = is_name_valid(curr_last_name)

    if not num_is_valid:
        return_msg = f"USER {curr_first_name}, {curr_last_name}, {curr_number} NUMBER IS INVALID."
        return False, return_msg

    if not first_name_is_valid:
        return_msg = f"USER {curr_first_name}, {curr_last_name}, {curr_number} FIRST NAME IS INVALID."
        return False, return_msg

    if not last_name_is_valid:
        return_msg = f"USER {curr_first_name}, {curr_last_name}, {curr_number} LAST NAME IS INVALID."
        return False, return_msg

    return_msg = f"USER {curr_first_name}, {curr_last_name}, {curr_number} IS VALID"
    return True, return_msg



print(purify_digits("12033219249"))

# print("Name is valid: " + str(is_name_valid("Ryan Swei")))
# print("Name is valid: " + str(is_name_valid("Ryan Swei)")))
# print("Name is valid: " + str(is_name_valid("Ryan Swei!")))
#
#
# valid, num = sanitize_phone_number("+12033219249")
# print(valid, num)

# valid, num = sanitize_phone_number("+1203219249")
# print(valid, num)

# valid, num = sanitize_phone_number("+120433219249")
# print(valid, num)