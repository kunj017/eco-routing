import pandas as pd
number_of_ev = 2
test = [
                [i//2+1,'src' if i%2==0 else 'dst','Not selected'] for i in range(2*number_of_ev)
            ]
mainDf = pd.DataFrame(test, columns = ['label','value','title'])
# print(mainDf)
# dropdown = [i for i in mainDf]
dropdown = [{'label':i['label'], 'value': i['value'], 'title':i['title']} for index, i in mainDf.iterrows()]
print(dropdown)
mainDf = mainDf.append({'label':'Kunj','value':'taneja','title':'lawde lag gye'},ignore_index=True)
dropdown = [{'label':i['label'], 'value': i['value'], 'title':i['title']} for index, i in mainDf.iterrows()]
print(dropdown)



my_file = open("output_graph.txt","r")

Q = int(my_file.readline())

print(f"Q is :  {Q}")
for i in range(Q):
    n = int(my_file.readline())
    arr = list(map(int,my_file.readline().split()))
    print(n)
    print(arr)
