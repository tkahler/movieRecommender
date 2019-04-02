#!/usr/bin/python3.6

import cgi
import cgitb
cgitb.enable()

import pandas as pd
from rake_nltk import Rake
import omdb
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

omdb.set_default('apikey', 'ebfc35ed')



def getSimMatrix(title):
    movie = omdb.get(title=title)
    if movie:

        #set index to be title
        movieDF = pd.DataFrame()
        fullTitle = movie['title']
        movieDF = movieDF.append({'Title': movie['title'],
                           'Genre' : movie['genre'],
                           'Director' : movie['director'],
                           'Actors' : movie['actors'],
                           'Plot' : movie['plot']}, ignore_index=True)

        df = pd.read_csv("https://query.data.world/s/uikepcpffyo2nhig52xxeevdialfl7")
        df = df[['Title','Genre','Director','Actors','Plot']]
        df = df.append(movieDF, sort=False)
        df.set_index('Title', inplace=True)


        df['Key_words'] = ""

        for index,row in df.iterrows():
            plot = row['Plot'].lower()

            r = Rake()
            #extract keywords form plot
            r.extract_keywords_from_text(plot);

            #add list of keywords as column
            keyWords = list(r.get_ranked_phrases())
            for word in keyWords:
                word.replace(" ", "")
                word.lower()
            row['Key_words'] = " ".join(keyWords)


            row['Director'] = row['Director'].lower().replace(" ", "").replace(",", " ")
            row['Actors'] = row['Actors'].lower().replace(" ", "").replace(",", " ")
            row['Genre'] = row['Genre'].lower().replace(",", "")

        #drop plot column
        df.drop(['Plot'], axis=1)

        #bag of words, words from all columns
        df['bagOfWords'] = df['Genre'] + " " + df['Director'] + " " +\
                           df['Actors'] + " " + df['Key_words']

        #drop all columns but bagOfWords
        df.drop(df.columns[:-1], axis=1, inplace=True)

        count = CountVectorizer()
        count_matrix = count.fit_transform(df['bagOfWords'])

        similarity = cosine_similarity(count_matrix, count_matrix)


        #index to movie title
        return pd.Series(df.index), similarity, fullTitle
    else:
        return None, None, "Could not find movie"


def recommend(title):
    indices, similarity, fullTitle = getSimMatrix(title)
    print("Content-type:text/html\n\n")
    print("<html>")
    print("<head>")
    print("<title>Recommendations</title>")
    print("</head>")
    print("<body>")
    if similarity is not None:
        indx = indices[indices == fullTitle].index[0]
        scores = pd.Series(similarity[indx]).sort_values(ascending = False)
        for i in range(8):
            print('<p>' + indices[scores.index[i+1]] + '</p>')

    else:
        print('<p>' + title + " not found go back to enter another movie</p>")
    print("</body>")
    print("</html>")


#get title from submit box
form = cgi.FieldStorage()
title = form.getvalue('searchbox')
recommend(title)



