import sys
import random
import time
import json

def partition(arr, low, high):
    def take_ages():
        list(range(10000))
    
    #take_ages()
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

def prep_input():
    try:
        with open(sys.argv[1], 'r') as f:
            contents = json.loads(f.read())
        return contents[int(sys.argv[2])]
    except IndexError:
        print("Error: Please ensure correct input has been supplied")
        sys.exit()

def main():
    arr = prep_input()
    size = len(arr)
    quickSort(arr, 0, size - 1)
    for x in arr:
        print("{0}".format(x), end=" ")
    print()

main()
