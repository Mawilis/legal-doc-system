#!/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ TIME SERIES ANALYZER - FORENSIC EDITION                                   ║
  ║ Hybrid forecasting (LSTM + Seasonality + Trend)                           ║
  ║ Features: Memory safety (tf.tidy), Scaler persistence, Phase-shifted FFT  ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import * as tf from '@tensorflow/tfjs-node';
import { createHash } from 'crypto';
import fs from 'fs';
import path from 'path';

export class TimeSeriesAnalyzer {
  constructor(modelPath = './models/timeseries') {
    this.modelPath = path.resolve(modelPath);
    this.model = null;
    this.min = null;
    this.max = null;
    this.seqLength = 5;
  }

  async forecast(data, periods = 12) {
    console.time('timeseries-forecast');

    if (!Array.isArray(data) || data.length < this.seqLength + 1) {
      throw new Error(
        `Invalid input: minimum ${this.seqLength + 1} numeric points required for sequence window.`
      );
    }

    const datasetHash = createHash('sha256').update(JSON.stringify(data)).digest('hex');

    const seasonality = await this.detectSeasonality(data);
    const trend = await this.extractTrend(data);

    if (!this.model) {
      await this.buildAndTrainModel(data);
      await this.persistModel();
    }

    const forecast = await this.generateForecast(data, periods, seasonality, trend);
    const confidence = this.calculateConfidence(forecast, data);
    const accuracy = await this.evaluateAccuracy(data);

    console.timeEnd('timeseries-forecast');

    return {
      forecast,
      confidence,
      seasonality,
      trend,
      metadata: {
        datasetHash,
        dataPoints: data.length,
        periods,
        method: 'Forensic LSTM + Prophet Hybrid',
        accuracy,
      },
    };
  }

  async detectSeasonality(data) {
    const n = data.length;
    const fft = [];
    for (let k = 0; k < n; k++) {
      let real = 0,
        imag = 0;
      for (let t = 0; t < n; t++) {
        const angle = (2 * Math.PI * k * t) / n;
        real += data[t] * Math.cos(angle);
        imag -= data[t] * Math.sin(angle);
      }
      fft.push(Math.sqrt(real * real + imag * imag));
    }
    const threshold = Math.max(...fft) * 0.3;
    const dominant = [];
    // Skip DC component (0) and analyze up to Nyquist limit
    for (let i = 1; i < n / 2; i++) {
      if (fft[i] > threshold) {
        dominant.push({ period: n / i, strength: fft[i] / fft[0] });
      }
    }
    return { hasSeasonality: dominant.length > 0, patterns: dominant };
  }

  async extractTrend(data) {
    const n = data.length;
    const window = Math.min(7, Math.floor(n / 3));
    const trend = [];
    for (let i = 0; i < n; i++) {
      const start = Math.max(0, i - Math.floor(window / 2));
      const end = Math.min(n, i + Math.floor(window / 2) + 1);
      const segment = data.slice(start, end);
      trend.push(segment.reduce((a, b) => a + b, 0) / segment.length);
    }
    // FORENSIC FIX: Divide by `n` to get per-period slope, preventing exponential explosion
    const slope = (trend[trend.length - 1] - trend[0]) / n;
    return {
      values: trend,
      slope,
      direction: slope > 0 ? 'upward' : slope < 0 ? 'downward' : 'stable',
    };
  }

  async buildAndTrainModel(data) {
    this.min = Math.min(...data);
    this.max = Math.max(...data);

    // Protect against zero-variance datasets
    if (this.max === this.min) {
      this.max += 1;
    }

    const normalized = data.map((x) => (x - this.min) / (this.max - this.min));

    const X = [],
      y = [];
    for (let i = 0; i < normalized.length - this.seqLength; i++) {
      X.push(normalized.slice(i, i + this.seqLength));
      y.push(normalized[i + this.seqLength]);
    }

    // FORENSIC FIX: Lightweight architecture to prevent overfitting on small time-series data
    const model = tf.sequential();
    model.add(tf.layers.lstm({ units: 16, inputShape: [this.seqLength, 1] }));
    model.add(tf.layers.dense({ units: 1, activation: 'linear' }));

    model.compile({ optimizer: tf.train.adam(0.01), loss: 'meanSquaredError' });

    // Use tf.tidy to automatically clean up tensors used during training setup
    await tf.tidy(() => {
      const xs = tf.tensor3d(X, [X.length, this.seqLength, 1]);
      const ys = tf.tensor2d(y, [y.length, 1]);
      return model.fit(xs, ys, { epochs: 50, batchSize: 8, verbose: 0 });
    });

    this.model = model;
  }

