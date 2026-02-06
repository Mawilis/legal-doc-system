const tf = require('@tensorflow/tfjs-node');
const fs = require('fs');

async function trainRiskModel() {
  // Generate synthetic training data
  const trainingData = generateTrainingData(10000);
  const validationData = generateTrainingData(2000);
  
  const model = tf.sequential({
    layers: [
      tf.layers.dense({ inputShape: [50], units: 128, activation: 'relu' }),
      tf.layers.dropout({ rate: 0.3 }),
      tf.layers.dense({ units: 64, activation: 'relu' }),
      tf.layers.dropout({ rate: 0.2 }),
      tf.layers.dense({ units: 32, activation: 'relu' }),
      tf.layers.dense({ units: 6, activation: 'softmax' }),
    ]
  });
  
  model.compile({
    optimizer: tf.train.adam(0.001),
    loss: 'categoricalCrossentropy',
    metrics: ['accuracy']
  });
  
  await model.fit(trainingData.features, trainingData.labels, {
    epochs: 100,
    validationData: [validationData.features, validationData.labels],
    callbacks: {
      onEpochEnd: (epoch, logs) => {
        console.log(`Epoch ${epoch}: loss = ${logs.loss}, accuracy = ${logs.acc}`);
      }
    }
  });
  
  await model.save(`file://${__dirname}/../models/risk-prediction`);
  console.log('✅ Risk prediction model trained and saved');
}

trainRiskModel();
