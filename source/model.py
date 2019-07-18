class Autoencoder():
    def __init__(self):
        self.img_rows = img_row
        self.img_cols = img_col
        self.channels = 3
    
        sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)


        self.autoencoder_model = self.build_model()
        self.autoencoder_model.compile(loss='mse', optimizer=sgd, metrics = ['acc'])
  
        self.autoencoder_model.summary()

    def downsampling(self, input_layer, number_of_filter, dropout=False, maxpooling=True):
        x = Conv2D(number_of_filter, (3, 3), padding='same')(input_layer)
        x = BatchNormalization()(x)
        if maxpooling:
            x = Activation('relu')(x)        
        if dropout:
            x = Dropout(0.3)(x)
        x = MaxPooling2D((2, 2))(x)

        return x
    
    def upsampling(self, input_layer, number_of_filter):
        x = Conv2D(number_of_filter, (3, 3), activation='relu', padding='same')(input_layer)
        x = UpSampling2D((2, 2))(x)

        return x

    def build_model(self):
        input_layer = Input(shape=(img_row, img_col, 3))

        x = self.downsampling(input_layer, 128)
        x = self.downsampling(x, 128)
        x = self.downsampling(x, 256)
        x = self.downsampling(x, 512, dropout=True)
        
        x = self.downsampling(x, 1024, dropout=True, maxpooling=False)
        
        x = self.upsampling(x, 512)
        x = self.upsampling(x, 256)
        x = self.upsampling(x, 128)
        x = self.upsampling(x, 128)

        output_layer = Conv2D(
            3, (3, 3), activation='sigmoid', padding='same')(x)

        return Model(input_layer, output_layer)

    def train_model(self, x_train, y_train, x_val, y_val, epochs, batch_size=20):
        early_stopping = EarlyStopping(monitor='val_loss',
                                       min_delta=0,
                                       patience=5,
                                       verbose=1,
                                       mode='auto')

        filepath = result_dir +  "/model/model-{epoch:02d}-{val_loss:.4f}.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1,
                                     save_best_only=True, save_weights_only=False, mode='min')
        my_callback = MyCallback()
        callbacks_list = [
            checkpoint,
            my_callback
        ]
        history = self.autoencoder_model.fit(x_train, y_train,
                                             batch_size=batch_size,
                                             epochs=epochs,
                                             validation_data=(x_val, y_val),
                                             callbacks=callbacks_list
                                             )
        # plt.plot(history.history['loss'])
        # plt.plot(history.history['val_loss'])
        # plt.title('Model loss')
        # plt.ylabel('Loss')
        # plt.xlabel('Epoch')
        # plt.legend(['Train', 'Test'], loc='upper left')
        # plt.show()
        # plt.savefig(result_dir + "/graph.jpg")
        # plt.close()

    def eval_model(self, x_test):
        preds = self.autoencoder_model.predict(x_test)
        return preds

    def save(self, path):
        self.autoencoder_model.save(path)