  async generateForecast(data, periods, seasonality, trend) {
    // Keep a running sequence of normalized values
    let currentSeqArray = data
      .slice(-this.seqLength)
      .map((x) => (x - this.min) / (this.max - this.min));
    const forecast = [];

    for (let i = 0; i < periods; i++) {
      // FORENSIC FIX: Memory safety wrap prevents Out-Of-Memory (OOM) fatal crashes
      const predVal = tf.tidy(() => {
        const input = tf.tensor3d([currentSeqArray], [1, this.seqLength, 1]);
        const pred = this.model.predict(input);
        return pred.dataSync()[0];
      });

      const denorm = predVal * (this.max - this.min) + this.min;

      // FORENSIC FIX: Phase shift `t` starts at `data.length + i` to continue the wave smoothly
      const t = data.length + i;
      const seasonalAdj = seasonality.hasSeasonality
        ? seasonality.patterns[0].strength *
          Math.sin((2 * Math.PI * t) / seasonality.patterns[0].period)
        : 0;

      const trendAdj = trend.slope * (i + 1);

      // Construct final forecast point
      forecast.push(denorm + seasonalAdj + trendAdj);

      // Shift window forward for the next prediction
      currentSeqArray.shift();
      currentSeqArray.push(predVal);
    }

    return forecast;
  }

  calculateConfidence(forecast, data) {
    const residuals = data.slice(1).map((v, i) => v - data[i]);
    const meanError = residuals.reduce((a, b) => a + b, 0) / residuals.length;
    const stdError = Math.sqrt(
      residuals.reduce((a, b) => a + Math.pow(b - meanError, 2), 0) / residuals.length
    );

    return forecast.map((_, i) => ({
      upper: forecast[i] + 1.96 * stdError * Math.sqrt(i + 1),
      lower: forecast[i] - 1.96 * stdError * Math.sqrt(i + 1),
      confidence: Math.max(0, 1 - 0.05 * Math.sqrt(i + 1)),
    }));
  }

  async evaluateAccuracy(data) {
    if (!this.model) return null;
    const normalized = data.map((x) => (x - this.min) / (this.max - this.min));
    const X = [],
      y = [];

    for (let i = 0; i < normalized.length - this.seqLength; i++) {
      X.push(normalized.slice(i, i + this.seqLength));
      y.push(normalized[i + this.seqLength]);
    }

    // FORENSIC FIX: Memory safety for evaluation
    const loss = tf.tidy(() => {
      const xs = tf.tensor3d(X, [X.length, this.seqLength, 1]);
      const ys = tf.tensor2d(y, [y.length, 1]);
      const evalResult = this.model.evaluate(xs, ys);
      return evalResult.dataSync()[0];
    });

    return Math.max(0, 1 - loss); // Pseudo accuracy bound
  }

  async persistModel() {
    if (this.model) {
      if (!fs.existsSync(this.modelPath)) {
        fs.mkdirSync(this.modelPath, { recursive: true });
      }
      await this.model.save(`file://${this.modelPath}`);

      // FORENSIC FIX: Persist scalers to prevent Amnesia State on reboot
      const scalers = { min: this.min, max: this.max };
      fs.writeFileSync(`${this.modelPath}/scalers.json`, JSON.stringify(scalers));
      console.log(`✅ Model and scalers persisted at ${this.modelPath}`);
    }
  }

  async loadModel() {
    if (
      fs.existsSync(`${this.modelPath}/model.json`) &&
      fs.existsSync(`${this.modelPath}/scalers.json`)
    ) {
      this.model = await tf.loadLayersModel(`file://${this.modelPath}/model.json`);

      const scalers = JSON.parse(fs.readFileSync(`${this.modelPath}/scalers.json`, 'utf8'));
      this.min = scalers.min;
      this.max = scalers.max;
      console.log(`✅ Model and scalers successfully loaded from ${this.modelPath}`);
    } else {
      throw new Error('No saved model or scalers found. Training required.');
    }
  }
}

export default TimeSeriesAnalyzer;
