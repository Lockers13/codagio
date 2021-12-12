def second_largest(input_arr):

    arr_size = len(input_arr)
    if arr_size < 2:
        return "Invalid input"
    
    first = second = float('-inf')

    for i in input_arr:
        try:
            if i > first:
                second = first
                first = i
            elif i > second and i != first:
                second = i
        except Exception:
            pass
    
    if second == float('-inf'):
        return "No second largest value"

    return second