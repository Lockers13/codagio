def second_largest(input_arr):

    arr_size = len(input_arr)

    if arr_size < 2:
        return "Invalid input"

    input_arr.sort(reverse=True)
    max_val = input_arr[0]

    for i in range(1, arr_size):
        if input_arr[i] != max_val:
            return input_arr[i]

    return "No second largest value"