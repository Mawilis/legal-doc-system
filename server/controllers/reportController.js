const PDFDocument = require('pdfkit');
const { createObjectCsvWriter } = require('csv-writer');
const Document = require('../models/documentModel');
const CustomError = require('../utils/customError');
const logger = require('../utils/logger');

/**
 * @desc    Generate a PDF report of documents within a date range
 * @route   GET /api/reports/documents/pdf?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
 * @access  Private/Admin
 */
exports.generateDocumentReportPDF = async (req, res, next) => {
    try {
        const { startDate, endDate } = req.query;

        if (!startDate || !endDate) {
            return next(new CustomError('Please provide both startDate and endDate in YYYY-MM-DD format.', 400));
        }

        const start = new Date(startDate);
        const end = new Date(new Date(endDate).setHours(23, 59, 59, 999));

        if (isNaN(start) || isNaN(end)) {
            return next(new CustomError('Invalid date format. Please use YYYY-MM-DD.', 400));
        }

        const documents = await Document.find({
            createdAt: { $gte: start, $lte: end }
        })
            .populate('createdBy', 'name')
            .populate('assignedTo', 'name')
            .lean();

        if (!documents.length) {
            return next(new CustomError('No documents found in the specified date range.', 404));
        }

        // --- PDF generation ---
        const doc = new PDFDocument({ margin: 40, size: 'A4' });

        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `attachment; filename="document_report_${Date.now()}.pdf"`);

        doc.pipe(res);

        // --- PDF Content ---
        doc.fontSize(18).text('Legal Document System', { align: 'center' });
        doc.fontSize(14).text('Document Activity Report', { align: 'center' });
        doc.moveDown(0.5);
        doc.fontSize(10).text(`From: ${startDate}  To: ${endDate}`, { align: 'center' });
        doc.moveDown(1);

        // Draw table header
        const headers = [
            { label: 'Title', width: 130 },
            { label: 'Case #', width: 80 },
            { label: 'Status', width: 60 },
            { label: 'Created By', width: 80 },
            { label: 'Assigned To', width: 80 }
        ];

        let y = doc.y;
        headers.forEach((header, i) => {
            doc.font('Helvetica-Bold').fontSize(10).text(header.label, 40 + headers.slice(0, i).reduce((acc, cur) => acc + cur.width, 0), y, {
                width: header.width,
                align: 'left'
            });
        });

        doc.moveDown(0.5);
        doc.strokeColor('#000').moveTo(40, doc.y).lineTo(550, doc.y).stroke();

        // Rows
        documents.forEach(docData => {
            y = doc.y;
            const values = [
                docData.title || 'N/A',
                docData.caseNumber || 'N/A',
                docData.status || 'N/A',
                docData.createdBy?.name || 'N/A',
                docData.assignedTo?.name || 'Unassigned'
            ];

            values.forEach((val, i) => {
                doc.font('Helvetica').fontSize(9).text(val, 40 + headers.slice(0, i).reduce((acc, cur) => acc + cur.width, 0), y, {
                    width: headers[i].width,
                    align: 'left'
                });
            });

            doc.moveDown(0.5);
        });

        doc.end();

        logger.info(`PDF report generated: documents from ${startDate} to ${endDate}`);

    } catch (error) {
        logger.error(`Error generating PDF report: ${error.message}`);
        next(new CustomError('Failed to generate PDF report.', 500));
    }
};
