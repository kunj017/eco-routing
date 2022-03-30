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