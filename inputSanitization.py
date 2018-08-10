import phonenumbers


def sanitize_phone_number(phone_number):

    try:
        phone_num_object = phonenumbers.parse(phone_number, None)
    except phonenumbers.phonenumberutil.NumberParseException:
        print(f"{phone_number} could not parse number!")
        return False, None

    if not phonenumbers.is_possible_number(phone_num_object):
        print(f"{phone_number} is not a possible number!")
        return False, None
    elif not phonenumbers.is_valid_number(phone_num_object):
        print(f"{phone_number} is not a valid/working number!")
        return False, None
    else:
        good_number = phonenumbers.format_number(phone_num_object, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return True, good_number


valid, num = sanitize_phone_number("+12033219249")
print(valid, num)