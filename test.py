import math

def chunks(lst, n):

    length = len(lst)

    # Determine how many chunks there will be
    num_chunks = math.ceil(length / n)
    return_values = [0] * num_chunks

    start_index = 0
    for i in range(0, num_chunks):
        if (i == num_chunks - 1 and start_index + n > length):
            return_values[i] = lst[start_index: length]
        else:
            return_values[i] = lst[start_index: start_index + n]
            start_index += n
    return return_values

lst = [int(i) for i in range(1, 506)]
lst = chunks(lst, 100)

for i in lst:
    print(i)