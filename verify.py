class validate:

    def verify_password(password: str):
        l, u, n, s = 0, 0, 0, 0
        # lower, upper, number, and special character
        special_characters = """`~!@#$%^*()_-+={[}}|\:;"',.?"""
        # All special characters except <, >, /, and & to prevent HTML injection

        if 8 < len(password) < 64:
            for i in password:
                if i == " ":
                    return False
                if i.islower():
                    l += 1
                if i.isupper():
                    u += 1
                if i.isdigit():
                    n += 1
                for c in special_characters:
                    if i == c:
                        s += 1
                if i == "<" or i == ">" or i == "&":
                    return False
        if l > 0 and u > 0 and n > 0 and s > 0:
            return True
        else:
            return False

    def verify_username(username: str):
        special_characters = "<>&/"
        if 2 < len(username) < 21:
            for x in username:
                if x == " ":
                    return False
                for y in special_characters:
                    if x == y:
                        return False
            return True
        else:
            return False


# For testing purpose
def main():
    test_password_f = ["123!12q", "123456!Q q", " ", "123456!Qq<"]
    test_password_t = ["123456!Qq", "123456!@#aaA"]
    for f in test_password_f:
        assert validate.verify_password(f) is False
    for t in test_password_t:
        assert validate.verify_password(t) is True

    test_username_t = ["test1", "1234", "Asd!2as@"]
    test_username_f = ["t est1", "1<>234", "As&d!2as@", " ", "1", "12"]

    for t in test_username_t:
        assert validate.verify_username(t) is True
    for f in test_username_f:
        assert validate.verify_username(f) is False


if __name__ == "__main__":
    main()
