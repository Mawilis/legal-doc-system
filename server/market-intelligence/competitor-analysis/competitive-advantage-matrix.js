const logger = require('../../utils/logger');
const auditLogger = require('../../utils/auditLogger');
const cryptoUtils = require('../../utils/cryptoUtils');

class CompetitiveAdvantageMatrix {
    constructor() {
        this.matrix = {};
        this.analysisHistory = [];
        logger.info('CompetitiveAdvantageMatrix initialized');
    }

    getMatrix() {
        return this.matrix;
    }

    addCompetitor(competitor) {
        if (!competitor || !competitor.id || !competitor.name) {
            throw new Error('Invalid competitor data');
        }

        // Decrypt encrypted data if present
        const decryptedCompetitor = {
            ...competitor,
            name: competitor.name.startsWith('encrypted_') 
                ? cryptoUtils.decrypt(competitor.name) 
                : competitor.name
        };

        this.matrix[competitor.id] = decryptedCompetitor;
        logger.info(`Added competitor: ${decryptedCompetitor.name}`);
        auditLogger.audit({
            action: 'ADD_COMPETITOR',
            competitorId: competitor.id,
            timestamp: new Date()
        });

        return decryptedCompetitor;
    }

    analyzeAdvantage(competitorId) {
        const competitor = this.matrix[competitorId];
        if (!competitor) {
            throw new Error('Competitor not found');
        }

        auditLogger.audit({
            action: 'ANALYZE_ADVANTAGE',
            competitorId,
            timestamp: new Date()
        });

        // Calculate advantage score based on strengths and weaknesses
        const strengths = competitor.strengths || [];
        const weaknesses = competitor.weaknesses || [];
        
        if (strengths.length === 0 && weaknesses.length === 0) {
            return 50; // Neutral score
        }

        const strengthScore = strengths.length * 10;
        const weaknessPenalty = weaknesses.length * 5;
        let score = 50 + strengthScore - weaknessPenalty;

        // Ensure score is between 0 and 100
        score = Math.max(0, Math.min(100, score));

        logger.debug(`Advantage score for ${competitorId}: ${score}`);
        return score;
    }

    generateReport() {
        const competitors = Object.values(this.matrix);
        
        // Calculate overall market position
        const totalScore = competitors.reduce((sum, comp) => {
            try {
                return sum + this.analyzeAdvantage(comp.id);
            } catch {
                return sum;
            }
        }, 0);
        
        const averageScore = competitors.length > 0 ? totalScore / competitors.length : 0;

        const report = {
            timestamp: new Date().toISOString(),
            competitors: competitors.map(comp => ({
                id: comp.id,
                name: comp.name,
                score: this.analyzeAdvantage(comp.id),
                strengths: comp.strengths || [],
                weaknesses: comp.weaknesses || []
            })),
            analysis: {
                totalCompetitors: competitors.length,
                averageAdvantageScore: averageScore,
                marketPosition: this.getMarketPosition(averageScore),
                recommendations: this.generateRecommendations(competitors)
            },
            recommendations: this.generateRecommendations(competitors)
        };

        auditLogger.audit({
            action: 'GENERATE_REPORT',
            reportId: `report_${Date.now()}`,
            timestamp: new Date()
        });

        return report;
    }

    getMarketPosition(score) {
        if (score >= 70) return 'LEADER';
        if (score >= 40) return 'CHALLENGER';
        if (score >= 20) return 'FOLLOWER';
        return 'NICHE';
    }

    generateRecommendations(competitors) {
        const recommendations = [];
        
        competitors.forEach(comp => {
            const score = this.analyzeAdvantage(comp.id);
            
            if (score < 30) {
                recommendations.push({
                    competitor: comp.name,
                    action: 'EXPLOIT_WEAKNESS',
                    details: `Target ${comp.name}'s weaknesses: ${(comp.weaknesses || []).join(', ')}`
                });
            } else if (score > 70) {
                recommendations.push({
                    competitor: comp.name,
                    action: 'MONITOR_CLOSELY',
                    details: `${comp.name} is a strong competitor with strengths: ${(comp.strengths || []).join(', ')}`
                });
            }
        });

        return recommendations;
    }

    clearMatrix() {
        this.matrix = {};
        logger.info('Competitive advantage matrix cleared');
    }
}

module.exports = CompetitiveAdvantageMatrix;
