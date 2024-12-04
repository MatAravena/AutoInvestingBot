params={
    'batch_size':[20,25],
    'epochs':[50,70],
    'model__neurons_1':[6,7],
    'model__neurons_2':[4,3],
    'model__activation':['relu','softmax'],
    'model__optimizer':['adam','rmsprop'],
    'model__dropout':[0.1,0.2]
    }

def create_model(neurons_1,neurons_2,activation,optimizer,dropout):
    nn = tf.keras.Sequential()
    nn.add(tf.keras.layers.Input(shape=11))

    nn.add(tf.keras.layers.Dense(units=neurons_1, activation=activation,kernel_initializer='glorot_uniform'))
    nn.add(tf.keras.layers.Dropout(rate=dropout))
    nn.add(tf.keras.layers.Dense(units=neurons_2,activation=activation))    
    nn.add(tf.keras.layers.Dropout(rate=dropout))
    nn.add(tf.keras.layers.Dense(units=1,activation='sigmoid'))
    nn.compile(optimizer=optimizer,loss='binary_crossentropy',
                   metrics=['accuracy']) 
    return nn

model = KerasClassifier(model=create_model)

gs= GridSearchCV(
    estimator=model, 
    param_grid=params,
    scoring='accuracy', 
    cv=10,
    n_jobs=-1,
    return_train_score=True,
    verbose=0
)