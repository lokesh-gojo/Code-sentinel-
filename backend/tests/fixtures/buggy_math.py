def divide(a, b):
    # Bug: Missing zero-division check
    return a / b

def append_to(element, to=[]):
    # Bug: Mutable default argument
    to.append(element)
    return to

if __name__ == "__main__":
    print(divide(10, 0))
