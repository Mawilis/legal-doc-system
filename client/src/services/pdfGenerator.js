// ~/client/src/services/pdfGenerator.js
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable'; // 👈 1. Import as a function

// --- CONFIGURATION ---
const THEME = {
    NAVY: [26, 54, 93],    // #1a365d
    BLUE: [49, 130, 206],  // #3182ce
    GRAY: [113, 128, 150], // #718096
    LIGHT: [247, 250, 252] // #f7fafc
};

/**
 * Generates a Bank-Grade PDF Invoice & Return of Service
 */
export const generateOfficialPDF = (doc, user) => {
    const pdf = new jsPDF();
    const pageWidth = pdf.internal.pageSize.width;
    const pageHeight = pdf.internal.pageSize.height;
    const margin = 20;

    // ==========================================
    // 1. HEADER BRANDING (Navy Strip)
    // ==========================================
    pdf.setFillColor(...THEME.NAVY);
    pdf.rect(0, 0, pageWidth, 40, 'F');

    // Logo / Company Name
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(22);
    pdf.setFont('helvetica', 'bold');
    pdf.text("LegalDocSys", margin, 20);

    // Sub-header
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    pdf.text("OFFICIAL RETURN OF SERVICE", margin, 28);
    pdf.text(`Generated: ${new Date().toLocaleDateString()}`, margin, 34);

    // ==========================================
    // 2. WATERMARK (Background)
    // ==========================================
    pdf.setTextColor(240, 240, 240);
    pdf.setFontSize(60);
    pdf.text("ORIGINAL", pageWidth / 2, 150, { align: 'center', angle: 45 });

    // ==========================================
    // 3. DOCUMENT META (Right Aligned)
    // ==========================================
    pdf.setTextColor(0, 0, 0);
    const topY = 55;

    pdf.setFontSize(11);
    pdf.setFont('helvetica', 'bold');
    pdf.text(`REF: ${doc.caseNumber || 'PENDING'}`, pageWidth - margin, topY, { align: 'right' });

    pdf.setFont('helvetica', 'normal');
    pdf.setFontSize(10);
    pdf.setTextColor(...THEME.GRAY);
    pdf.text(`Date Lodged: ${new Date(doc.createdAt).toLocaleDateString()}`, pageWidth - margin, topY + 6, { align: 'right' });
    pdf.text(`Clerk/Sheriff: ${user?.name || 'System Admin'}`, pageWidth - margin, topY + 12, { align: 'right' });

    // ==========================================
    // 4. CASE PARTICULARS (Left Side)
    // ==========================================
    let yPos = topY;
    const lit = doc.litigationDetails || {};
    const agree = doc.agreementDetails || {};

    const drawField = (label, value) => {
        pdf.setFontSize(9);
        pdf.setTextColor(...THEME.GRAY);
        pdf.text(label.toUpperCase(), margin, yPos);

        pdf.setFontSize(11);
        pdf.setTextColor(0, 0, 0);
        pdf.text(value || 'N/A', margin, yPos + 5);

        yPos += 14;
    };

    drawField("Document Type", doc.subType || doc.category);
    drawField("Court / Forum", lit.courtName || "High Court");
    drawField("Plaintiff / Applicant", lit.plaintiff || agree.partyA);
    drawField("Defendant / Respondent", lit.defendant || agree.partyB);
    drawField("Service Address", doc.serviceAddress);

    // ==========================================
    // 5. THE FINANCIAL TABLE (Fixed AutoTable)
    // ==========================================
    const baseFee = doc.estimatedFee || 450.00;
    const travelFee = 65.00;
    const vat = (baseFee + travelFee) * 0.15;
    const total = baseFee + travelFee + vat;

    // 👈 2. FIX: Call autoTable(pdf, options) explicitly
    autoTable(pdf, {
        startY: yPos + 10,
        head: [['Description', 'Reference', 'Amount (ZAR)']],
        body: [
            ['Service of Process (Rule 41)', doc.caseNumber || 'N/A', baseFee.toFixed(2)],
            ['Travel Allowance (Zone 1)', 'Standard', travelFee.toFixed(2)],
            ['VAT (15%)', 'Tax', vat.toFixed(2)],
            [{ content: 'TOTAL DUE', styles: { fontStyle: 'bold', fillColor: [240, 240, 240] } }, '', { content: total.toFixed(2), styles: { fontStyle: 'bold' } }]
        ],
        theme: 'grid', // 'grid' looks more like a bank statement
        headStyles: { fillColor: THEME.NAVY, textColor: 255 },
        styles: { fontSize: 10, cellPadding: 5 },
        columnStyles: { 2: { halign: 'right' } }
    });

    // ==========================================
    // 6. CERTIFICATION & FOOTER
    // ==========================================
    // We use pdf.lastAutoTable.finalY because the function attaches this property to the doc
    const finalY = pdf.lastAutoTable.finalY + 20;

    // Certification Box
    pdf.setFillColor(245, 245, 245);
    pdf.rect(margin, finalY, pageWidth - (margin * 2), 35, 'F');

    pdf.setFontSize(10);
    pdf.setTextColor(...THEME.NAVY);
    pdf.setFont('helvetica', 'bold');
    pdf.text("SHERIFF'S CERTIFICATION", margin + 5, finalY + 10);

    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(0, 0, 0);
    const certText = `I, the undersigned Sheriff, certify that on ${new Date().toLocaleDateString()} at the address mentioned above, I successfully served this process in accordance with the Rules of Court.`;
    const splitCert = pdf.splitTextToSize(certText, pageWidth - (margin * 2) - 10);
    pdf.text(splitCert, margin + 5, finalY + 20);

    // Footer Details (Banking)
    const footerY = pageHeight - 40;
    pdf.setDrawColor(200, 200, 200);
    pdf.line(margin, footerY, pageWidth - margin, footerY);

    pdf.setFontSize(8);
    pdf.setTextColor(...THEME.GRAY);

    // Bank Details Left
    pdf.text("BANKING DETAILS:", margin, footerY + 8);
    pdf.text("LegalDocSys Trust Account | FNB | Acc: 123456789 | Branch: 250655", margin, footerY + 13);
    pdf.text(`Payment Ref: ${doc.caseNumber || 'LDS-REF'}`, margin, footerY + 18);

    // Signature Right
    pdf.text("LegalDocSys | Authorized Financial Service Provider", pageWidth - margin, footerY + 8, { align: 'right' });
    pdf.text("Page 1 of 1", pageWidth - margin, footerY + 13, { align: 'right' });

    // ==========================================
    // 7. SAVE FILE
    // ==========================================
    pdf.save(`Return_${doc.caseNumber || 'Draft'}.pdf`);
};