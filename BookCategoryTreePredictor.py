# mongoimport --db dbName --collection collectionName --file fileName.json
# import a json collection in mongodb
import Models
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.tree import DecisionTreeClassifier
import graphviz
from sklearn import tree

# step1 - Acquisire in un dataframe tutti i dati del DB
# step2 - Rimuovere i campi non utili
# step3 - Fill dei campi vuoti con il valore medio e fill delle descrizioni con il titolo
# step4 - matrice termini-doc con le long description
# step5 - unione della matrice con le altre feature
# step6 - creazione di training set e test set
# step7 - addestramento modelli predittivi

books = Models.GetAllBooks()
books_df = pd.DataFrame(books)
books_df.set_index('bid')

drop_columns = ['thumbnailUrl', 'isbn', '_id']
books_df.drop(drop_columns, inplace=True, axis=1)

books_df['longDescription'].fillna(books_df['title'], inplace=True)
books_df['pageCount'].fillna(books_df['pageCount'].median, inplace=True)
books_df['categories'].fillna('none', inplace=True)
books_df['cat'] = books_df['categories'].map(lambda x: x[0] if len(x) > 0 else 'default')  # da una lista, prendo solo il primo valore
books_df['aut'] = books_df['authors'].map(lambda x: x[0] if len(x) > 0 else 'default')  # da una lista, prendo solo il primo valore
books_df.drop('categories', inplace=True, axis=1)
books_df.drop('authors', inplace=True, axis=1)

vect = CountVectorizer(ngram_range=(1, 2),stop_words='english')
matrix = vect.fit_transform(books_df['longDescription'])  # restituisce la matrice termini-doc
print(len(vect.get_feature_names()))
freqs = [(word, matrix.getcol(idx).sum()) for word, idx in vect.vocabulary_.items()]

dtMatrix = pd.DataFrame(matrix.todense(), columns=vect.get_feature_names())
df = pd.concat([books_df, dtMatrix], axis=1)
status_dummy = pd.get_dummies(df.status, prefix="status")  # creo delle variabili numeriche per usare una categorica
authors_dummy = pd.get_dummies(df.aut, prefix="aut")  # creo delle variabili numeriche per usare una categorica
df = pd.concat([df, status_dummy], axis=1)  # rimuovo le vecchie variabili
df = pd.concat([df, authors_dummy], axis=1)  # rimuovo le vecchie variabili
drop_columns = ['longDescription', 'shortDescription', 'title', 'status', 'publishedDate', 'bid', 'aut']
df.drop(drop_columns, inplace=True, axis=1)
print(df.shape) #ok
print(list(df))

# todo: solve underfitting introducing other authors or adding new features

cols = list(df)
cols.remove('cat')
X = df[cols]
y = df['cat']
X_train, X_test, y_train, y_test = train_test_split(X,y)

dtree = DecisionTreeClassifier(max_leaf_nodes=20)
dtree.fit(X_train, y_train)

score = dtree.score(X_test, y_test)
print("Score: " + str(score))

### PRINT TREE ###
dot_data = tree.export_graphviz(dtree, out_file=None)
graph = graphviz.Source(dot_data)
graph.render("book_tree")
