import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux'; // Access User Data
import styled from 'styled-components';
import { apiGet } from '../../../services/apiService';
import { toast } from 'react-toastify';

// 🔌 IMPORT THE PROFESSIONAL GENERATOR
import { generateOfficialPDF } from '../../../services/pdfGenerator';

import {
    FaFileInvoiceDollar, FaMapMarkerAlt, FaUserTie, FaCheckCircle,
    FaPrint, FaPen, FaArrowLeft, FaFilePdf, FaInfoCircle,
    FaBuilding, FaPhone, FaEnvelope, FaIdCard, FaGlobe, FaUniversity,
    FaBalanceScale
} from 'react-icons/fa';

// ==========================================
// 🎨 ENTERPRISE STYLES (Preserved & Polished)
// ==========================================
const PageLayout = styled.div`
  padding: 40px; background-color: #f4f7f6; min-height: 100vh;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
`;

const Header = styled.div`
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 30px; background: white; padding: 20px 30px;
  border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  @media(max-width: 768px) { flexDirection: column; align-items: flex-start; gap: 15px; }
`;

const BackButton = styled.button`
  background: none; border: none; color: #718096; cursor: pointer;
  display: flex; align-items: center; gap: 8px; font-weight: 600;
  margin-bottom: 20px; transition: color 0.2s;
  &:hover { color: #1a365d; }
`;

const TitleBlock = styled.div`
  h1 { font-size: 1.8rem; color: #1a365d; margin: 0; font-weight: 800; }
  .ref-badge { 
    font-family: 'Courier New', monospace; background: #e2e8f0; color: #4a5568; 
    padding: 2px 8px; border-radius: 4px; font-size: 0.9rem; margin-left: 10px;
  }
`;

const StatusBadge = styled.span`
  background: ${props => props.$status === 'Served' ? '#def7ec' : props.$status === 'Non-Service' ? '#fde8e8' : '#feecdc'};
  color: ${props => props.$status === 'Served' ? '#03543f' : props.$status === 'Non-Service' ? '#9b1c1c' : '#9c4221'};
  padding: 6px 16px; border-radius: 50px; font-weight: 700; font-size: 0.8rem;
  text-transform: uppercase; letter-spacing: 0.05em; display: inline-flex; align-items: center; gap: 6px;
`;

const Grid = styled.div`
  display: grid; grid-template-columns: 2fr 1fr; gap: 30px;
  @media(max-width: 1100px) { grid-template-columns: 1fr; }
`;

const Card = styled.div`
  background: white; border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
  border-top: 4px solid ${props => props.$accent || '#cbd5e0'};
  padding: 25px; margin-bottom: 25px; position: relative;
`;

const SectionTitle = styled.h3`
  font-size: 0.95rem; color: #718096; text-transform: uppercase; letter-spacing: 0.08em;
  border-bottom: 1px solid #edf2f7; padding-bottom: 15px; margin-bottom: 20px;
  display: flex; align-items: center; gap: 10px; font-weight: 700;
`;

const DataGrid = styled.div`
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  @media(max-width: 600px) { grid-template-columns: 1fr; }
`;

const Field = styled.div`
  margin-bottom: 5px;
  label { display: block; font-size: 0.75rem; color: #a0aec0; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
  div { font-size: 1rem; color: #2d3748; font-weight: 500; display: flex; align-items: center; gap: 8px; word-break: break-word; }
  .mono { font-family: 'Courier New', monospace; background: #f7fafc; padding: 2px 6px; border-radius: 4px; }
  a { color: #3182ce; text-decoration: none; &:hover { text-decoration: underline; }}
`;

const InvoiceBox = styled.div`
  background: #f0fff4; border: 1px solid #c6f6d5; border-radius: 8px; padding: 20px;
`;

const ActionButton = styled.button`
  background: ${props => props.$primary ? '#1a365d' : 'white'};
  color: ${props => props.$primary ? 'white' : '#4a5568'};
  border: 1px solid ${props => props.$primary ? '#1a365d' : '#cbd5e0'};
  padding: 10px 20px; border-radius: 8px; font-weight: 600; cursor: pointer;
  transition: all 0.2s; display: flex; align-items: center; gap: 8px;
  &:hover { transform: translateY(-1px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
`;

