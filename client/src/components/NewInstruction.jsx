import React, { useState } from 'react';
import { apiPost } from '../services/apiService';
import { FaGavel, FaUserTie, FaUserShield, FaFileInvoiceDollar, FaBuilding } from 'react-icons/fa';

const NewInstruction = ({ onSuccess }) => {
    // 1. INITIAL STATE (Matches the Enterprise Schema)
    const [formData, setFormData] = useState({
        courtName: 'Magistrate Court',
        courtDivision: '',
        caseNumber: '',
        type: 'Summons', // Default

        // Nested Party Objects
        plaintiff: {
            name: '',
            idNumber: '',
            physicalAddress: '',
            email: '',
            contactNumber: ''
        },
        defendant: {
            name: '',
            idNumber: '',
            physicalAddress: '', // This acts as the Service Address
            email: '',
            contactNumber: ''
        },

        // Dynamic Legal Details
        legalDetails: {
            causeOfAction: '',
            amountClaimed: '',
            interestRate: '10.5',
            paymentDeadline: '',
            marriageRegime: '',
            childrenDetails: '',
            propertyDescription: '',
            judgmentAmount: ''
        },

        urgency: 'Normal',
        estimatedFee: 0 // Calculated automatically later
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // 2. DOCUMENT TYPES LIST
    const documentTypes = [
        'Summons', 'Combined Summons', 'Divorce Summons',
        'Warrant of Execution', 'Warrant of Ejectment',
        'Garnishee Order', 'Section 65 Proceedings',
        'Interdict', 'Letter of Demand', 'Subpoena'
    ];

    // 3. HANDLERS
    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handlePartyChange = (party, field, value) => {
        setFormData({
            ...formData,
            [party]: {
                ...formData[party],
                [field]: value
            }
        });
    };

    const handleLegalChange = (e) => {
        setFormData({
            ...formData,
            legalDetails: {
                ...formData.legalDetails,
                [e.target.name]: e.target.value
            }
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            console.log("🚀 Sending Enterprise Instruction:", formData);
            await apiPost('/documents', formData);
            alert('✅ Instruction Registered Successfully!');
            if (onSuccess) onSuccess();

            // Optional: Reset form here
        } catch (err) {
            console.error("Submission Error:", err);
            setError(err.response?.data?.message || 'Failed to register case.');
        } finally {
            setLoading(false);
        }
    };

    // 4. DYNAMIC FORM SECTIONS
    const renderDynamicFields = () => {
        switch (formData.type) {
            case 'Summons':
            case 'Combined Summons':
            case 'Letter of Demand':
                return (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-blue-50 p-4 rounded-lg border border-blue-100">
                        <div className="col-span-2">
                            <label className="text-xs font-bold text-gray-500 uppercase">Cause of Action</label>
                            <input name="causeOfAction" onChange={handleLegalChange} placeholder="e.g. Breach of Contract / Goods Sold" className="w-full p-2 border rounded" />
                        </div>
                        <div>
                            <label className="text-xs font-bold text-gray-500 uppercase">Amount Claimed (R)</label>
                            <input type="number" name="amountClaimed" onChange={handleLegalChange} placeholder="0.00" className="w-full p-2 border rounded" />
                        </div>
                    </div>
                );

            case 'Divorce Summons':
                return (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-pink-50 p-4 rounded-lg border border-pink-100">
                        <div>
                            <label className="text-xs font-bold text-gray-500 uppercase">Marriage Regime</label>
                            <select name="marriageRegime" onChange={handleLegalChange} className="w-full p-2 border rounded">
                                <option value="">Select Regime...</option>
                                <option value="In Community">In Community of Property</option>
                                <option value="Out of Community (ANC)">Out of Community (ANC)</option>
                                <option value="Accrual">With Accrual</option>
                            </select>
                        </div>
                        <div>
                            <label className="text-xs font-bold text-gray-500 uppercase">Minor Children Details</label>
                            <input name="childrenDetails" onChange={handleLegalChange} placeholder="e.g. 2 Children (Aged 5 & 8)" className="w-full p-2 border rounded" />
                        </div>
                    </div>
                );

            case 'Warrant of Execution':
            case 'Garnishee Order':
                return (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-red-50 p-4 rounded-lg border border-red-100">
                        <div>
                            <label className="text-xs font-bold text-gray-500 uppercase">Judgment Amount (R)</label>
                            <input type="number" name="judgmentAmount" onChange={handleLegalChange} placeholder="Total Judgment Debt" className="w-full p-2 border rounded" />
                        </div>
                        <div>
                            <label className="text-xs font-bold text-gray-500 uppercase">Target Property / Salary</label>
                            <input name="propertyDescription" onChange={handleLegalChange} placeholder="Vehicle details or Employer Name" className="w-full p-2 border rounded" />
                        </div>
                    </div>
                );

            default:
                return null;
        }
    };

    return (
        <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200 max-w-5xl mx-auto">

            {/* HEADER */}
            <div className="flex items-center space-x-3 mb-8 pb-4 border-b border-gray-100">
                <div className="bg-blue-600 p-3 rounded-lg text-white">
                    <FaGavel size={24} />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">New Legal Instruction</h2>
                    <p className="text-sm text-gray-500">Register a new case file for service</p>
                </div>
            </div>

            {error && <div className="mb-6 p-4 bg-red-50 text-red-700 border-l-4 border-red-500 rounded">{error}</div>}

            <form onSubmit={handleSubmit} className="space-y-8">

                {/* SECTION 1: COURT & CASE INFO */}
                <section>
                    <h3 className="text-sm font-bold text-gray-400 uppercase mb-4 flex items-center gap-2">
                        <FaBuilding /> Court Details
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="md:col-span-2">
                            <label className="block text-xs font-bold text-gray-600 mb-1">Court Name</label>
                            <input name="courtName" value={formData.courtName} onChange={handleChange} className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-600 mb-1">Division</label>
                            <input name="courtDivision" placeholder="e.g. JHB Central" onChange={handleChange} className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-xs font-bold text-gray-600 mb-1">Case Number</label>
                            <input name="caseNumber" placeholder="1234/2025" onChange={handleChange} required className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 font-mono" />
                        </div>
                    </div>
                </section>

                {/* SECTION 2: DOCUMENT TYPE & SPECIFICS */}
                <section>
                    <h3 className="text-sm font-bold text-gray-400 uppercase mb-4 flex items-center gap-2">
                        <FaFileInvoiceDollar /> Instrument Type
                    </h3>
                    <div className="mb-4">
                        <select name="type" value={formData.type} onChange={handleChange} className="w-full p-3 border-2 border-blue-100 rounded-lg text-lg font-semibold text-gray-700 focus:border-blue-500">
                            {documentTypes.map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                    </div>
                    {/* Dynamic Fields Render Here */}
                    {renderDynamicFields()}
                </section>

                {/* SECTION 3: THE PARTIES */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

                    {/* PLAINTIFF */}
                    <section className="bg-gray-50 p-5 rounded-lg border border-gray-200">
                        <h3 className="text-sm font-bold text-blue-600 uppercase mb-4 flex items-center gap-2">
                            <FaUserTie /> Plaintiff / Applicant
                        </h3>
                        <div className="space-y-3">
                            <input placeholder="Full Name / Company" onChange={(e) => handlePartyChange('plaintiff', 'name', e.target.value)} className="w-full p-2 border rounded" required />
                            <input placeholder="ID / Reg Number" onChange={(e) => handlePartyChange('plaintiff', 'idNumber', e.target.value)} className="w-full p-2 border rounded" />
                            <input placeholder="Phone / Email" onChange={(e) => handlePartyChange('plaintiff', 'contactNumber', e.target.value)} className="w-full p-2 border rounded" />
                        </div>
                    </section>

                    {/* DEFENDANT */}
                    <section className="bg-gray-50 p-5 rounded-lg border border-gray-200">
                        <h3 className="text-sm font-bold text-red-600 uppercase mb-4 flex items-center gap-2">
                            <FaUserShield /> Defendant / Respondent
                        </h3>
                        <div className="space-y-3">
                            <input placeholder="Full Name / Company" onChange={(e) => handlePartyChange('defendant', 'name', e.target.value)} className="w-full p-2 border rounded" required />
                            <textarea placeholder="SERVICE ADDRESS (Physical Location)" onChange={(e) => handlePartyChange('defendant', 'physicalAddress', e.target.value)} className="w-full p-2 border rounded h-24 font-medium" required />
                        </div>
                    </section>
                </div>

                {/* SUBMIT */}
                <div className="pt-6 border-t border-gray-100 flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                        <input type="checkbox" className="w-5 h-5 text-red-600" onChange={(e) => setFormData({ ...formData, urgency: e.target.checked ? 'Urgent' : 'Normal' })} />
                        <span className="font-bold text-gray-700">Mark as URGENT Service</span>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`px-8 py-3 rounded-lg font-bold text-white shadow-lg transition-all ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-xl transform hover:-translate-y-1'
                            }`}
                    >
                        {loading ? 'Registering...' : 'Submit Instruction'}
                    </button>
                </div>

            </form>
        </div>
    );
};

export default NewInstruction; 