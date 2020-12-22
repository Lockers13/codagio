import sys
import random

def partition(arr, low, high):   
    # for x in arr:
    #     print("{0}".format(x), end=" ")
    # print()
    pivot = arr[(high+low)//2]
    i = low - 1
    j = high + 1 

    while True:
        i += 1
        while arr[i] < pivot:
            i += 1
        j -= 1
        while arr[j] > pivot:
            j -= 1
        if i >= j:
            return j

        arr[i], arr[j] = arr[j], arr[i]


def quickSort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quickSort(arr, low, pi)
        quickSort(arr, pi+1, high)

def init_arr_from_file():
    
    return [random.randint(0,100) for i in range(5000)]


arr = init_arr_from_file()
size = len(arr)
quickSort(arr, 0, size - 1)
# for x in arr:
#     print("{0}".format(x), end=" ")
# print()