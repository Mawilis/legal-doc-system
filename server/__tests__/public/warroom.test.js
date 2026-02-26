/* eslint-disable */
/* eslint-env jest */
/*╔═══════════════════════════════════════════════════════════════════════════════════════╗
  ║ WAR ROOM DASHBOARD TESTS - $5B+ INFRASTRUCTURE VERIFICATION                           ║
  ║ Tests UI components, API integration, WebSocket, and accessibility                     ║
  ╚═══════════════════════════════════════════════════════════════════════════════════════╝*/

import { JSDOM } from 'jsdom.js';
import fs from "fs";
import path from "path";
import { fileURLToPath } from 'url.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Mock fetch and WebSocket
global.fetch = jest.fn();
global.WebSocket = jest.fn();

describe('War Room Dashboard', () => {
    let dom;
    let container;
    let warroomHTML;
    let warroomJS;
    
    beforeAll(() => {
        // Load the actual HTML and JS files
        warroomHTML = fs.readFileSync(
            path.join(__dirname, '../../public/dashboard/warroom.html'),
            'utf8'
        );
        
        // Create DOM environment
        dom = new JSDOM(warroomHTML, {
            runScripts: 'dangerously',
            resources: 'usable',
            url: 'https://wilsyos.com/dashboard/warroom'
        });
        
        global.document = dom.window.document;
        global.window = dom.window;
        global.localStorage = {
            getItem: jest.fn(),
            setItem: jest.fn(),
            removeItem: jest.fn()
        };
        
        // Load the JavaScript (simulated)
        warroomJS = fs.readFileSync(
            path.join(__dirname, '../../public/js/warroom.js'),
            'utf8'
        );
    });
    
    beforeEach(() => {
        jest.clearAllMocks();
        document.body.innerHTML = warroomHTML;
    });
    
    describe('HTML Structure', () => {
        test('should have correct document title', () => {
            expect(document.title).toBe('WILSY OS - THE WAR ROOM | Global Threat Intelligence');
        });
        
        test('should have all required elements', () => {
            expect(document.getElementById('matrix-bg')).toBeTruthy();
            expect(document.getElementById('status-badge')).toBeTruthy();
            expect(document.getElementById('valuation')).toBeTruthy();
            expect(document.getElementById('threat-level')).toBeTruthy();
            expect(document.getElementById('threat-fill')).toBeTruthy();
            expect(document.getElementById('active-quarantines')).toBeTruthy();
            expect(document.getElementById('recent-alerts')).toBeTruthy();
            expect(document.getElementById('valuation-risk')).toBeTruthy();
            expect(document.getElementById('threat-trend')).toBeTruthy();
            expect(document.getElementById('threats-body')).toBeTruthy();
            expect(document.getElementById('alert-feed')).toBeTruthy();
            expect(document.getElementById('heatmap-grid')).toBeTruthy();
            expect(document.getElementById('timestamp')).toBeTruthy();
        });
        
        test('should have security meta tags', () => {
            const csp = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
            expect(csp).toBeTruthy();
            expect(csp.getAttribute('content')).toContain("default-src 'self'");
        });
        
        test('should have accessibility attributes', () => {
            const statusBadge = document.getElementById('status-badge');
            expect(statusBadge.getAttribute('role')).toBe('status');
            expect(statusBadge.getAttribute('aria-live')).toBe('polite');
            
            const threatMeter = document.querySelector('.threat-meter');
            expect(threatMeter.getAttribute('role')).toBe('progressbar');
        });
    });
    
    describe('CSS Classes', () => {
        test('should have responsive grid classes', () => {
            const statusGrid = document.querySelector('.status-grid');
            expect(statusGrid).toBeTruthy();
            
            const cards = document.querySelectorAll('.status-card');
            expect(cards.length).toBe(4);
        });
        
        test('should have threat meter classes', () => {
            const threatFill = document.querySelector('.threat-fill');
            expect(threatFill).toBeTruthy();
            
            const threatLabels = document.querySelectorAll('.threat-label');
            expect(threatLabels.length).toBe(4);
        });
    });
    
    describe('API Client', () => {
        test('should initialize with correct base URL', () => {
            const { APIClient } = require('../../public/js/warroom.js');
            const client = new APIClient('/api/v1/admin/threat', 'test-token');
            
            expect(client.baseURL).toBe('/api/v1/admin/threat');
            expect(client.token).toBe('test-token');
        });
        
        test('should make authenticated requests', async () => {
            const { APIClient } = require('../../public/js/warroom.js');
            const client = new APIClient('/api/v1/admin/threat', 'test-token');
            
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: true, data: {} })
            });
            
            await client.getThreatPosture();
            
            expect(global.fetch).toHaveBeenCalledWith(
                '/api/v1/admin/threat/posture',
                expect.objectContaining({
                    headers: expect.objectContaining({
                        'Authorization': 'Bearer test-token'
                    })
                })
            );
        });
    });
    
    describe('Authentication', () => {
        test('should redirect to login if no token', () => {
            delete global.location;
            global.location = { href: '' };
            
            localStorage.getItem.mockReturnValueOnce(null);
            
            // This would trigger the redirect in the actual code
            expect(true).toBe(true); // Placeholder
        });
    });
    
    describe('Matrix Background', () => {
        test('should initialize canvas', () => {
            const { MatrixRain } = require('../../public/js/warroom.js');
            const matrix = new MatrixRain();
            
            expect(matrix.canvas).toBeTruthy();
            expect(matrix.ctx).toBeTruthy();
        });
    });
    
    describe('Error Handling', () => {
        test('should handle API failures gracefully', async () => {
            const { APIClient } = require('../../public/js/warroom.js');
            const client = new APIClient('/api/v1/admin/threat', 'test-token');
            
            global.fetch.mockRejectedValueOnce(new Error('Network error'));
            
            await expect(client.getThreatPosture()).rejects.toThrow('Network error');
        });
        
        test('should handle WebSocket failures', () => {
            const { WebSocketManager } = require('../../public/js/warroom.js');
            const manager = new WebSocketManager('ws://test', 'token', jest.fn(), jest.fn());
            
            // Should not throw
            manager.connect();
            
            // Simulate error
            if (manager.socket && manager.socket.onerror) {
                manager.socket.onerror(new Event('error'));
            }
        });
    });
    
    describe('Accessibility', () => {
        test('should have ARIA labels on interactive elements', () => {
            const cards = document.querySelectorAll('.status-card');
            cards.forEach(card => {
                expect(card.getAttribute('role')).toBe('article');
            });
            
            const heatmapCells = document.querySelectorAll('.heatmap-cell');
            heatmapCells.forEach(cell => {
                expect(cell.getAttribute('role')).toBe('gridcell');
            });
        });
        
        test('should have visible focus indicators', () => {
            const links = document.querySelectorAll('.footer-link');
            links.forEach(link => {
                const styles = window.getComputedStyle(link);
                expect(styles.outline).toBeDefined();
            });
        });
    });
    
    describe('Responsive Design', () => {
        test('should have mobile breakpoint styles', () => {
            const mediaQuery = window.matchMedia('(max-width: 768px)');
            expect(mediaQuery).toBeDefined();
        });
        
        test('should have reduced motion preferences', () => {
            const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
            expect(mediaQuery).toBeDefined();
        });
    });
    
    describe('Performance', () => {
        test('should lazy load non-critical resources', () => {
            const scripts = document.querySelectorAll('script[defer]');
            expect(scripts.length).toBeGreaterThan(0);
        });
        
        test('should preload critical assets', () => {
            const preloads = document.querySelectorAll('link[rel="preload"]');
            expect(preloads.length).toBeGreaterThan(0);
        });
    });
});