const ModalOverlay = styled.div`
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(26, 54, 93, 0.7); backdrop-filter: blur(4px);
  display: flex; justify-content: center; align-items: center; z-index: 1000;
`;

const ModalContent = styled.div`
  background: white; padding: 40px; border-radius: 16px; width: 450px;
  box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); text-align: center;
`;

// ==========================================
// 🧠 HELPERS
// ==========================================
const generateSmartRef = (doc) => {
    if (!doc) return 'REF-ERR';
    if (doc.caseNumber && doc.caseNumber.length > 3) return doc.caseNumber;
    const datePart = new Date(doc.createdAt).getFullYear();
    const idPart = (doc._id || '000000').substring((doc._id || '000000').length - 6).toUpperCase();
    return `LDS-${datePart}-${idPart}`;
};

const formatZAR = (amount) => new Intl.NumberFormat('en-ZA', { style: 'currency', currency: 'ZAR' }).format(amount || 0);

// ==========================================
// 🚀 MAIN COMPONENT
// ==========================================
const DocumentDetails = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useSelector(state => state.auth); // Get current logged-in user
    const [doc, setDoc] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showReturnModal, setShowReturnModal] = useState(false);

    useEffect(() => {
        const fetchCaseFile = async () => {
            try {
                const response = await apiGet(`/documents/${id}`);
                let data = response.data || response;
                setDoc(data);
            } catch (err) {
                console.error("Failed to load case:", err);
                toast.error("Could not load case file.");
                navigate('/dashboard');
            } finally {
                setLoading(false);
            }
        };
        fetchCaseFile();
    }, [id, navigate]);

    // --- 🖨️ NEW PROFESSIONAL PDF ENGINE ---
    const handleGeneratePDF = () => {
        // We pass the document AND the user info to the generator
        generateOfficialPDF(doc, user);
        toast.success("Official PDF Downloaded");
        setShowReturnModal(false);
    };

    // --- PARTY RENDERER ---
    const PartyRenderer = ({ label, data, role }) => {
        const isObject = typeof data === 'object' && data !== null;
        const name = isObject ? data.name : (data || 'N/A');
        const idNum = isObject ? (data.idNumber || data.regNumber || 'N/A') : '';
        const contact = isObject ? (data.phone || data.email || '') : '';
        const icon = role === 'plaintiff' ? <FaUserTie className="text-blue-500" /> : <FaUserTie className="text-red-500" />;

        return (
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                <h4 className="text-xs font-bold text-gray-500 uppercase mb-3 flex items-center gap-2">
                    {icon} {label}
                </h4>
                <div className="text-lg font-bold text-gray-800 mb-1">{name}</div>
                {(idNum || contact) && (
                    <div className="flex flex-col gap-1 mt-2">
                        {idNum && <div className="text-sm text-gray-600 flex items-center gap-2"><FaIdCard size={12} /> <span className="font-mono">{idNum}</span></div>}
                        {contact && <div className="text-sm text-gray-600 flex items-center gap-2"><FaPhone size={12} /> {contact}</div>}
                    </div>
                )}
            </div>
        );
    };

    if (loading) return <div className="flex h-screen justify-center items-center text-gray-500">Loading Secure File...</div>;
    if (!doc) return <div>Document Not Found</div>;

    const lit = doc.litigationDetails || {};
    const agree = doc.agreementDetails || {};
    const smartRef = generateSmartRef(doc);
    const address = (!doc.serviceAddress || doc.serviceAddress === 'N/A') ? (lit.serviceAddress || 'No Address Provided') : doc.serviceAddress;

    // Safety for strings
    const safeType = (doc.subType || doc.type || '').toLowerCase();
    const safeCategory = (doc.category || '').toLowerCase();

    // --- SPECIFICS RENDERER ---
    const renderSpecifics = () => {
        if (safeType.includes('divorce') || safeType.includes('family')) {
            return (
                <Card $accent="#805ad5">
                    <SectionTitle><FaInfoCircle /> Matrimonial Particulars</SectionTitle>
                    <DataGrid>
                        <Field><label>Regime / Status</label><div>{lit.reliefSought || 'N/A'}</div></Field>
                        <Field><label>Minors / Dependents</label><div>{lit.additionalInfo || 'N/A'}</div></Field>
                    </DataGrid>
                </Card>
            );
        }
        if (safeType.includes('contract') || safeType.includes('agreement')) {
            return (
                <Card $accent="#3182ce">
                    <SectionTitle><FaBuilding /> Contract Specifics</SectionTitle>
                    <DataGrid>
                        <Field><label>Value</label><div>{formatZAR(agree.value)}</div></Field>
                        <Field><label>Effective Date</label><div>{agree.effectiveDate || 'N/A'}</div></Field>
                    </DataGrid>
                </Card>
            );
        }
        return null;
    };

    return (
        <PageLayout>
            <BackButton onClick={() => navigate('/dashboard')}>
                <FaArrowLeft /> Dashboard
            </BackButton>

            <Header>
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div className="p-3 bg-blue-50 rounded-lg text-blue-700"><FaUniversity size={24} /></div>
                    <TitleBlock>
                        <h1>{doc.subType || doc.category || 'Untitled Document'}</h1>
                        <p>Ref: <span className="ref-badge">{smartRef}</span></p>
                    </TitleBlock>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <ActionButton onClick={() => navigate(`/documents/${id}/edit`)}>
                        <FaPen /> Edit Details
                    </ActionButton>
                    <ActionButton $primary onClick={() => setShowReturnModal(true)}>
                        <FaPrint /> Generate Return
                    </ActionButton>
                </div>
            </Header>

            <Grid>
                {/* LEFT COLUMN */}
                <div>
                    {renderSpecifics()}
                    <Card $accent="#2d3748">
                        <SectionTitle><FaUserTie /> Parties Involved</SectionTitle>
                        <DataGrid>
                            <PartyRenderer label="Plaintiff / Applicant" data={lit.plaintiff || agree.partyA} role="plaintiff" />
                            <PartyRenderer label="Defendant / Respondent" data={lit.defendant || agree.partyB} role="defendant" />
                        </DataGrid>
                    </Card>
                    <Card $accent="#e53e3e">
                        <SectionTitle><FaMapMarkerAlt /> Service Location</SectionTitle>
                        <h4 className="text-lg font-bold text-gray-800 mb-1">{address}</h4>
                        <div className="text-right mt-2">
                            <span style={{ color: doc.urgency === 'Urgent' ? '#e53e3e' : '#2d3748', fontWeight: 'bold' }}>
                                {doc.urgency === 'Urgent' ? '⚡ URGENT SERVICE' : 'Standard Service'}
                            </span>
                        </div>
                    </Card>
                </div>

                {/* RIGHT COLUMN */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
                    <Card $accent="#38a169">
                        <SectionTitle><FaCheckCircle /> Status & Control</SectionTitle>
                        <div className="flex justify-between items-center mb-6">
                            <StatusBadge $status={doc.status}>{doc.status || 'Pending'}</StatusBadge>
                        </div>
                        <Field><label>Attorney</label><div>{doc.createdBy?.name || 'Internal'}</div></Field>
                    </Card>

                    <Card $accent="#2b6cb0">
                        <SectionTitle><FaFileInvoiceDollar /> Pro Forma Invoice</SectionTitle>
                        <InvoiceBox>
                            <div className="flex justify-between text-xl font-extrabold text-green-900">
                                <span>TOTAL</span>
                                <span>{formatZAR(doc.estimatedFee)}</span>
                            </div>
                        </InvoiceBox>
                    </Card>
                </div>
            </Grid>

            {/* MODAL */}
            {showReturnModal && (
                <ModalOverlay onClick={() => setShowReturnModal(false)}>
                    <ModalContent onClick={e => e.stopPropagation()}>
                        <FaFilePdf size={48} color="#e53e3e" className="mx-auto mb-4" />
                        <h2 className="text-xl font-bold text-gray-800 mb-2">Official Return</h2>
                        <p className="text-gray-500 mb-6 text-sm">Generate certified PDF for <strong>{smartRef}</strong>?</p>
                        <div className="flex justify-center gap-3">
                            <ActionButton onClick={() => setShowReturnModal(false)}>Cancel</ActionButton>
                            <ActionButton $primary onClick={handleGeneratePDF}>Download PDF</ActionButton>
                        </div>
                    </ModalContent>
                </ModalOverlay>
            )}
        </PageLayout>
    );
};

export default DocumentDetails;