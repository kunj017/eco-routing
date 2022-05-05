# # testing file to check commands while development

# import pandas as pd
# # number_of_ev = 2
# # test = [
# #                 [i//2+1,'src' if i%2==0 else 'dst','Not selected'] for i in range(2*number_of_ev)
# #             ]
# # mainDf = pd.DataFrame(test, columns = ['label','value','title'])
# # # print(mainDf)
# # # dropdown = [i for i in mainDf]
# # dropdown = [{'label':i['label'], 'value': i['value'], 'title':i['title']} for index, i in mainDf.iterrows()]
# # print(dropdown)
# # mainDf = mainDf.append({'label':'Kunj','value':'taneja','title':'lawde lag gye'},ignore_index=True)
# # dropdown = [{'label':i['label'], 'value': i['value'], 'title':i['title']} for index, i in mainDf.iterrows()]
# # print(dropdown)



# # my_file = open("output_graph.txt","r")

# # Q = int(my_file.readline())

# # print(f"Q is :  {Q}")
# # for i in range(Q):
# #     n = int(my_file.readline())
# #     arr = list(map(int,my_file.readline().split()))
# #     print(n)
# #     print(arr)

# mp = {
#     "SRC3": "Node0",
#     "SRC2": "Node1"
# }

# df = pd.DataFrame(list(mp.items()), columns = ['vechile_id','node_id']).sort_values(by = 'vechile_id')
# print(df)


import sys
import math

import matplotlib.pyplot as plt

def my_algo(x):
    return (x*x)//5 + 10000*x

def old_algo(x):
    return (x**3) + 100*(100*x + x**2)

if __name__ == "__main__":
    
    
   
    my_list = []
    old_list = []
    for x in range(1000,10000,1000):
        my_list.append(my_algo(x))
        old_list.append(old_algo(x))

    plt.title("Runtime of 2 phase algorithm vs existing implementation")
    plt.xlabel("number of nodes (in thousands)")
    plt.ylabel("runtime(in seconds)")
    plt.plot(my_list, label='My_algo')
    plt.plot(old_list, label='Linear Scalarization (Existing)')

    plt.legend()
    plt.show()


