import numpy as np
from copy import deepcopy

def fit_cut_the_tail_proxy(X,y,quantiles,IQR,proxy_model,lower_tail_model,normal_model,upper_tail_model):

    proxy_model.fit(X,y)

    lower_outlier = (y < (quantiles[0] - 1.5*IQR))
    upper_outlier = (y > (quantiles[1] + 1.5*IQR))
    normal = (y >= (quantiles[0] - 1.5*IQR)) & (y <= (quantiles[1] + 1.5*IQR))

    if np.sum(lower_outlier) > 1:
        lower_tail_model.fit(X[lower_outlier],y[lower_outlier])
    else:
        lower_tail_model.fit(X[normal],y[normal])

    if np.sum(upper_outlier) > 1:
        upper_tail_model.fit(X[upper_outlier],y[upper_outlier])
    else:
        upper_tail_model.fit(X[normal],y[normal])

    normal_model.fit(X[normal],y[normal])

def predict_cut_the_tail_proxy(X,quantiles,IQR,proxy_model,lower_tail_model,normal_model,upper_tail_model):

    y_proxy = proxy_model.predict(X)

    lower_outlier = (y_proxy < (quantiles[0] - 1.5*IQR))
    upper_outlier = (y_proxy > (quantiles[1] + 1.5*IQR))
    normal = (y_proxy >= (quantiles[0] - 1.5*IQR)) & (y_proxy <= (quantiles[1] + 1.5*IQR))

    y_lower = lower_tail_model.predict(X)
    y_normal = normal_model.predict(X)
    y_upper = upper_tail_model.predict(X)

    return y_lower*lower_outlier + y_normal*normal + y_upper*upper_outlier


def fit_cut_the_tail(X,y,quantiles,tail_classifier,lower_tail_model,normal_model,upper_tail_model):
    q = np.quantile(y,q = quantiles)

    y = np.array(y)

    # get tail classes
    y_tail = (y <= q[0])*1 + (y >= q[1])*3 + ((y > q[0]) & (y < q[1]))*2

    # fit tail classifier

    tail_classifier.fit(X,y_tail)

    # fit lower tail model
    lower_tail_model.fit(X[y_tail==1],y[y_tail==1])

    # fit normal model
    normal_model.fit(X[y_tail==2],y[y_tail==2])

    # fit upper tail model
    upper_tail_model.fit(X[y_tail==3],y[y_tail==3])
    

def predict_cut_the_tails(X,tail_classifier,lower_tail_model,normal_model,upper_tail_model):

    y_tail = tail_classifier.predict(X)

    y_lower = lower_tail_model.predict(X)
    y_normal = normal_model.predict(X)
    y_upper = upper_tail_model.predict(X)

    y = y_lower*(y_tail==1) + y_normal*(y_tail==2) + y_upper*(y_tail==3)

    return y  


def fit_tail_classifier(X,y_tail,model):
    model.fit(X,y_tail)
    return model

def fit_tail_models(X,y,y_tail,model):
    models = [deepcopy(model) for i in [0,1,2]]
    for i in [0,1,2]:
        models[i].fit(X[y_tail==i],y[y_tail==i]) 
    return models

def tail_predict(x,tail_classifier,tail_models):
    tail_class = tail_classifier.predict([x])
    return tail_models[tail_class[0]].predict([x])

def batch_tail_predict(X,tail_classifier,tail_models):
    t_class = tail_classifier.predict(X)
    
    preds = np.zeros((len(t_class),1))
    for i in range(len(t_class)): #very inneficient
        preds[i] = tail_models[t_class[i]].predict([X[i]])[0]
    
    return preds

def split_by_quantile_class(df,target,q):
    ''' Creates a column called 'quant_class' that identifies the samples in the 
        target distribution tails. Lower tail:0, normal:1, upper tail:2
    Args

        df: original dataset
        target: target variable
        q: list of upper and lower quantile

    Returns:

        df: updated dataframe

    '''

    q = np.quantile(df[[target]],q = q)

    quant_class = []

    for index, row in df.iterrows():
        if row[target] <= q[0]:
            quant_class.append(0)
        elif (row[target] > q[0]) and (row[target] < q[1]):
            quant_class.append(1)
        elif row[target] >= q[1]:
            quant_class.append(2)
    
    df['tail_class'] = quant_class

    return df

def split_by_quantile(df,target,q):
    '''
    Args

        df: original dataset
        target: target variable
        q: list of upper and lower quantile

    Returns:

        lbdf: data below the lower quantile
        nddf: data between quantiles
        ubdf: date over the upper quantile

    '''

    q = np.quantile(df[[target]],q = q)

    lbdf = df[df[target] <= q[0]]
    ubdf = df[df[target] >= q[1]]
    nddf = df[(df[target] > q[0]) & (df[target] < q[1])]

    return lbdf,nddf,ubdf

