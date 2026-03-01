#!/* eslint-disable */
/*╔═══════════════════════════════════════════════════════════════════════════╗
  ║ PREDICTIVE TEMPLATE ENGINE - MASTER ORCHESTRATOR                          ║
  ║ Fuses TimeSeries, NLP Trend Detection, and TensorFlow Regulatory models   ║
  ╚═══════════════════════════════════════════════════════════════════════════╝*/

import TimeSeriesAnalyzer from './TimeSeriesAnalyzer.js';
import LegalTrendDetector from './LegalTrendDetector.js';
import RegulatoryForecaster from './RegulatoryForecaster.js';

export class PredictiveTemplateEngine {
  constructor() {
    this.timeSeries = new TimeSeriesAnalyzer();
    this.trendDetector = new LegalTrendDetector();
    this.forecaster = new RegulatoryForecaster();

    this.predictions = new Map();
    this.isInitialized = false;
  }

  async initializeEngines() {
    if (this.isInitialized) return;
    await this.trendDetector.initialize();
    this.isInitialized = true;
  }

  // FORENSIC FIX: Renamed to match the Service Wrapper's expected method
  async analyzeTemplate(template) {
    console.time('predictive-analysis');
    await this.initializeEngines();

    const practiceArea = template.practiceArea || 'general';
    const jurisdiction = template.jurisdiction || 'global';

    const historicalPatterns = await this.analyzeHistoricalPatterns(template);
    const emergingTrends = await this.detectEmergingTrends(practiceArea, jurisdiction);
    const regulatoryForecast = await this.forecastRegulatoryChanges(practiceArea, jurisdiction);
    const usagePredictions = await this.predictUsagePatterns(template);

    const futureVersions = await this.generateFutureVersions(
      template,
      regulatoryForecast,
      emergingTrends
    );

    console.timeEnd('predictive-analysis');

    const prediction = {
      templateId: template.templateId,
      timestamp: new Date().toISOString(),
      historicalPatterns,
      emergingTrends,
      regulatoryForecast,
      usagePredictions,
      futureVersions,
      riskScore: this.calculateRiskScore(regulatoryForecast),
      confidence: this.calculateConfidence(regulatoryForecast, emergingTrends),
    };

    this.predictions.set(template.templateId, prediction);
    return prediction;
  }

  async analyzeHistoricalPatterns(template) {
    const patterns = [];
    if (template.versionHistory && template.versionHistory.length > 0) {
      const changes = template.versionHistory.map((v) => ({
        date: v.createdAt || new Date(),
        type: this.classifyChange(v.changelog || ''),
      }));

      patterns.push({
        type: 'version_frequency',
        value: this.calculateVersionFrequency(changes),
        trend: this.determineTrend(changes.map((c) => c.date)),
      });

      patterns.push({
        type: 'seasonal',
        value: this.detectSeasonality(changes),
        confidence: 0.87,
      });
    }
    return patterns;
  }

  classifyChange(changelog) {
    const lower = changelog.toLowerCase();
    if (lower.includes('compliance') || lower.includes('law')) return 'regulatory';
    if (lower.includes('variable') || lower.includes('logic')) return 'structural';
    if (lower.includes('clause')) return 'content';
    return 'other';
  }

  calculateVersionFrequency(changes) {
    if (changes.length < 2) return 0;
    const first = new Date(changes[0].date);
    const last = new Date(changes[changes.length - 1].date);
    const days = (last - first) / (1000 * 60 * 60 * 24);
    return days === 0 ? 0 : changes.length / days;
  }

  determineTrend(dates) {
    if (dates.length < 3) return 'stable';
    const intervals = [];
    for (let i = 1; i < dates.length; i++) {
      intervals.push(new Date(dates[i]) - new Date(dates[i - 1]));
    }
    const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    const recentInterval =
      intervals.slice(-3).reduce((a, b) => a + b, 0) / Math.min(3, intervals.length);

    if (recentInterval < avgInterval * 0.7) return 'accelerating';
    if (recentInterval > avgInterval * 1.3) return 'decelerating';
    return 'stable';
  }

  detectSeasonality(changes) {
    if (changes.length < 4) return 'random';
    const months = changes.map((c) => new Date(c.date).getMonth());
    const monthCounts = Array(12).fill(0);
    months.forEach((m) => monthCounts[m]++);

    const variance = this.calculateVariance(monthCounts);
    return variance > 2 ? 'seasonal' : 'random';
  }

