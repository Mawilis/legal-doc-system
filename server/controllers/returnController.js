const fs = require('fs');
const path = require('path');
const PDFDocument = require('pdfkit');
const Attempt = require('../models/Attempt');
const DispatchInstruction = require('../models/DispatchInstruction');

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function renderHeader(doc, title) {
  doc.fontSize(18).text(title, { align: 'center' });
  doc.moveDown();
  doc.fontSize(10).text(`Generated at: ${new Date().toISOString()}`);
  doc.moveDown();
}

function renderInstructionSummary(doc, instruction) {
  doc.fontSize(12).text('Instruction Summary', { underline: true });
  doc.fontSize(10).text(`Title: ${instruction.title}`);
  doc.text(`Document Code: ${instruction.documentCode}`);
  doc.text(`Case Number: ${instruction.caseNumber}`);
  doc.text(`Court: ${instruction.court}`);
  doc.text(`Service Type: ${instruction.serviceType}`);
  doc.moveDown();
}

function renderAttempts(doc, attempts) {
  doc.fontSize(12).text('Attempts Log', { underline: true });
  attempts.forEach((a, idx) => {
    doc.fontSize(10).text(`Attempt #${idx + 1}`);
    doc.text(`  At: ${new Date(a.at).toISOString()}`);
    doc.text(`  Outcome: ${a.outcome}`);
    doc.text(`  GPS: ${a.gps.lat}, ${a.gps.lng} (${a.gps.accuracy || 0}m)`);
    doc.text(`  Notes: ${a.notes || '-'}`);
    doc.text(`  Hash: ${a.hash}`);
    doc.moveDown();
  });
}

async function generatePdf(filePath, build) {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({ size: 'A4', margin: 50 });
    const stream = fs.createWriteStream(filePath);
    doc.pipe(stream);
    build(doc);
    doc.end();
    stream.on('finish', resolve);
    stream.on('error', reject);
  });
}

exports.generateReturns = async (req, res) => {
  try {
    const { id } = req.params;
    const instruction = await DispatchInstruction.findById(id);
    if (!instruction) return res.status(404).json({ message: 'Instruction not found' });

    const attempts = await Attempt.find({ instructionId: id }).sort({ at: 1 });
    if (!attempts.length) return res.status(400).json({ message: 'No attempts logged yet' });

    const filesDir = path.join(__dirname, '../files/returns', String(id));
    ensureDir(filesDir);

    // Return of Service PDF
    const returnFilename = `return-of-service-${Date.now()}.pdf`;
    const returnPath = path.join(filesDir, returnFilename);
    
    await generatePdf(returnPath, (doc) => {
      renderHeader(doc, 'Return of Service');
      renderInstructionSummary(doc, instruction);
      renderAttempts(doc, attempts);
      doc.fontSize(10).text('This document includes hashed attempt entries for integrity.', { align: 'left' });
    });

    const publicUrl = `/files/returns/${id}/${returnFilename}`;
    instruction.returnOfServicePdfUrl = publicUrl;
    
    if (instruction.status === 'completed' || instruction.status === 'in_progress') {
        instruction.status = 'returned';
    }
    
    await instruction.save();

    return res.status(200).json({
      returnOfServicePdfUrl: publicUrl,
      status: instruction.status,
    });
  } catch (err) {
    return res.status(400).json({ message: err.message });
  }
};
