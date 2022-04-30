from multiprocessing import Process, Pool, Array, Value, Manager


# def squre(i):
#     print(i*i)
# if __name__ == '__main__':
#     for i in range(10):
#         p = Process(target=squre, args=(i,))
#         p.start()



# def squre(i):
#     return(i*i)
# if __name__ == '__main__':
#     pool = Pool(processes=11)
#     l = [1,2,3,4,5,6,7,8,9,10]
#     out = pool.map(squre, l)
#     print(out)



# def squre(i):
#     return(i*i)
# if __name__ == '__main__':
#     pool = Pool(processes=11)
#     l = [1,2,3,4,5,6,7,8,9,10]
#     out = pool.map_async(squre, l)
#     out = out.get()
#     print(out)




# # here print result in square_list will print data but print result in main will print []
# # why because both main and p1 are in different process
# result = []
# def square_list(mylist):
# 	"""
# 	function to square a given list
# 	"""
# 	global result
# 	for num in mylist:
# 		result.append(num * num)
# 	print("Result(in process p1): {}".format(result))

# if __name__ == "__main__":
# 	mylist = [1,2,3,4]

# 	p1 = Process(target=square_list, args=(mylist,))
# 	p1.start()
# 	p1.join()
# 	print("Result(in main program): {}".format(result))



# # as we created array and value from multiprocessing package they will be acting as shared space between assigned processers 
# def list_square(l, array, value):
    
#     for i,v in enumerate(l):
#         array[i] = v*v
#     value.value = sum(array)
#     print("Process lo array, value:", array[:], value.value)

# if __name__ == "__main__":
#     l = [1,2,3,4]
#     array = Array('i', 4)
#     value = Value('i')
#     P = Process(target=list_square, args=(l, array, value))
#     P.start()
#     print("Main lo array, value:", array[:], value.value)
