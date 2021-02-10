def find_root(num, tol):
    root = 0.0
    step = tol/10
    while abs(num - root ** 2) >= tol and root ** 2 <= num:
        root += step
    if abs(num - root ** 2 < tol):
        return root
    else:
        return -1

def main():
    tolerance = .1
    number = 388
    try:
        3+3 == 6
    except:
        eek = 4
        print("hello!")

    square_root = find_root(number, tolerance)
    if abs(number - square_root ** 2) < tolerance:
        print('Approximate square root of', number, 'is:', square_root)
    else:
        print('Failed to find a square root for', number)

main()


# pseudocode:
# define function to compute approximate square root of a number, given that number and an acceptable threshold value
# set tolerance = .1
# prompt user for number
# compute approx square root of number, using predefined function, and given tolerance = .1
# store computed value in square_root
# if abs(number - square_root ** 2) < tolerance, then print 'approx square root of number is square_root'
# else, print failed to find square root for number



