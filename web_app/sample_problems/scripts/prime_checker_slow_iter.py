def is_prime(inputs):
    ret_list = []
    for num in inputs:
        try:
            int(num)
        except ValueError:
            ret_list.append("Not an integer!")
            continue
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
        ret_list.append(is_prime)
    return ret_list
