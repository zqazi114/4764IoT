from mongodb import Mongo
from sklearn import svm

SPLIT = 3
COLUMBIA = ["C", "O", "L", "U", "M", "B", "I", "A"]
COLUMBIA_ONEHOT = [ [1,0,0,0,0,0,0,0], 
                    [0,1,0,0,0,0,0,0],
                    [0,0,1,0,0,0,0,0],
                    [0,0,0,1,0,0,0,0],
                    [0,0,0,0,1,0,0,0],
                    [0,0,0,0,0,1,0,0],
                    [0,0,0,0,0,0,1,0],
                    [0,0,0,0,0,0,0,1]
                    ]
m = Mongo()

def get_data():
    print("LOG: importing data")
    X = []
    y = []
    for i, char in enumerate(COLUMBIA):
        X.append(m.get_accel_from_db(char=char))
        y.append(COLUMBIA_ONEHOT[i])
    return X, y

def train_model(X, y):
    print("LOG: training model")
    split = len(X)//SPLIT
    X_train = X[:split]
    y_train = y[:split]
    X_test = X[split:]
    y_test = y[split:]

    clf = svm.SVC(gamma='scale', decision_function_shape='ovo')
    clf.fit(X_train, y_train)

    print("LOG: testing model")
    pred = clf.predict(X_test)
    acc = (y_test == pred).sum()/len(y_test)
    print("LOG: accuracy={}".format(acc))

    print("LOG: saving model to file")
    
    return clf

X, y = get_data()
#model = train_model(X, y)