  async detectEmergingTrends(practiceArea, jurisdiction) {
    const trends = [];

    // FORENSIC FIX: Access the correct payload properties from the upgraded NLP engine
    const trendData = await this.trendDetector.scanLegalDatabases(practiceArea, jurisdiction, '6m');

    trends.push({
      type: 'emerging_topics',
      terms: trendData.trends.emerging.map((t) => t.name),
      impact: 'high',
      timeframe: '3-6 months',
    });

    const jurisdictionTrends = await this.trendDetector.analyzeJurisdictionTrends(jurisdiction);
    trends.push({
      type: 'jurisdiction_shifts',
      harmonizationScore: jurisdictionTrends.harmonization.score,
      impact: 'critical',
      timeframe: '6-12 months',
    });

    return trends;
  }

  async forecastRegulatoryChanges(practiceArea, jurisdiction) {
    // FORENSIC FIX: Correctly map the TensorFlow forecaster output
    const predictionResult = await this.forecaster.predict(practiceArea, jurisdiction, 12);
    const forecastArray = predictionResult.forecast || [];

    return {
      changes: forecastArray.map((f) => ({
        probability: f.probability,
        effectiveDate: f.date,
        impact: f.impactLevel,
        intelligenceSources: f.intelligence?.sources || [],
      })),
      summary: {
        totalChanges: forecastArray.length,
        criticalChanges: forecastArray.filter((f) => f.impactLevel === 'critical').length,
        averageProbability: forecastArray.length
          ? forecastArray.reduce((a, b) => a + b.probability, 0) / forecastArray.length
          : 0,
      },
    };
  }

  async predictUsagePatterns(template) {
    // FORENSIC FIX: Generate a safe 6-point sliding window for the LSTM if template lacks history
    let historySequence = template.usageHistory || [];
    if (historySequence.length < 6) {
      const base = template.usageStats?.timesUsed || 10;
      historySequence = [base * 0.8, base * 0.85, base * 0.9, base * 0.95, base, base * 1.05];
    }

    const forecast = await this.timeSeries.forecast(historySequence, 12);

    return {
      nextMonth: Math.round(forecast.forecast[0]),
      nextQuarter: Math.round(forecast.forecast.slice(0, 3).reduce((a, b) => a + b, 0)),
      nextYear: Math.round(forecast.forecast.reduce((a, b) => a + b, 0)),
      peakPeriods: this.identifyPeakPeriods(forecast.forecast),
    };
  }

  identifyPeakPeriods(forecastArray) {
    const peaks = [];
    const avg = forecastArray.reduce((a, b) => a + b, 0) / forecastArray.length;

    forecastArray.forEach((value, index) => {
      if (value > avg * 1.5) {
        peaks.push({
          month: index + 1,
          expectedVolume: Math.round(value),
          preparation: this.generatePreparationPlan(value),
        });
      }
    });
    return peaks;
  }

  generatePreparationPlan(volume) {
    return {
      scale: volume > 1000 ? 'high' : 'medium',
      recommendations: [
        'Pre-warm template cache',
        'Increase queue capacity',
        'Provision additional workers',
      ],
    };
  }

  async generateFutureVersions(template, regulatoryForecast, emergingTrends) {
    const versions = [];
    const currentVersion = template.version || 1;

    if (regulatoryForecast.summary.criticalChanges > 0) {
      versions.push({
        version: currentVersion + 1,
        predictedDate: this.calculateVersionDate(3),
        changes: ['Mandatory compliance updates based on high-probability regulatory shifts'],
        priority: 'high',
        estimatedEffort: '2 weeks',
      });
    }

    if (emergingTrends.length > 0) {
      versions.push({
        version: currentVersion + 2,
        predictedDate: this.calculateVersionDate(6),
        changes: ['Adopt emerging terminology', 'Update clauses for modern practices'],
        priority: 'medium',
        estimatedEffort: '1 week',
      });
    }

    return versions;
  }

  calculateVersionDate(monthsAhead) {
    const date = new Date();
    date.setMonth(date.getMonth() + monthsAhead);
    return date.toISOString().split('T')[0];
  }

  calculateRiskScore(regulatoryForecast) {
    return regulatoryForecast.summary.averageProbability > 0.7 ? 0.85 : 0.25;
  }

  calculateConfidence(regulatoryForecast, emergingTrends) {
    const regulatoryConfidence = regulatoryForecast.summary.averageProbability;
    const trendsConfidence = emergingTrends.length > 0 ? 0.85 : 0.7;
    return (regulatoryConfidence + trendsConfidence) / 2;
  }

  calculateVariance(arr) {
    const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
    return arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / arr.length;
  }

  getPrediction(templateId) {
    return this.predictions.get(templateId);
  }

  getAllPredictions() {
    return Array.from(this.predictions.values());
  }
}

export default PredictiveTemplateEngine;
