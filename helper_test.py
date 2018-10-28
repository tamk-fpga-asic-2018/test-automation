#helpper test

import helpers


def ints_to_string_test():
    """
    """
    print("ints_to_string test:")
    testString = "123"
    intList = list([1,2,3])
    print("intList", intList)

    intString = helpers.ints_to_string(intList)
    print("intString", intString)
    if intString == testString:
        print("PASS")
    else:
        print("FAIL")



ints_to_string_test()